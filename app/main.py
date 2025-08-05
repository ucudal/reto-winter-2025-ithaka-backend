from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback
from app.api.v1.conversations import router as conversations_router
from app.api.v1.websockets import router as websockets_router

from dotenv import load_dotenv

load_dotenv()

v1 = '/api/v1'

app = FastAPI(title="Chatbot Backend", version="1.0.0", debug=True)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("====== UNHANDLED EXCEPTION ======")
    traceback.print_exc()  
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "trace": traceback.format_exc()
        }
    )@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("====== UNHANDLED EXCEPTION ======")
    traceback.print_exc()  
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "trace": traceback.format_exc()
        }
    )
app.include_router(conversations_router)

app.include_router(websockets_router, prefix=v1 + '/ws', tags=["Websockets"])


@app.get("/")
def root():
    return {"message": "API está corriendo"}

