# Discord Bot - Ithaka

Bot de Discord básico para el proyecto Ithaka que responde preguntas con respuestas hardcodeadas y está preparado para integración futura con agentes IA.

## Características

### Funcionalidades Actuales
- ✅ Respuestas automáticas a menciones y mensajes directos
- ✅ Comandos básicos (`!ping`, `!info`, `!ask`, `!status`)
- ✅ Mensajes de bienvenida para nuevos miembros
- ✅ Respuestas contextuales hardcodeadas
- ✅ Sistema de FAQ básico
- ✅ Manejo de errores y logging

### Funcionalidades Futuras (Preparadas)
- 🔮 Integración con agentes IA
- 🔮 Respuestas inteligentes personalizadas
- 🔮 Análisis de sentimiento
- 🔮 Búsqueda vectorial en base de conocimiento
- 🔮 Contexto de conversación avanzado

## Configuración

### 1. Variables de Entorno

Configura las siguientes variables en tu archivo `.env`:

```env
# Token del bot de Discord (OBLIGATORIO)
DISCORD_TOKEN=tu_token_aqui

# Prefijo de comandos (opcional, por defecto: !)
COMMAND_PREFIX=!
```

### 2. Obtener Token de Discord

1. Ve a [Discord Developer Portal](https://discord.com/developers/applications)
2. Crea una nueva aplicación
3. Ve a la sección "Bot"
4. Crea un bot y copia el token
5. Habilita "Message Content Intent" en la sección de intents

### 3. Invitar el Bot a tu Servidor

1. En el Developer Portal, ve a "OAuth2" > "URL Generator"
2. Selecciona scope "bot"
3. Selecciona los permisos necesarios:
   - Send Messages
   - Read Message History
   - Use Slash Commands
   - Embed Links
   - Add Reactions
4. Usa la URL generada para invitar el bot

## Instalación

### Prerrequisitos
- Python 3.9+
- PostgreSQL (para funcionalidades futuras)
- Dependencias del proyecto

### Instalar Dependencias
```bash
pip install discord.py python-dotenv
```

O usando el archivo de requisitos del proyecto:
```bash
pip install -r requirements.txt
```

## Uso

### Ejecutar el Bot

Desde el directorio del proyecto:
```bash
python app/discord_bot/main.py
```

O desde el módulo:
```bash
python -m app.discord_bot.main
```

### Comandos Disponibles

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `!ping` | Verifica latencia del bot | `!ping` |
| `!info` | Información del bot y proyecto | `!info` |
| `!ask <pregunta>` | Hace una pregunta al bot | `!ask qué es ithaka` |
| `!status` | Estado del bot | `!status` |
| `!help` | Lista todos los comandos | `!help` |

### Interacción Automática

El bot responde automáticamente a:
- Menciones: `@IthakaBot hola`
- Mensajes directos
- Patrones específicos (saludos, despedidas, etc.)

## Estructura del Código

```
app/discord_bot/
├── __init__.py          # Módulo principal
├── main.py              # Punto de entrada
├── bot.py               # Lógica principal del bot
├── config.py            # Configuración
├── responses.py         # Respuestas hardcodeadas
├── ai_integration.py    # Interface para IA futura
└── README.md           # Este archivo
```

## Desarrollo

### Agregar Nuevas Respuestas

Edita `responses.py` para agregar nuevas respuestas hardcodeadas:

```python
# En FAQS dictionary
FAQS = {
    "nueva pregunta": "nueva respuesta",
    # ...
}
```

### Agregar Nuevos Comandos

En `bot.py`, agrega comandos usando el decorador:

```python
@bot.command(name='nuevo_comando', help='Descripción del comando')
async def nuevo_comando(ctx, argumento):
    # Lógica del comando
    await ctx.send("Respuesta")
```

### Preparación para IA

El archivo `ai_integration.py` contiene las interfaces preparadas para cuando se implementen los agentes IA. No requiere modificaciones hasta la integración.

## Logging

El bot genera logs en:
- Consola (nivel INFO)
- Archivo `discord_bot.log`

Niveles de logging:
- `INFO`: Eventos normales
- `WARNING`: Situaciones a tener en cuenta
- `ERROR`: Errores que requieren atención

## Troubleshooting

### Bot no se conecta
- Verifica que `DISCORD_TOKEN` esté configurado correctamente
- Revisa que el token sea válido en el Developer Portal
- Confirma que el bot esté habilitado

### Bot no responde a comandos
- Verifica el prefijo de comandos (`COMMAND_PREFIX`)
- Confirma que el bot tenga permisos para leer mensajes
- Revisa que "Message Content Intent" esté habilitado

### Errores de permisos
- Revisa los permisos del bot en el servidor
- Confirma que tenga permisos para enviar mensajes
- Verifica permisos para embeds y reacciones

## Integración Futura con IA

### Cuando esté listo:

1. Implementar las funciones en `ai_integration.py`
2. Conectar con los agentes del proyecto Ithaka
3. Habilitar la integración con `discord_ai.enable_ai_integration()`
4. Actualizar la lógica de respuestas en `bot.py`

### Interface preparada:

```python
# Usar respuesta de IA
response = await get_smart_response(message_content, user_id)
```

## Contribuir

1. Mantén el estilo de código consistente
2. Agrega logging apropiado
3. Documenta nuevas funcionalidades
4. Prueba thoroughly antes de hacer commit
5. Actualiza este README si es necesario

## Soporte

Para problemas específicos del bot de Discord:
1. Revisa los logs
2. Verifica la configuración
3. Consulta la documentación de discord.py
4. Reporta issues con detalles específicos
