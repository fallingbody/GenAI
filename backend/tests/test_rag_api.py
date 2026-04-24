"""
Backend API Tests for Proto - RAG Training Pipeline
Tests: /api/train, /api/training-status, /api/rag-query, /api/dataset-info, /api/generate
"""

import pytest
import requests
import os
import base64

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Simple test image - 1x1 red pixel PNG
TEST_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

# More realistic test image - 10x10 gradient PNG for better testing
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


class TestTrainingStatus:
    """Test /api/training-status endpoint"""
    
    def test_get_training_status(self):
        """Test GET /api/training-status returns status info"""
        response = requests.get(f"{BASE_URL}/api/training-status")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "is_trained" in data
        assert "total_entries" in data
        assert "stats" in data
        assert "storage_path" in data
        
        # Verify data types
        assert isinstance(data["is_trained"], bool)
        assert isinstance(data["total_entries"], int)
        
        print(f"✓ Training status: is_trained={data['is_trained']}, entries={data['total_entries']}")
        return data


class TestDatasetInfo:
    """Test /api/dataset-info endpoint"""
    
    def test_get_dataset_info(self):
        """Test GET /api/dataset-info returns dataset details"""
        response = requests.get(f"{BASE_URL}/api/dataset-info")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "total_samples" in data
        assert "categories" in data
        assert "frameworks" in data
        assert "sources" in data
        assert "dataset_name" in data
        assert "description" in data
        assert "reference" in data
        
        # Verify expected values
        assert data["total_samples"] == 46, f"Expected 46 samples, got {data['total_samples']}"
        assert "pix2code" in data["sources"]
        assert "curated" in data["sources"]
        assert data["sources"]["pix2code"] == 30, f"Expected 30 pix2code samples"
        assert data["sources"]["curated"] == 16, f"Expected 16 curated samples"
        
        print(f"✓ Dataset info: {data['total_samples']} samples ({data['sources']})")
        return data


class TestTrainEndpoint:
    """Test /api/train endpoint"""
    
    def test_train_rag_model(self):
        """Test POST /api/train trains the model"""
        response = requests.post(f"{BASE_URL}/api/train", timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "status" in data
        assert data["status"] == "success"
        assert "message" in data
        assert "stats" in data
        
        # Verify stats
        stats = data["stats"]
        assert "total_samples" in stats
        assert stats["total_samples"] == 46
        assert "categories" in stats
        assert "frameworks" in stats
        assert "sources" in stats
        
        print(f"✓ Training complete: {stats['total_samples']} samples loaded")
        return data


class TestRAGQuery:
    """Test /api/rag-query endpoint"""
    
    def test_rag_query_basic(self):
        """Test POST /api/rag-query returns similar UI examples"""
        # First ensure model is trained
        status_response = requests.get(f"{BASE_URL}/api/training-status")
        status = status_response.json()
        
        if not status["is_trained"] or status["total_entries"] == 0:
            # Train first
            requests.post(f"{BASE_URL}/api/train", timeout=60)
        
        # Now query
        payload = {
            "query": "login form with email and password inputs",
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
        
        # Verify result structure
        for result in results:
            assert "id" in result
            assert "description" in result
            assert "category" in result
            assert "code" in result
            assert "framework" in result
            assert "similarity" in result
            assert 0 <= result["similarity"] <= 1
        
        print(f"✓ RAG query returned {len(results)} results")
        return data
    
    def test_rag_query_with_framework_filter(self):
        """Test RAG query with framework filter"""
        payload = {
            "query": "dashboard with stats cards",
            "n_results": 3,
            "framework": "React"
        }
        response = requests.post(f"{BASE_URL}/api/rag-query", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        print(f"✓ RAG query with framework filter returned {len(data['results'])} results")
    
    def test_rag_query_not_trained_error(self):
        """Test RAG query returns error when not trained (if applicable)"""
        # This test is informational - the model should be trained
        status_response = requests.get(f"{BASE_URL}/api/training-status")
        status = status_response.json()
        
        if status["is_trained"]:
            print("✓ Model is trained, skipping not-trained error test")
        else:
            payload = {"query": "test query"}
            response = requests.post(f"{BASE_URL}/api/rag-query", json=payload)
            assert response.status_code == 400
            print("✓ RAG query correctly returns 400 when not trained")


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
    
    def test_generate_with_valid_image(self):
        """Test POST /api/generate with valid image (full integration test)"""
        # First ensure model is trained
        status_response = requests.get(f"{BASE_URL}/api/training-status")
        status = status_response.json()
        
        if not status["is_trained"] or status["total_entries"] == 0:
            train_response = requests.post(f"{BASE_URL}/api/train", timeout=60)
            assert train_response.status_code == 200
        
        # Generate code
        payload = {
            "image_base64": REALISTIC_TEST_IMAGE,
            "project_name": "TEST_LoginPage",
            "description": "A simple login form with email and password fields",
            "framework": "React"
        }
        
        response = requests.post(f"{BASE_URL}/api/generate", json=payload, timeout=120)
        assert response.status_code == 200, f"Generate failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "project_name" in data
        assert data["project_name"] == "TEST_LoginPage"
        assert "description" in data
        assert "framework" in data
        assert data["framework"] == "React"
        assert "generated_code" in data
        assert len(data["generated_code"]) > 0
        assert "rag_context" in data
        assert "timestamp" in data
        
        print(f"✓ Code generated successfully: {len(data['generated_code'])} chars")
        print(f"  RAG context: {len(data['rag_context'])} references used")
        return data


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
    
    def test_get_project_by_id(self):
        """Test GET /api/projects/{id} returns specific project"""
        # First get list
        list_response = requests.get(f"{BASE_URL}/api/projects")
        projects = list_response.json()
        
        if len(projects) == 0:
            pytest.skip("No projects to test")
        
        project_id = projects[0]["id"]
        response = requests.get(f"{BASE_URL}/api/projects/{project_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == project_id
        assert "generated_code" in data
        
        print(f"✓ Project retrieved: {data['project_name']}")
    
    def test_get_nonexistent_project(self):
        """Test GET /api/projects/{id} returns 404 for invalid ID"""
        response = requests.get(f"{BASE_URL}/api/projects/nonexistent-id-12345")
        assert response.status_code == 404
        print("✓ Nonexistent project returns 404")


class TestTrainingStatusAfterTrain:
    """Verify training status after training"""
    
    def test_status_shows_trained(self):
        """Verify training status shows is_trained=true with 46 entries"""
        # Ensure trained
        requests.post(f"{BASE_URL}/api/train", timeout=60)
        
        response = requests.get(f"{BASE_URL}/api/training-status")
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_trained"] == True, "Model should be trained"
        assert data["total_entries"] == 46, f"Expected 46 entries, got {data['total_entries']}"
        
        print(f"✓ Training status verified: is_trained={data['is_trained']}, entries={data['total_entries']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
