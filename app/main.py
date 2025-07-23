from fastapi import FastAPI

from app.api.v1.websockets import router as websockets_router

app = FastAPI(title="Chatbot Backend", version="1.0.0")

app.include_router(websockets_router, prefix="/api/v1/websockets", tags=["Websockets"])


@app.get("/")
def root():
    return {"message": "API está corriendo"}
