"""
RAG Training Service for Proto
Uses ChromaDB (in-memory) for vector storage and the real pix2code public dataset from HuggingFace.
Dataset: N0zomu/pix2code-data (1748 samples)
"""

import chromadb
from chromadb.config import Settings
import logging
import json
from pathlib import Path
from dataset_generator import load_public_dataset, get_dataset_info

logger = logging.getLogger(__name__)

COLLECTION_NAME = "proto_ui_components"

class RAGService:
    def __init__(self):
        self.client = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
        self.collection = None
        self.is_trained = False
        self.training_stats = {"total_samples": 0, "categories": {}}
        self._dataset_cache = None
    
    def get_collection(self):
        if self.collection is None:
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
        return self.collection
    
    def train(self):
        """Train the RAG system by loading the real pix2code public dataset into ChromaDB."""
        logger.info("Starting RAG training with pix2code public dataset...")
        
        # Reset client for clean training
        self.client = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
        self.collection = None
        collection = self.get_collection()
        
        # Load real public dataset
        dataset = load_public_dataset()
        self._dataset_cache = {item["id"]: item for item in dataset}
        
        # Add to ChromaDB in batches - only store descriptions as documents
        # Code is stored separately in _dataset_cache (avoids metadata size limits)
        batch_size = 50
        for i in range(0, len(dataset), batch_size):
            batch = dataset[i:i+batch_size]
            ids = [item["id"] for item in batch]
            documents = [item["description"] for item in batch]
            metadatas = [{
                "category": item["category"],
                "framework": item["framework"],
                "source": item["source"],
                "split": item["split"]
            } for item in batch]
            
            collection.add(ids=ids, documents=documents, metadatas=metadatas)
            logger.info(f"Added batch {i//batch_size + 1}: {len(batch)} items (total: {collection.count()})")
        
        # Compute stats
        categories = {}
        splits = {"train": 0, "test": 0}
        for item in dataset:
            cat = item["category"]
            categories[cat] = categories.get(cat, 0) + 1
            splits[item["split"]] = splits.get(item["split"], 0) + 1
        
        self.training_stats = {
            "total_samples": len(dataset),
            "categories": categories,
            "splits": splits,
            "dataset": "pix2code (HuggingFace: N0zomu/pix2code-data)"
        }
        self.is_trained = True
        
        logger.info(f"Training complete! {len(dataset)} real pix2code samples loaded")
        return self.training_stats
    
    def query(self, description: str, n_results: int = 5, framework: str = None):
        """Query the RAG system for similar UI components."""
        collection = self.get_collection()
        
        if collection.count() == 0:
            return []
        
        try:
            results = collection.query(
                query_texts=[description],
                n_results=min(n_results, collection.count())
            )
        except Exception as e:
            logger.error(f"RAG query error: {e}")
            return []
        
        retrieved = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i] if results.get("distances") else None
                
                # Get full code from cache
                cached = self._dataset_cache.get(doc_id, {}) if self._dataset_cache else {}
                
                retrieved.append({
                    "id": doc_id,
                    "description": results["documents"][0][i],
                    "category": metadata.get("category", "unknown"),
                    "code": cached.get("code", ""),
                    "dsl": cached.get("dsl", ""),
                    "framework": metadata.get("framework", "unknown"),
                    "source": metadata.get("source", "unknown"),
                    "similarity": round(1 - (distance or 0), 3)
                })
        
        return retrieved
    
    def get_status(self):
        """Get current training status."""
        collection = self.get_collection()
        count = collection.count()
        
        return {
            "is_trained": count > 0,
            "total_entries": count,
            "stats": self.training_stats if self.is_trained else {},
            "storage_path": "in-memory (ChromaDB EphemeralClient)"
        }

# Singleton instance
rag_service = RAGService()
