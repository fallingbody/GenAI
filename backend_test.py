import requests
import sys
import base64
import json
from datetime import datetime
from io import BytesIO
from PIL import Image

class ProtoAPITester:
    def __init__(self, base_url="https://pdf-frontend-gen.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def create_test_image_base64(self):
        """Create a simple test image and return base64 string"""
        try:
            # Create a simple test image with some visual features
            img = Image.new('RGB', (200, 150), color='white')
            
            # Add some visual elements to make it a valid UI mockup
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            
            # Draw a simple UI mockup
            draw.rectangle([20, 20, 180, 40], fill='blue', outline='black')  # Header
            draw.rectangle([20, 50, 80, 70], fill='green', outline='black')  # Button 1
            draw.rectangle([100, 50, 160, 70], fill='red', outline='black')  # Button 2
            draw.rectangle([20, 80, 180, 130], fill='lightgray', outline='black')  # Content area
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return img_str
        except Exception as e:
            print(f"Error creating test image: {e}")
            return None

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Response: {data}"
            self.log_test("Root Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("Root Endpoint", False, str(e))
            return False

    def test_generate_code_endpoint(self):
        """Test the code generation endpoint"""
        try:
            # Create test image
            test_image = self.create_test_image_base64()
            if not test_image:
                self.log_test("Generate Code - Image Creation", False, "Failed to create test image")
                return False

            # Test data
            test_data = {
                "image_base64": test_image,
                "project_name": "Test UI Project",
                "description": "A simple test UI with header, buttons, and content area",
                "framework": "React"
            }

            response = requests.post(
                f"{self.api_url}/generate",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=60  # Longer timeout for AI generation
            )

            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                # Check required fields in response
                required_fields = ['id', 'project_name', 'description', 'framework', 'generated_code', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details += f", Missing fields: {missing_fields}"
                else:
                    details += f", Generated code length: {len(data.get('generated_code', ''))}"
                    # Store the project ID for later tests
                    self.test_project_id = data.get('id')
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"

            self.log_test("Generate Code Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("Generate Code Endpoint", False, str(e))
            return False

    def test_projects_list_endpoint(self):
        """Test the projects list endpoint"""
        try:
            response = requests.get(f"{self.api_url}/projects", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Projects count: {len(data)}"
                
                # Check structure of first project if any exist
                if data:
                    project = data[0]
                    required_fields = ['id', 'project_name', 'description', 'framework', 'timestamp']
                    missing_fields = [field for field in required_fields if field not in project]
                    if missing_fields:
                        success = False
                        details += f", Missing fields in project: {missing_fields}"
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"

            self.log_test("Projects List Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("Projects List Endpoint", False, str(e))
            return False

    def test_specific_project_endpoint(self):
        """Test getting a specific project"""
        if not hasattr(self, 'test_project_id'):
            self.log_test("Specific Project Endpoint", False, "No test project ID available")
            return False

        try:
            response = requests.get(f"{self.api_url}/projects/{self.test_project_id}", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                required_fields = ['id', 'project_name', 'description', 'framework', 'generated_code', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details += f", Missing fields: {missing_fields}"
                else:
                    details += f", Project: {data.get('project_name')}"
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"

            self.log_test("Specific Project Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("Specific Project Endpoint", False, str(e))
            return False

    def test_invalid_requests(self):
        """Test error handling with invalid requests"""
        try:
            # Test generate endpoint without required fields
            response = requests.post(
                f"{self.api_url}/generate",
                json={"project_name": "Test"},  # Missing required fields
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            success = response.status_code in [400, 422]  # Should return validation error
            details = f"Status: {response.status_code} (expected 400/422)"
            
            self.log_test("Invalid Request Handling", success, details)
            return success
        except Exception as e:
            self.log_test("Invalid Request Handling", False, str(e))
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Proto Backend API Tests")
        print(f"Testing against: {self.api_url}")
        print("=" * 50)

        # Test basic connectivity first
        if not self.test_root_endpoint():
            print("❌ Root endpoint failed - stopping tests")
            return False

        # Test main functionality
        self.test_generate_code_endpoint()
        self.test_projects_list_endpoint()
        self.test_specific_project_endpoint()
        self.test_invalid_requests()

        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed")
            return False

def main():
    tester = ProtoAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())