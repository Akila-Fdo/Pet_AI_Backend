import requests
import json
from langchain.tools import tool

# ✅ FIX: Correct endpoint URL
FASTAPI_URL = "http://127.0.0.1:8000/predict"

@tool
def analyze_pet_image(image_path: str, animal: str, disease_type: str) -> str:
    """
    Analyze pet image and return disease prediction.
    
    Args:
        image_path: Path to the pet image file
        animal: Type of animal (dog or cat)
        disease_type: Type of disease to check (skin or eye)
    
    Returns:
        JSON string containing prediction result with class and confidence
    """
    try:
        # ✅ FIX: Proper file handling with error handling
        with open(image_path, "rb") as f:
            response = requests.post(
                FASTAPI_URL,
                files={"file": f},
                data={
                    "animal": animal,  # ✅ FIX: Now using the animal parameter
                    "disease_type": disease_type,
                    "user_id": "demo"
                },
                timeout=30
            )
        
        response.raise_for_status()  # Raise exception for bad status codes
        
        # ✅ FIX: Return JSON string instead of str(dict)
        result = response.json()
        return json.dumps(result)
    
    except FileNotFoundError:
        return json.dumps({"error": f"Image file not found: {image_path}"})
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"FastAPI request failed: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"})