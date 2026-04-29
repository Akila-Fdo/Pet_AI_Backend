import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DOG_SKIN_MODEL = os.path.join(BASE_DIR, "weights/dog_skin_model.pth")
DOG_EYE_MODEL = os.path.join(BASE_DIR, "weights/dog_eye_model_ResNet_NEW.pth")
CAT_SKIN_MODEL = os.path.join(BASE_DIR, "weights/cat_skin_model.pth")

DEVICE = "cuda" if __import__("torch").cuda.is_available() else "cpu"