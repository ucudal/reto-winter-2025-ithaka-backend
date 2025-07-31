# 🤖 Sistema de Agentes IA - Ithaka Backend

Sistema completo de agentes conversacionales implementado con **LangGraph + LangChain** para manejar postulaciones emprendedoras, FAQs y validaciones.

## 🏗️ Arquitectura

### Agentes Implementados

1. **🎯 Supervisor** - Router inteligente que analiza intenciones
2. **📝 Wizard** - Formulario conversacional con 20 preguntas + human-in-the-loop
3. **❓ FAQ** - Responde consultas usando búsqueda vectorial (PGVector)
4. **✅ Validator** - Valida datos usando funciones existentes

### Tecnologías

- **LangGraph** - Orquestación de agentes
- **LangChain** - Framework de IA
- **OpenAI** - LLM y embeddings (gpt-4o-mini + text-embedding-3-small)
- **PGVector** - Búsqueda semántica de FAQs
- **PostgreSQL** - Persistencia

## 🚀 Instalación y Setup

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Copia `config/env.example` a `.env` y configura:

```bash
# Base de Datos
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Email y Twilio (existentes)
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
```

### 3. Ejecutar Setup Automático

```bash
python scripts/setup_system.py
```

Este script:

- ✅ Verifica variables de entorno
- ✅ Crea tablas de BD con PGVector
- ✅ Puebla FAQs con embeddings
- ✅ Ejecuta test del sistema

### 4. Iniciar Servidor

```bash
uvicorn app.main:app --reload
```

## 💬 Uso del Sistema

### WebSocket Endpoint

**URL:** `ws://localhost:8000/api/v1/ws/`

### Ejemplos de Mensajes

#### FAQ (Preguntas Frecuentes)

```json
{"content": "¿Qué es el programa Fellows?"}
{"content": "¿Cuánto cuestan los cursos?"}
{"content": "¿Cómo me entero de las convocatorias?"}
```

#### Wizard (Postulación)

```json
{"content": "Quiero postular mi idea"}
{"content": "Tengo un emprendimiento"}
{"content": "volver"}
{"content": "cancelar"}
```

### Flujo del Wizard

1. **Preguntas 1-11:** Datos personales obligatorios
2. **Pregunta 11:** ¿Tienes idea/emprendimiento?
   - **NO** → Registro básico completado
   - **SI** → Continúa con preguntas evaluativas
3. **Preguntas 12-20:** Evaluativas con IA + rúbrica

#### Comandos Especiales

- `"volver"` - Pregunta anterior
- `"cancelar"` - Terminar proceso
- `"continuar"` - Aceptar respuesta actual (en mejoras)

## 🗄️ Base de Datos

### Tablas Existentes (mantenidas)

- `conversations` - Conversaciones
- `messages` - Historial de mensajes
- `postulations` - Postulaciones completadas

### Nuevas Tablas

```sql
-- FAQs con embeddings vectoriales
CREATE TABLE faq_embeddings (
    id SERIAL PRIMARY KEY,
    question VARCHAR NOT NULL,
    answer TEXT NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sesiones del wizard
CREATE TABLE wizard_sessions (
    id SERIAL PRIMARY KEY,
    conv_id INTEGER REFERENCES conversations(id),
    current_question INTEGER DEFAULT 1,
    responses JSON DEFAULT '{}',
    state VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🧠 Sistema de Evaluación

### Rúbrica de Evaluación

Configurada en `app/config/rubrica.json`:

- **Preguntas evaluativas** - Criterios específicos por pregunta
- **Evaluación IA** - Score + feedback + sugerencias
- **Human-in-the-loop** - Usuario puede mejorar respuestas
- **Máximo 3 iteraciones** de mejora por pregunta

### Validaciones

Integra funciones existentes en `utils/validators.py`:

- ✅ Email (RFC 5322)
- ✅ Teléfono (8-12 dígitos)
- ✅ Cédula uruguaya (dígito verificador)
- ✅ Opciones predefinidas
- ✅ Longitud mínima de texto

## 📊 Arquitectura de Archivos

```
app/
├── agents/           # Agentes IA
│   ├── supervisor.py    # Router principal
│   ├── wizard.py        # Formulario conversacional
│   ├── faq.py          # FAQ con vectores
│   └── validator.py     # Validaciones
├── graph/           # LangGraph workflow
│   ├── state.py        # Estado compartido
│   └── workflow.py     # Orquestación
├── services/        # Servicios
│   ├── chat_service.py     # Servicio principal
│   ├── embedding_service.py # Embeddings
│   └── evaluation_service.py # Evaluación IA
├── config/          # Configuraciones
│   ├── rubrica.json    # Criterios evaluación
│   └── questions.py    # Preguntas wizard
└── db/models.py     # Modelos actualizados
```

## 🔧 Debugging y Logs

### Activar Logs Detallados

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Verificar Estado del Sistema

```python
from app.services.chat_service import chat_service

# Test básico
result = await chat_service.process_message("Hola")
print(result)
```

### Test de Componentes

```python
# Test FAQ
from app.agents.faq import faq_agent

# Test Wizard
from app.agents.wizard import wizard_agent

# Test Workflow completo
from app.graph.workflow import process_user_message
```

## ⚡ Performance

### Métricas Objetivo

- **FAQ Response:** < 3 segundos
- **Wizard Evaluation:** < 5 segundos
- **Vector Search:** < 2 segundos

### Optimizaciones

- Embeddings cacheados en BD
- Conexiones async a BD
- Límite de resultados vectoriales
- Fallbacks ante errores

## 🚨 Troubleshooting

### Error: "No module named 'langchain'"

```bash
pip install -r requirements.txt
```

### Error: "Extension vector does not exist"

```sql
CREATE EXTENSION vector;
```

### Error: "OpenAI API key not found"

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Error: "Database connection failed"

Verificar `DATABASE_URL` en `.env`

## 📈 Monitoreo

### Métricas Importantes

- Sesiones de wizard completadas vs canceladas
- Tiempo promedio por evaluación IA
- FAQs más consultadas
- Errores de validación más frecuentes

### Logs de Sistema

- Decisiones del supervisor
- Evaluaciones de respuestas
- Errores de conexión
- Performance de queries vectoriales

---

## 🎯 Próximos Pasos

1. **Dashboard Admin** - Interfaz para gestionar FAQs y rúbricas
2. **Métricas Avanzadas** - Analytics de uso del sistema
3. **A/B Testing** - Optimización de prompts y criterios
4. **Integración WhatsApp** - Usando infraestructura Twilio existente

---

**¿Preguntas?** Consulta el plan completo en `PLAN_DESARROLLO_AGENTES_IA.md`
