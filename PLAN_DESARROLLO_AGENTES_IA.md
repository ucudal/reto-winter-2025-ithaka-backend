# Plan de Desarrollo - Sistema de Agentes IA para Ithaka Backend

## 🎯 Objetivo General

Integrar un sistema de agentes IA conversacionales usando LangGraph + LangChain para crear un chatbot inteligente que maneje postulaciones emprendedoras, FAQs y validaciones con interacción human-in-the-loop.

## 🏗️ Arquitectura de Agentes

### 1. **Agente Supervisor** (Router/Orchestrator)

- **Función**: Analizar intención del usuario y rutear a agente apropiado
- **Tecnología**: LangGraph + LangChain con OpenAI
- **Inputs**: Mensaje del usuario + historial de conversación
- **Outputs**: Decisión de routing + contexto para agente destino
- **Estados posibles**:
  - `ROUTING` → Analizando intención
  - `DELEGATING` → Enviando a agente específico
  - `WAITING` → Esperando respuesta de agente

### 2. **Agente Wizard** (Formulario Conversacional)

- **Función**: Guiar proceso de postulación paso a paso
- **Estados del flujo**:
  - `ASKING_QUESTION` → Formulando pregunta actual
  - `VALIDATING_RESPONSE` → Verificando respuesta con criterios de rúbrica
  - `WAITING_CONFIRMATION` → Human-in-the-loop para confirmar/corregir
  - `ITERATING_IMPROVEMENT` → Sugiriendo mejoras basadas en rúbrica
  - `SAVING_PROGRESS` → Persistiendo respuesta válida
  - `COMPLETING` → Finalizando postulación
- **Comandos especiales**: `"volver"` (pregunta anterior), `"cancelar"` (terminar sesión)

### 3. **Agente FAQ** (Preguntas Frecuentes)

- **Función**: Responder consultas usando base de conocimiento vectorial
- **Tecnología**: PGVector + embeddings de OpenAI
- **Estados**:
  - `SEARCHING` → Buscando en base vectorial
  - `GENERATING_RESPONSE` → Creando respuesta contextualizada
  - `CLARIFYING` → Pidiendo más detalles si query ambigua

### 4. **Agente Validator** (Validación de Datos)

- **Función**: Validar campos específicos usando funciones existentes
- **Integración**: Con `utils/validators.py` existente
- **Estados**:
  - `VALIDATING` → Ejecutando validaciones
  - `ERROR_HANDLING` → Manejando errores de validación
  - `SUCCESS` → Confirmando datos válidos

## 📊 Base de Datos y Persistencia

### Modelos Existentes (mantenidos):

```python
# Ya existentes en app/db/models.py
Conversation(id, email?, started_at)
Message(id, conv_id, role, content, ts)
Postulation(id, conv_id, payload_json, created_at)
```

### Nuevos Modelos:

```python
# Nuevo modelo para FAQ con PGVector
class FAQEmbedding(Base):
    __tablename__ = "faq_embeddings"
    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI embeddings dimension
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Modelo para sesiones del wizard
class WizardSession(Base):
    __tablename__ = "wizard_sessions"
    id = Column(Integer, primary_key=True)
    conv_id = Column(Integer, ForeignKey("conversations.id"))
    current_question = Column(Integer, default=1)
    responses = Column(JSON, default={})
    state = Column(String(50), default="ACTIVE")  # ACTIVE, PAUSED, COMPLETED, CANCELLED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

## 🔄 Flujo de Interacción Detallado

### Inicio de Conversación:

1. **Usuario conecta WebSocket** → Supervisor analiza primer mensaje
2. **Detección de intención**:
   - `"postular"/"emprender"/"formulario"` → Wizard Agent
   - `"pregunta"/"consulta"/"FAQ"` → FAQ Agent
   - `"validar email/teléfono/cédula"` → Validator Agent

### Flujo Wizard (Postulación):

```mermaid
graph TD
    A[Usuario: "Quiero postular"] --> B[Supervisor: Detecta intención]
    B --> C[Wizard: Inicia sesión]
    C --> D[Pregunta 1: Apellido, Nombre]
    D --> E[Validación inmediata]
    E --> F{¿Válida?}
    F -->|No| G[Human-in-loop: ¿Corregir?]
    F -->|Sí| H[Guardar respuesta]
    G -->|Corregir| D
    G -->|Cancelar| I[Terminar sesión]
    H --> J[Siguiente pregunta]
    J --> K{¿Pregunta 11 completada?}
    K -->|No| D
    K -->|Sí| L[Preguntas evaluativas con rúbrica]
    L --> M[IA evalúa con criterios]
    M --> N{¿Respuesta convincente?}
    N -->|No| O[Sugerir mejoras]
    N -->|Sí| P[Continuar]
    O --> Q[Human-in-loop: ¿Mejorar?]
    Q -->|Sí| L
    Q -->|No| P
    P --> R{¿Todas completadas?}
    R -->|No| L
    R -->|Sí| S[Guardar postulación completa]
    S --> T[Enviar confirmación]
```

### Estados de Sesión del Wizard:

- **Persistencia**: Solo si usuario proporcionó email (pregunta 2)
- **Recuperación**: Al reconectar, cargar `WizardSession` existente
- **Comandos**:
  - `"volver"` → `current_question -= 1`
  - `"cancelar"` → `state = "CANCELLED"`

## 🧠 Implementación de Agentes con LangGraph

### Estructura de Archivos:

```
app/
├── agents/
│   ├── __init__.py
│   ├── supervisor.py          # Agente principal de routing
│   ├── wizard.py             # Agente formulario
│   ├── faq.py               # Agente FAQ con vectores
│   ├── validator.py         # Agente validaciones
│   └── schemas.py           # Schemas compartidos
├── graph/
│   ├── __init__.py
│   ├── state.py            # Estado compartido del grafo
│   ├── workflow.py         # Definición del grafo LangGraph
│   └── nodes.py           # Nodos del grafo
├── services/
│   ├── chat_service.py     # Servicio principal (ACTUALIZAR)
│   ├── embedding_service.py # Servicio embeddings
│   └── evaluation_service.py # Servicio rúbrica
└── db/
    └── models.py          # Agregar nuevos modelos
```

### Grafo LangGraph Principal:

```python
# app/graph/workflow.py
from langgraph.graph import StateGraph
from .state import ConversationState
from ..agents import supervisor, wizard, faq, validator

workflow = StateGraph(ConversationState)

# Nodos
workflow.add_node("supervisor", supervisor.route_message)
workflow.add_node("wizard", wizard.handle_wizard_flow)
workflow.add_node("faq", faq.handle_faq_query)
workflow.add_node("validator", validator.validate_data)

# Bordes condicionales
workflow.add_conditional_edges(
    "supervisor",
    supervisor.decide_next_agent,
    {
        "wizard": "wizard",
        "faq": "faq",
        "validator": "validator",
        "end": "__end__"
    }
)

# Punto de entrada
workflow.set_entry_point("supervisor")
```

## 📝 Preguntas del Wizard y Validaciones

### Preguntas 1-11 (Datos Personales - Obligatorias):

1. **Apellido, Nombre** → Validación: No vacío, formato nombre
2. **Mail** → Validación: `validate_email()` existente + persistir conversación
3. **Celular/Teléfono** → Validación: `validate_phone()` existente
4. **Nº Documento** → Validación: `validate_ci()` existente
5. **País y localidad** → Validación: Lista predefinida
6. **Campus UCU** → Validación: ["Maldonado", "Montevideo", "Salto"]
7. **Relación con UCU** → Validación: Lista predefinida
8. **Facultad** → Condicional: Solo si relación con UCU existe
9. **Cómo llegaste a Ithaka** → Validación: Lista predefinida
10. **Qué te motiva** → Validación: Mínimo 10 caracteres
11. **Tienes idea/emprendimiento** → Validación: [NO, SI] - Si NO → Finalizar

### Preguntas 12-20 (Evaluativas - Con Rúbrica IA):

- **Contexto de rúbrica** inyectado en prompt del agente
- **Evaluación en tiempo real** con criterios específicos
- **Iteración human-in-the-loop** para mejoras

## 🔧 Variables de Entorno Necesarias

```bash
# .env.example
# Base de Datos
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Email (ya existente)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password

# Twilio (ya existente)
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# Configuración del sistema
LOG_LEVEL=INFO
EMBEDDING_DIMENSION=1536
MAX_FAQ_RESULTS=5
```

## 📦 Nuevas Dependencias

```txt
# Agregar a requirements.txt
langchain>=0.1.0
langgraph>=0.0.40
openai>=1.0.0
pgvector>=0.2.0
numpy>=1.24.0
sentence-transformers>=2.2.0
tiktoken>=0.5.0
```

## 🚀 Cronograma de Desarrollo

### **Fase 1: Infraestructura Base (2-3 días)**

1. **Día 1**:

   - Instalar dependencias LangGraph + LangChain + OpenAI
   - Crear modelos de BD nuevos (FAQEmbedding, WizardSession)
   - Configurar PGVector en PostgreSQL
   - Crear archivo `.env.example`

2. **Día 2**:

   - Implementar estructura base de agentes (`app/agents/`)
   - Crear estado compartido para LangGraph (`app/graph/state.py`)
   - Implementar servicio de embeddings (`app/services/embedding_service.py`)

3. **Día 3**:
   - Crear grafo principal LangGraph (`app/graph/workflow.py`)
   - Implementar Agente Supervisor básico
   - Integrar con WebSocket handler existente

### **Fase 2: Agente FAQ (2 días)**

4. **Día 4**:

   - Implementar servicio de embeddings para FAQ
   - Crear script para poblar tabla `faq_embeddings` con datos proporcionados
   - Implementar Agente FAQ con búsqueda vectorial

5. **Día 5**:
   - Testing del Agente FAQ
   - Optimización de búsqueda semántica
   - Integración con grafo principal

### **Fase 3: Agente Wizard (3-4 días)**

6. **Día 6**:

   - Implementar lógica base del Wizard
   - Crear sistema de preguntas secuenciales (1-11)
   - Integrar validaciones existentes (`utils/validators.py`)

7. **Día 7**:

   - Implementar persistencia de sesión del Wizard
   - Crear comandos "volver" y "cancelar"
   - Human-in-the-loop para confirmaciones

8. **Día 8**:

   - Implementar preguntas evaluativas (12-20)
   - Integrar contexto de rúbrica en prompts
   - Sistema de evaluación IA con iteración

9. **Día 9**:
   - Testing completo del flujo Wizard
   - Optimización de prompts y evaluaciones
   - Manejo de casos edge

### **Fase 4: Integración y Testing (2 días)**

10. **Día 10**:

    - Integración completa de todos los agentes
    - Testing end-to-end del sistema
    - Optimización de performance

11. **Día 11**:
    - Testing de casos límite y errores
    - Documentación de APIs
    - Deployment y configuración final

## 🔍 Criterios de Aceptación

### Funcionalidades Core:

- ✅ Usuario puede iniciar conversación y ser ruteado correctamente
- ✅ FAQ responde preguntas usando base vectorial
- ✅ Wizard guía proceso completo de postulación (20 preguntas)
- ✅ Validaciones funcionan correctamente (email, teléfono, cédula)
- ✅ Human-in-the-loop permite volver/cancelar/confirmar
- ✅ IA evalúa respuestas con criterios de rúbrica
- ✅ Persistencia funciona solo con email proporcionado
- ✅ Sistema maneja desconexiones y reconexiones

### Performance:

- ⚡ Respuesta FAQ < 3 segundos
- ⚡ Evaluación de pregunta wizard < 5 segundos
- ⚡ Búsqueda vectorial < 2 segundos

### Robustez:

- 🛡️ Manejo de errores sin crash del sistema
- 🛡️ Validación de todos los inputs del usuario
- 🛡️ Logging completo para debugging
- 🛡️ Rate limiting para prevenir spam

## 📋 Notas de Implementación

1. **Prompts del Wizard**: Incluir contexto de rúbrica específica para cada pregunta evaluativa
2. **Embeddings**: Usar OpenAI text-embedding-3-small para consistencia
3. **Persistencia**: Implementar auto-save cada respuesta válida
4. **Error Handling**: Graceful degradation si OpenAI falla
5. **Logging**: Registrar todas las interacciones para análisis posterior

---

**Este plan está listo para implementación. ¿Apruebas el plan para proceder con el desarrollo?**
