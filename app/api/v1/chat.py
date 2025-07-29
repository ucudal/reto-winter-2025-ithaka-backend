from fastapi import APIRouter
from app.langgraph.flow import run_flow  # El método que arma y ejecuta el grafo

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(message: str):
    response = run_flow(message)
    return {"response": response}
