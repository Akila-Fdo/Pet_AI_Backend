from fastapi import FastAPI, UploadFile, File, Form
from app.models import dog_skin, dog_eye, cat_skin
from app.utils.image import preprocess
from app.services.router import route_prediction

app = FastAPI(title="Pet AI Disease Detection API")

# 🔥 Load models ONCE
@app.on_event("startup")
def load_models():
    app.state.dog_skin = dog_skin.load_model()
    app.state.dog_eye = dog_eye.load_model()
    app.state.cat_skin = cat_skin.load_model()

# 📸 Prediction endpoint
@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    animal: str = Form(...),
    disease_type: str = Form(...)
):
    image = preprocess(file.file)

    result = route_prediction(app, animal, disease_type, image)

    return result