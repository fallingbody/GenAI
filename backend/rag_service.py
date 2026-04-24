"""
RAG Training Service for Proto
Uses ChromaDB for vector storage and pix2code dataset for training.
"""

import chromadb
from chromadb.config import Settings
import logging
import os
from pathlib import Path
from dataset_generator import get_full_dataset

logger = logging.getLogger(__name__)

CHROMA_DIR = str(Path(__file__).parent / "chroma_db")
COLLECTION_NAME = "proto_ui_components"

class RAGService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.collection = None
        self.is_trained = False
        self.training_stats = {"total_samples": 0, "categories": {}, "frameworks": {}}
    
    def get_collection(self):
        """Get or create the ChromaDB collection."""
        if self.collection is None:
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
        return self.collection
    
    def train(self):
        """Train the RAG system by loading the pix2code + curated dataset into ChromaDB."""
        logger.info("Starting RAG training...")
        
        collection = self.get_collection()
        
        # Clear existing data for fresh training
        existing = collection.count()
        if existing > 0:
            all_ids = collection.get()["ids"]
            if all_ids:
                collection.delete(ids=all_ids)
            logger.info(f"Cleared {existing} existing entries")
        
        # Load dataset
        dataset = get_full_dataset()
        
        # Prepare batch data
        ids = []
        documents = []
        metadatas = []
        
        for item in dataset:
            ids.append(item["id"])
            
            # The document is the description - this is what gets embedded and searched
            documents.append(item["description"])
            
            # Metadata stores the actual code and other info
            metadatas.append({
                "category": item["category"],
                "code": item["code"][:4000],  # ChromaDB metadata limit
                "dsl": item.get("dsl", "")[:2000],
                "framework": item["framework"],
                "source": item["source"]
            })
        
        # Add to ChromaDB in batches
        batch_size = 20
        for i in range(0, len(ids), batch_size):
            batch_end = min(i + batch_size, len(ids))
            collection.add(
                ids=ids[i:batch_end],
                documents=documents[i:batch_end],
                metadatas=metadatas[i:batch_end]
            )
            logger.info(f"Added batch {i//batch_size + 1}: {batch_end - i} items")
        
        # Update stats
        categories = {}
        frameworks = {}
        for item in dataset:
            cat = item["category"]
            fw = item["framework"]
            categories[cat] = categories.get(cat, 0) + 1
            frameworks[fw] = frameworks.get(fw, 0) + 1
        
        self.training_stats = {
            "total_samples": len(dataset),
            "categories": categories,
            "frameworks": frameworks,
            "sources": {"pix2code": sum(1 for d in dataset if d["source"] == "pix2code"),
                        "curated": sum(1 for d in dataset if d["source"] == "curated")}
        }
        self.is_trained = True
        
        logger.info(f"Training complete! {len(dataset)} samples loaded into ChromaDB")
        return self.training_stats
    
    def query(self, description: str, n_results: int = 5, framework: str = None):
        """Query the RAG system for similar UI components."""
        collection = self.get_collection()
        
        if collection.count() == 0:
            return []
        
        # Build query with optional framework filter
        where_filter = None
        if framework and framework != "HTML/CSS/JS":
            where_filter = {"framework": framework}
        
        try:
            results = collection.query(
                query_texts=[description],
                n_results=min(n_results, collection.count()),
                where=where_filter if where_filter else None
            )
        except Exception:
            # If filter fails (no matching framework), query without filter
            results = collection.query(
                query_texts=[description],
                n_results=min(n_results, collection.count())
            )
        
        # Format results
        retrieved = []
        if results and results["ids"] and results["ids"][0]:
            for i, id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i] if results.get("distances") else None
                retrieved.append({
                    "id": id,
                    "description": results["documents"][0][i],
                    "category": metadata.get("category", "unknown"),
                    "code": metadata.get("code", ""),
                    "framework": metadata.get("framework", "unknown"),
                    "similarity": round(1 - (distance or 0), 3)
                })
        
        return retrieved
    
    def get_status(self):
        """Get current training status and stats."""
        collection = self.get_collection()
        count = collection.count()
        
        return {
            "is_trained": count > 0,
            "total_entries": count,
            "stats": self.training_stats if self.is_trained else {},
            "storage_path": CHROMA_DIR
        }

# Singleton instance
rag_service = RAGService()
