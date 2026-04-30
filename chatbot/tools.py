import requests
from langchain.tools import tool

FASTAPI_URL = "http://127.0.0.1:8000/analyze-image"

@tool
def analyze_pet_image(image_path: str, animal: str, disease_type: str) -> str:
    """
    Analyze pet image and return disease prediction.
    """

    with open(image_path, "rb") as f:
        response = requests.post(
            FASTAPI_URL,
            files={"file": f},
            data={
                "disease_type": disease_type,
                "user_id": "demo"
            }
        )

    return str(response.json())