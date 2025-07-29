from app.api.v1.websockets import router as websockets_router
from fastapi import FastAPI
from app.api.v1.conversations import router as conversations_router

v1 = '/api/v1'

app = FastAPI(title="Chatbot Backend", version="1.0.0")

app.include_router(conversations_router)

app.include_router(websockets_router, prefix=v1 + '/ws', tags=["Websockets"])


@app.get("/")
def root():
    return {"message": "API está corriendo"}
