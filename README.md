# 🤖 Ithaka Chatbot Backend - Componente de IA

Backend inteligente para el chatbot de postulaciones de **Ithaka**, el centro de emprendimiento e innovación de la Universidad Católica del Uruguay (UCU).

## 🎯 Descripción del Proyecto

Este componente de IA forma parte de un proyecto fullstack más amplio. Está diseñado como un **microservicio independiente** que maneja toda la lógica de inteligencia artificial para:

- **Wizard conversacional** de 20+ preguntas para postulaciones
- **Sistema de FAQs** con búsqueda semántica avanzada
- **Validaciones en tiempo real** de datos críticos (email, cédula, etc.)
- **Persistencia de conversaciones** y seguimiento de progreso
- **Integración WebSocket** para comunicación en tiempo real

## 🚀 Tecnologías Utilizadas

- **LangGraph** + **LangChain**: Flujo conversacional inteligente y orquestación de IA
- **ChromaDB**: Base de datos vectorial para búsqueda semántica de FAQs
- **FastAPI**: Framework web moderno y rápido con WebSockets
- **PostgreSQL**: Persistencia de conversaciones y postulaciones
- **Docker**: Containerización para desarrollo y producción
- **OpenAI GPT-4**: Modelo de lenguaje principal

## 📋 Funcionalidades Principales

### 1. **Wizard de Postulación Inteligente**

- 20 preguntas dinámicas basadas en las respuestas del usuario
- Validación en tiempo real de emails, teléfonos, y otros datos
- Flujo condicional (preguntas adicionales solo si tiene idea/emprendimiento)
- Persistencia automática del progreso

### 2. **Sistema de FAQs Avanzado**

- Búsqueda semántica con ChromaDB y embeddings OpenAI
- 10+ FAQs precargadas sobre Ithaka, cursos, programas
- Categorización automática (cursos, emprendimiento, fellows, recursos)
- Fallback a búsqueda por palabras clave si no hay embeddings

### 3. **API RESTful + WebSockets**

- Comunicación en tiempo real via WebSockets
- Endpoints REST alternativos para integración
- Documentación automática con Swagger/OpenAPI
- Health checks y monitoreo

## 🛠️ Instalación y Configuración

### Prerequisitos

- **Docker** y **Docker Compose**
- **Python 3.11+** (para desarrollo local)
- **PostgreSQL** (incluido en Docker Compose)

### 1. Clonar y Configurar

```bash
# Clonar el repositorio
git clone <repository-url>
cd reto-winter-2025-ithaka-backend

# Crear archivo .env con tus configuraciones
cp .env.example .env
```

### 2. Configurar Variables de Entorno

Edita el archivo `.env`:

```env
# API Keys (críticas para funcionamiento completo)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Base de datos
DATABASE_URL=postgresql://ithaka_user:ithaka_password@localhost:5432/ithaka_chatbot

# Configuración del servidor
HOST=0.0.0.0
PORT=8000
DEBUG=true

# ChromaDB
CHROMA_DB_PATH=./data/chroma_db

# JWT (para futuras funcionalidades de auth)
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Levantar con Docker (Recomendado)

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f chatbot_backend

# Levantar con PGAdmin (opcional, para administrar BD)
docker-compose --profile admin up -d
```

### 4. Desarrollo Local (Alternativo)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Levantar solo PostgreSQL
docker-compose up -d postgres

# Correr servidor en modo desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🎮 Uso y Testing

### 1. **Verificar que esté funcionando**

```bash
# Health check
curl http://localhost:8000/health

# Información del servicio
curl http://localhost:8000/
```

### 2. **Probar el Chat via REST**

```bash
# Enviar mensaje
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hola, quiero postular mi idea",
    "session_id": "test-session-123"
  }'
```

### 3. **Probar FAQs**

```bash
# Buscar FAQs
curl "http://localhost:8000/api/v1/faq/search/programa%20fellows"

# Ver todas las categorías
curl "http://localhost:8000/api/v1/faq/categories"
```

### 4. **WebSocket (usando JavaScript)**

```javascript
const ws = new WebSocket("ws://localhost:8000/api/v1/websockets/ws/chat");

ws.onopen = function () {
  // Enviar mensaje
  ws.send(
    JSON.stringify({
      message: "¿Qué es el programa Fellows?",
      sender: "user",
      type: "text",
      session_id: "test-123",
    })
  );
};

ws.onmessage = function (event) {
  const response = JSON.parse(event.data);
  console.log("Bot:", response.message);
};
```

## 📖 Documentación de la API

Una vez levantado el servidor, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Principales

| Método | Endpoint                            | Descripción               |
| ------ | ----------------------------------- | ------------------------- |
| `GET`  | `/`                                 | Información del servicio  |
| `GET`  | `/health`                           | Health check              |
| `WS`   | `/api/v1/websockets/ws/chat`        | WebSocket para chat       |
| `POST` | `/api/v1/chat/message`              | Enviar mensaje (REST)     |
| `GET`  | `/api/v1/chat/history/{session_id}` | Historial de conversación |
| `GET`  | `/api/v1/chat/wizard/steps`         | Información del wizard    |
| `POST` | `/api/v1/faq/search`                | Buscar FAQs               |
| `GET`  | `/api/v1/faq/categories`            | Categorías de FAQs        |

## 🧪 Testing del Wizard Completo

Para probar el flujo completo de postulación:

1. **Iniciar conversación**: "Hola, quiero postular"
2. **Seguir el wizard**: Responder cada pregunta
3. **Probar validaciones**: Ingresar email inválido
4. **Flujo condicional**: Decir "Sí" a "¿Tienes una idea?"
5. **Completar**: Responder todas las preguntas requeridas

El sistema te guiará através de los 20+ pasos según tus respuestas.

## 📁 Estructura del Proyecto

```
reto-winter-2025-ithaka-backend/
├── app/
│   ├── api/v1/              # Endpoints REST
│   ├── config/              # Configuraciones
│   ├── db/                  # Base de datos y modelos
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Lógica de negocio (IA)
│   ├── websockets/          # Manejo de WebSockets
│   └── main.py             # Aplicación principal
├── db/init/                # Scripts de inicialización
├── data/                   # Datos persistentes (ChromaDB)
├── docker-compose.yml      # Configuración Docker
├── Dockerfile             # Imagen del contenedor
└── requirements.txt       # Dependencias Python
```

## 🔧 Servicios Principales

### 1. **ChatService** (`app/services/chat_service.py`)

- Orquesta todo el flujo conversacional usando LangGraph
- Clasifica intenciones (wizard, faq, general)
- Maneja validaciones y genera respuestas contextuales

### 2. **FAQService** (`app/services/faq_service.py`)

- Búsqueda semántica con ChromaDB
- 10+ FAQs precargadas sobre Ithaka
- Fallback a búsqueda por palabras clave

### 3. **WizardConfig** (`app/services/wizard_config.py`)

- Configuración de las 20 preguntas
- Lógica de flujo condicional
- Validaciones por tipo de campo

## 🐛 Troubleshooting

### Problemas Comunes

**1. Error "API key not configured"**

```bash
# Verificar que OPENAI_API_KEY esté configurada
echo $OPENAI_API_KEY
```

**2. Error de conexión a PostgreSQL**

```bash
# Verificar que el contenedor esté corriendo
docker-compose ps postgres

# Ver logs de PostgreSQL
docker-compose logs postgres
```

**3. ChromaDB no inicializa**

```bash
# Verificar permisos de directorio
ls -la data/chroma_db/

# Recrear volumen
docker-compose down -v
docker-compose up -d
```

**4. WebSocket se desconecta**

- Verificar que no haya proxy/firewall bloqueando
- Usar `ws://` en desarrollo, `wss://` en producción

### Logs y Debugging

```bash
# Ver logs del backend
docker-compose logs -f chatbot_backend

# Acceder al contenedor
docker exec -it ithaka_chatbot_backend bash

# Verificar servicios
curl http://localhost:8000/health
```

## 🔄 Desarrollo y Contribución

### Agregar nuevas FAQs

```python
# Editar app/services/faq_service.py
ITHAKA_FAQS.append({
    "question": "Nueva pregunta",
    "answer": "Nueva respuesta",
    "category": "categoria",
    "keywords": "palabras clave"
})
```

### Modificar preguntas del wizard

```python
# Editar app/services/wizard_config.py
WIZARD_STEPS.append(WizardStep(
    step_number=22,
    question="¿Nueva pregunta?",
    field_name="nuevo_campo",
    validation_type="text",
    required=True
))
```

### Testing Manual

Usa la documentación interactiva en `/docs` para probar todos los endpoints.

## 🚢 Despliegue en Producción

### Variables Críticas

```env
# CRÍTICO: Cambiar en producción
SECRET_KEY=production-secret-key-very-secure
OPENAI_API_KEY=sk-real-openai-key
DATABASE_URL=postgresql://user:pass@prod-db:5432/db

# Configuración de producción
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

### Consideraciones

1. **Seguridad**: Cambiar todas las claves por defecto
2. **Base de datos**: Usar PostgreSQL gestionado (AWS RDS, etc.)
3. **Backup**: Configurar backups automáticos de BD y ChromaDB
4. **Monitoreo**: Implementar logging y métricas
5. **SSL**: Usar HTTPS y WSS para WebSockets

## 📊 Características del Sistema

- **Escalable**: Diseñado como microservicio independiente
- **Resiliente**: Fallbacks para cuando no hay API keys
- **Eficiente**: Búsqueda vectorial optimizada con ChromaDB
- **Mantenible**: Código bien estructurado y documentado
- **Testeable**: Health checks y endpoints de monitoreo
- **Flexible**: Fácil agregar nuevas preguntas/FAQs

## 🤝 Integración con Frontend/Backend

Este componente está diseñado para integrarse fácilmente:

- **WebSocket**: Para interfaces en tiempo real
- **REST API**: Para integraciones síncronas
- **Datos estructurados**: JSON bien definido
- **CORS configurado**: Para desarrollo local
- **Documentación**: Swagger automático

## 📞 Soporte

Para preguntas sobre este componente de IA:

1. Revisar logs: `docker-compose logs chatbot_backend`
2. Verificar configuración: `/health` endpoint
3. Probar endpoints: `/docs` para documentación interactiva
4. Consultar este README para troubleshooting

---

✨ **¡El componente de IA está listo para integrarse con tu aplicación fullstack!** ✨
