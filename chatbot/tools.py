import requests
import json
import os
from langchain.tools import tool

# ✅ FIX: Correct endpoint URL
FASTAPI_URL = "http://127.0.0.1:8000/predict"

@tool(return_direct=False)
def analyze_pet_image(input_request: str) -> str:
    """Analyze a pet image to detect diseases. Input: JSON string with image_path, animal, disease_type. Only call if user provides real image path."""
    try:
        # Parse JSON input
        params = json.loads(input_request)
        
        image_path = params.get("image_path")
        animal = params.get("animal", "dog")
        disease_type = params.get("disease_type")
        
        if not image_path:
            return json.dumps({"error": "❌ Missing image_path. Ask user for actual file path."})
        
        # Check for placeholder paths - guide agent away from using them
        if "/path/to" in image_path.lower() or "example" in image_path.lower():
            return json.dumps({"error": "❌ This is a placeholder path. Ask the user for their actual image file path."})
        
        if not disease_type:
            return json.dumps({"error": "❌ Missing disease_type. Should be 'skin' or 'eye'."})
        
        # Check if file exists
        if not os.path.exists(image_path):
            return json.dumps({"error": f"❌ Image not found at: {image_path}\nAsk user to verify the path is correct."})
        
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