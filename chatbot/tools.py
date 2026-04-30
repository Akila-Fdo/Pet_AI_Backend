import requests
import json
import os
from langchain.tools import tool

# ✅ FIX: Correct endpoint URL
FASTAPI_URL = "http://127.0.0.1:8000/predict"

@tool(return_direct=False)
def analyze_pet_image(input_request: str) -> str:
    """Analyze a pet image to detect skin or eye diseases. Input should be JSON with image_path, animal, and disease_type fields. Returns prediction and confidence."""
    try:
        # Parse JSON input
        params = json.loads(input_request)
        
        image_path = params.get("image_path")
        animal = params.get("animal", "dog")
        disease_type = params.get("disease_type")
        
        if not image_path:
            return json.dumps({"error": "image_path is required"})
        if not disease_type:
            return json.dumps({"error": "disease_type is required (skin or eye)"})
        
        # Check if file exists
        if not os.path.exists(image_path):
            return json.dumps({"error": f"Image file not found: {image_path}"})
        
        # Call FastAPI endpoint
        with open(image_path, "rb") as f:
            response = requests.post(
                FASTAPI_URL,
                files={"file": f},
                data={
                    "animal": animal,
                    "disease_type": disease_type,
                    "user_id": "demo"
                },
                timeout=30
            )
        
        response.raise_for_status()
        result = response.json()
        return json.dumps(result)
    
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON input format"})
    except FileNotFoundError as e:
        return json.dumps({"error": f"Image file not found: {str(e)}"})
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"FastAPI request failed: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})