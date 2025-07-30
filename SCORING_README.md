
# Sistema de Scoring de Postulaciones

Este sistema permite evaluar automáticamente las postulaciones de los candidatos basándose en el texto de sus respuestas abiertas. **Ahora incluye dos motores de evaluación: uno basado en reglas y otro con IA.**

## Características

- **Evaluación automática**: Analiza textos y asigna scores en tres dimensiones
- **Dos motores de evaluación**: Reglas predefinidas o IA (OpenAI GPT)
- **API REST**: Endpoints para evaluar textos y procesar postulaciones
- **Base de datos**: Almacena y actualiza scores en la base de datos
- **Análisis inteligente**: La IA proporciona análisis detallado de cada postulación

## Motores de Evaluación

### 1. Motor de Reglas (Predeterminado)
- **Algoritmo predefinido**: Basado en palabras clave, longitud, conectores
- **Ventajas**: Rápido, sin costos, consistente
- **Desventajas**: Menos sofisticado, no entiende contexto

### 2. Motor de IA (OpenAI GPT)
- **Análisis inteligente**: Usa GPT-3.5-turbo para evaluación contextual
- **Ventajas**: Más preciso, entiende matices, proporciona análisis
- **Desventajas**: Requiere API key, tiene costo por uso

## Dimensiones de Evaluación

### 1. Creatividad (40% del score total)
- **Vocabulario variado**: Diversidad de palabras utilizadas
- **Desarrollo de ideas**: Longitud y profundidad del texto
- **Palabras creativas**: Uso de términos relacionados con innovación

### 2. Claridad (30% del score total)
- **Estructura**: Uso de conectores y puntuación
- **Coherencia**: Organización lógica del texto
- **Longitud apropiada**: Balance entre detalle y concisión

### 3. Compromiso (30% del score total)
- **Motivación**: Expresiones de interés y pasión
- **Planificación**: Referencias a objetivos y metas futuras
- **Dedicación**: Palabras relacionadas con esfuerzo y constancia

## Estructura del Proyecto

```
app/
├── services/
│   ├── scoring_service.py      # Servicio principal de scoring
│   ├── score_engine.py         # Motor de evaluación con reglas
│   └── ai_score_engine.py     # Motor de evaluación con IA
├── api/v1/
│   └── scoring.py             # Endpoints de la API
└── db/
    └── models.py              # Modelo Postulation
```

## Configuración

### 1. Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL=postgresql+asyncpg://usuario:password@localhost/dbname
OPENAI_API_KEY=tu_api_key_de_openai
```

### 2. Instalación de Dependencias
```bash
pip install -r requirements.txt
```

## Uso

### 1. Evaluación de Texto Individual

#### Con Motor de Reglas
```python
from app.services.score_engine import evaluar_postulacion

texto = "Me apasiona la tecnología y quiero innovar..."
scores = evaluar_postulacion(texto)
```

#### Con Motor de IA
```python
from app.services.ai_score_engine import evaluar_postulacion_ai

texto = "Me apasiona la tecnología y quiero innovar..."
scores = await evaluar_postulacion_ai(texto)
# Incluye análisis detallado en scores['analisis']
```

### 2. Procesamiento de Postulaciones en Base de Datos

```python
from app.services.scoring_service import procesar_postulaciones

# Procesa con motor de reglas
await procesar_postulaciones(use_ai=False)

# Procesa con motor de IA
await procesar_postulaciones(use_ai=True)
```

### 3. API Endpoints

#### Evaluar texto
```bash
# Con motor de reglas
POST /api/v1/scoring/evaluate
{
    "texto": "Texto a evaluar...",
    "use_ai": false
}

# Con motor de IA
POST /api/v1/scoring/evaluate
{
    "texto": "Texto a evaluar...",
    "use_ai": true
}
```

#### Procesar todas las postulaciones
```bash
# Con motor de reglas
POST /api/v1/scoring/process-all?use_ai=false

# Con motor de IA
POST /api/v1/scoring/process-all?use_ai=true
```

#### Procesar postulación específica
```bash
# Con motor de reglas
POST /api/v1/scoring/process/123?use_ai=false

# Con motor de IA
POST /api/v1/scoring/process/123?use_ai=true
```

## Pruebas

### Prueba del Motor de Reglas
```bash
python test_scoring_simple.py
```

### Prueba del Motor de IA
```bash
python test_ai_scoring.py
```

### Prueba Completa del Sistema
```bash
python app/test_scoring.py
```

### Prueba de la API
1. Inicia el servidor: `uvicorn app.main:app --reload`
2. Visita: `http://localhost:8000/docs`

## Comparación de Motores

### Motor de Reglas
- ✅ **Rápido**: Sin latencia de red
- ✅ **Gratis**: Sin costos de API
- ✅ **Consistente**: Mismos resultados siempre
- ❌ **Limitado**: No entiende contexto complejo
- ❌ **Rígido**: Basado en palabras clave

### Motor de IA
- ✅ **Inteligente**: Entiende contexto y matices
- ✅ **Flexible**: Se adapta a diferentes estilos
- ✅ **Análisis**: Proporciona explicaciones detalladas
- ❌ **Costo**: Requiere API key y tiene costos
- ❌ **Latencia**: Tiempo de respuesta de la API

## Ejemplos de Respuestas

### Motor de Reglas
```json
{
    "creatividad": 75,
    "claridad": 80,
    "compromiso": 85,
    "score_total": 79.5
}
```

### Motor de IA
```json
{
    "creatividad": 82,
    "claridad": 78,
    "compromiso": 88,
    "score_total": 82.8,
    "analisis": "El candidato demuestra alta creatividad con vocabulario variado y conceptos innovadores. La claridad es buena con estructura coherente. Muestra fuerte compromiso con metas específicas y motivación genuina."
}
```

## Personalización

### Ajustar Pesos (Ambos Motores)
```python
# En score_engine.py o ai_score_engine.py
score_total = (creatividad * 0.4 + claridad * 0.3 + compromiso * 0.3)
```

### Personalizar Prompt de IA
```python
# En ai_score_engine.py
prompt = f"""
Analiza el siguiente texto de una postulación...
[Tu prompt personalizado aquí]
"""
```

### Agregar Nuevas Dimensiones
1. Modifica las funciones de evaluación
2. Actualiza los modelos de respuesta
3. Ajusta los pesos en el cálculo total

## Troubleshooting

### Error: "OPENAI_API_KEY not found"
- Verifica que tu archivo `.env` tenga la variable `OPENAI_API_KEY`
- El motor de IA usará evaluación de fallback

### Error: "Rate limit exceeded"
- El motor de IA tiene límites de uso
- Considera usar el motor de reglas para pruebas masivas

### Error: "Database connection failed"
- Verifica `DATABASE_URL` en tu archivo `.env`
- Asegúrate de que la base de datos esté corriendo