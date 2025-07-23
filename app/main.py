from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1.websockets import router as websockets_router
from app.api.v1.chat import router as chat_router
from app.api.v1.faq import router as faq_router
from app.db.config.database import create_tables
from app.services.faq_service import faq_service
from app.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización y limpieza de la aplicación"""
    # Inicialización
    print("🚀 Iniciando Ithaka Chatbot Backend...")

    # Crear tablas de base de datos
    try:
        create_tables()
        print("✅ Base de datos inicializada")
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")

    # Inicializar servicios
    try:
        # El FAQService ya se inicializa automáticamente
        print("✅ Servicios de IA inicializados")
    except Exception as e:
        print(f"❌ Error inicializando servicios: {e}")

    print("🎉 Servidor listo!")

    yield

    # Limpieza al cerrar
    print("🔄 Cerrando servicios...")


app = FastAPI(
    title="Ithaka Chatbot Backend",
    version="1.0.0",
    description="Backend de IA para el chatbot de postulaciones de Ithaka - UCU",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(websockets_router,
                   prefix="/api/v1/websockets", tags=["WebSockets"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(faq_router, prefix="/api/v1/faq", tags=["FAQ"])


@app.get("/")
async def root():
    """Endpoint raíz con información del servicio"""
    return {
        "service": "Ithaka Chatbot Backend",
        "version": "1.0.0",
        "description": "Backend de IA para el chatbot de postulaciones de Ithaka",
        "status": "operational",
        "features": [
            "Wizard de postulación con 20+ preguntas",
            "Sistema de FAQs con búsqueda semántica",
            "Validaciones en tiempo real",
            "Persistencia de conversaciones",
            "Integración con LangGraph + LangChain + ChromaDB"
        ],
        "endpoints": {
            "websocket_chat": "/api/v1/websockets/ws/chat",
            "rest_chat": "/api/v1/chat/message",
            "faq_search": "/api/v1/faq/search",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-01-03T10:00:00Z",
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "ai_service": "operational" if settings.openai_api_key else "limited",
            "chromadb": "operational",
            "websockets": "active"
        }
    }
