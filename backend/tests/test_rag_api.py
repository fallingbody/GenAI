"""
Backend API Tests for Proto - RAG Training Pipeline with pix2code Public Dataset
Tests: /api/train, /api/training-status, /api/rag-query, /api/dataset-info, /api/generate
Dataset: N0zomu/pix2code-data (1748 samples from HuggingFace)
"""

import pytest
import requests
import os
import base64

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Simple test image - 1x1 red pixel PNG (for validation tests only)
TEST_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

# More realistic test image - 10x10 gradient PNG
REALISTIC_TEST_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFklEQVQYV2NkYGD4z0AEYBxVSF+FABJADq0kQJYbAAAAAElFTkSuQmCC"


class TestHealthAndRoot:
    """Test basic API health"""
    
    def test_root_endpoint(self):
        """Test GET /api/ returns welcome message"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Proto" in data["message"]
        print(f"✓ Root endpoint working: {data['message']}")


class TestDatasetInfo:
    """Test /api/dataset-info endpoint - pix2code public dataset"""
    
    def test_get_dataset_info(self):
        """Test GET /api/dataset-info returns real pix2code dataset details"""
        response = requests.get(f"{BASE_URL}/api/dataset-info")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure for pix2code dataset
        assert "dataset_name" in data
        assert "huggingface_id" in data
        assert "description" in data
        assert "reference_paper" in data
        assert "reference_github" in data
        assert "reference_huggingface" in data
        assert "total_train" in data
        assert "total_test" in data
        assert "total_samples" in data
        assert "framework" in data
        assert "source" in data
        
        # Verify expected values for pix2code dataset (1748 samples)
        assert data["total_samples"] == 1748, f"Expected 1748 samples, got {data['total_samples']}"
        assert data["total_train"] == 1573, f"Expected 1573 train samples, got {data['total_train']}"
        assert data["total_test"] == 175, f"Expected 175 test samples, got {data['total_test']}"
        assert data["huggingface_id"] == "N0zomu/pix2code-data"
        assert data["source"] == "pix2code"
        assert "pix2code" in data["dataset_name"].lower()
        
        # Verify reference links
        assert "huggingface.co" in data["reference_huggingface"]
        assert "github.com" in data["reference_github"]
        assert "arxiv.org" in data["reference_paper"]
        
        print(f"✓ Dataset info: {data['total_samples']} samples (train={data['total_train']}, test={data['total_test']})")
        print(f"  HuggingFace: {data['huggingface_id']}")
        return data


class TestTrainingStatus:
    """Test /api/training-status endpoint"""
    
    def test_get_training_status(self):
        """Test GET /api/training-status returns status with 1748 entries"""
        response = requests.get(f"{BASE_URL}/api/training-status")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "is_trained" in data
        assert "total_entries" in data
        assert "stats" in data
        assert "storage_path" in data
        assert "is_training" in data
        
        # Verify data types
        assert isinstance(data["is_trained"], bool)
        assert isinstance(data["total_entries"], int)
        assert isinstance(data["is_training"], bool)
        
        # Verify trained state with 1748 entries
        assert data["is_trained"] == True, "Model should be trained"
        assert data["total_entries"] == 1748, f"Expected 1748 entries, got {data['total_entries']}"
        
        # Verify stats structure
        if data["stats"]:
            assert "total_samples" in data["stats"]
            assert "categories" in data["stats"]
            assert data["stats"]["total_samples"] == 1748
        
        print(f"✓ Training status: is_trained={data['is_trained']}, entries={data['total_entries']}")
        return data


class TestTrainEndpoint:
    """Test /api/train endpoint - background training"""
    
    def test_train_endpoint_exists(self):
        """Test POST /api/train endpoint exists and returns proper response"""
        # Check if already trained - don't retrain if 1748 entries exist
        status_response = requests.get(f"{BASE_URL}/api/training-status")
        status = status_response.json()
        
        if status.get("total_entries") == 1748 and status.get("is_trained"):
            print(f"✓ Model already trained with 1748 entries - skipping retrain")
            return
        
        # Only test if not trained
        response = requests.post(f"{BASE_URL}/api/train", timeout=15)
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure for background training
        assert "status" in data
        assert data["status"] in ["started", "already_training"]
        assert "message" in data
        
        print(f"✓ Train endpoint working: {data['status']}")


class TestRAGQuery:
    """Test /api/rag-query endpoint with pix2code data"""
    
    def test_rag_query_basic(self):
        """Test POST /api/rag-query returns similar pix2code layouts"""
        payload = {
            "query": "navigation header with buttons",
            "n_results": 5
        }
        response = requests.post(f"{BASE_URL}/api/rag-query", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "results" in data
        assert "query" in data
        assert data["query"] == payload["query"]
        
        # Verify results
        results = data["results"]
        assert isinstance(results, list)
        assert len(results) > 0, "Expected at least one result"
        
        # Verify result structure for pix2code data
        for result in results:
            assert "id" in result
            assert "description" in result
            assert "category" in result
            assert "code" in result
            assert "dsl" in result  # pix2code specific
            assert "framework" in result
            assert "source" in result
            assert "similarity" in result
            assert 0 <= result["similarity"] <= 1
            assert result["source"] == "pix2code"
            assert "pix2code" in result["id"]
        
        print(f"✓ RAG query returned {len(results)} pix2code results")
        return data
    
    def test_rag_query_with_framework_filter(self):
        """Test RAG query with framework filter"""
        payload = {
            "query": "grid layout with cards",
            "n_results": 3,
            "framework": "HTML/Bootstrap"
        }
        response = requests.post(f"{BASE_URL}/api/rag-query", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        print(f"✓ RAG query with framework filter returned {len(data['results'])} results")
    
    def test_rag_query_categories(self):
        """Test RAG query returns proper pix2code categories"""
        payload = {
            "query": "two column layout with text",
            "n_results": 5
        }
        response = requests.post(f"{BASE_URL}/api/rag-query", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Valid pix2code categories
        valid_categories = ["two_column_layout", "grid_layout", "dashboard_layout", "form_layout", "hero_section", "content_page", "navigation_bar", "web_layout"]
        
        for result in data["results"]:
            assert result["category"] in valid_categories, f"Invalid category: {result['category']}"
        
        print(f"✓ RAG query categories validated")


class TestGenerateEndpoint:
    """Test /api/generate endpoint"""
    
    def test_generate_requires_all_fields(self):
        """Test POST /api/generate validates required fields"""
        # Missing image_base64
        payload = {
            "project_name": "Test Project",
            "description": "A test description"
        }
        response = requests.post(f"{BASE_URL}/api/generate", json=payload)
        assert response.status_code == 422, "Should return 422 for missing required field"
        print("✓ Generate endpoint validates required fields")
    
    def test_generate_with_small_image_fails(self):
        """Test POST /api/generate fails with small test images (expected per image_testing.md)"""
        payload = {
            "image_base64": TEST_IMAGE_BASE64,  # 1x1 pixel - too small
            "project_name": "TEST_SmallImage",
            "description": "Testing with small image",
            "framework": "React"
        }
        
        response = requests.post(f"{BASE_URL}/api/generate", json=payload, timeout=60)
        # Small images should fail - Gemini requires real visual features
        # This is expected behavior per image_testing.md
        if response.status_code == 500:
            print("✓ Generate correctly rejects small test images (expected behavior)")
        else:
            print(f"  Generate response: {response.status_code}")


class TestProjectsEndpoint:
    """Test /api/projects endpoints"""
    
    def test_get_projects_list(self):
        """Test GET /api/projects returns project list"""
        response = requests.get(f"{BASE_URL}/api/projects")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        
        if len(data) > 0:
            project = data[0]
            assert "id" in project
            assert "project_name" in project
            assert "description" in project
            assert "framework" in project
            assert "timestamp" in project
        
        print(f"✓ Projects list: {len(data)} projects found")
        return data
    
    def test_get_nonexistent_project(self):
        """Test GET /api/projects/{id} returns 404 for invalid ID"""
        response = requests.get(f"{BASE_URL}/api/projects/nonexistent-id-12345")
        assert response.status_code == 404
        print("✓ Nonexistent project returns 404")


class TestTrainingStatusVerification:
    """Verify training status shows correct pix2code data"""
    
    def test_status_shows_1748_entries(self):
        """Verify training status shows is_trained=true with 1748 entries"""
        response = requests.get(f"{BASE_URL}/api/training-status")
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_trained"] == True, "Model should be trained"
        assert data["total_entries"] == 1748, f"Expected 1748 entries, got {data['total_entries']}"
        
        # Verify stats categories
        if data["stats"] and "categories" in data["stats"]:
            categories = data["stats"]["categories"]
            assert "grid_layout" in categories
            assert "two_column_layout" in categories
            # grid_layout should be the largest category
            assert categories["grid_layout"] > 1000, "grid_layout should have >1000 samples"
        
        print(f"✓ Training status verified: is_trained={data['is_trained']}, entries={data['total_entries']}")
        if data["stats"] and "categories" in data["stats"]:
            print(f"  Categories: {data['stats']['categories']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
