"""
Instrucciones de implementación del Discord Bot para Ithaka

Este documento contiene instrucciones paso a paso para implementar y usar el bot de Discord.
"""

# GUÍA DE IMPLEMENTACIÓN - DISCORD BOT ITHAKA

## ✅ Estado Actual

El bot de Discord ha sido implementado exitosamente con las siguientes características:

### 🚀 Funcionalidades Implementadas
- ✅ **Bot básico funcional** con respuestas hardcodeadas
- ✅ **Comandos disponibles**: `!ping`, `!info`, `!ask`, `!status`, `!help`
- ✅ **Respuestas automáticas** a menciones y mensajes directos
- ✅ **Sistema de FAQ** integrado con respuestas predefinidas
- ✅ **Mensajes de bienvenida** para nuevos miembros
- ✅ **Manejo de errores** robusto
- ✅ **Logging completo** para monitoreo
- ✅ **Embeds de Discord** para respuestas visualmente atractivas

### 🔮 Preparado para el Futuro
- 🔮 **Interface para agentes IA** completamente definida
- 🔮 **Arquitectura modular** para fácil extensión
- 🔮 **Sistema de respuestas inteligentes** listo para conectar
- 🔮 **Análisis de contexto** preparado para implementar

## 📁 Estructura del Proyecto

```
app/discord_bot/
├── __init__.py              # Módulo principal
├── main.py                  # Punto de entrada
├── bot.py                   # Lógica principal del bot
├── config.py                # Configuración y variables de entorno
├── responses.py             # Respuestas hardcodeadas y FAQ
├── ai_integration.py        # Interface para futura integración IA
├── utils.py                 # Utilidades y helpers
├── test_config.py          # Script de verificación
└── README.md               # Documentación específica
```

## 🛠️ Configuración Completada

### Variables de Entorno (`.env`)
```env
# Discord Bot Configuration
DISCORD_TOKEN=
COMMAND_PREFIX=!
```

### Dependencias Instaladas
- ✅ `discord.py==2.5.2`
- ✅ `python-dotenv` (ya estaba)
- ✅ Todas las dependencias del proyecto principal

## 🚀 Cómo Ejecutar el Bot

### Método 1: Ejecución Directa
```bash
cd /Users/erik/Desktop/reto-winter-2025-ithaka-backend
source .venv/bin/activate
python app/discord_bot/main.py
```

### Método 2: Como Módulo
```bash
cd /Users/erik/Desktop/reto-winter-2025-ithaka-backend
source .venv/bin/activate
python -m app.discord_bot.main
```

### Verificar Configuración Antes de Ejecutar
```bash
python app/discord_bot/test_config.py
```

## 🎮 Comandos Disponibles

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `!ping` | Verifica latencia del bot | `!ping` |
| `!info` | Información del bot y proyecto | `!info` |
| `!ask <pregunta>` | Hace una pregunta al bot | `!ask qué es ithaka` |
| `!status` | Estado del bot y estadísticas | `!status` |
| `!help` | Lista todos los comandos | `!help` |

## 💬 Interacciones Automáticas

El bot responde automáticamente a:
- **Menciones**: `@IthakaBot hola`
- **Mensajes directos**: Cualquier DM al bot
- **Patrones específicos**: Saludos, despedidas, preguntas sobre tecnología

## 📊 Respuestas Hardcodeadas Implementadas

### Categorías de Respuestas:
1. **Saludos**: Respuestas amigables de bienvenida
2. **Información de Ithaka**: Datos sobre el proyecto
3. **Respuestas técnicas**: Información sobre la tecnología
4. **FAQ**: Preguntas frecuentes predefinidas
5. **Despedidas**: Mensajes de cierre
6. **Fallback**: Respuestas cuando no entiende la pregunta

### FAQ Incluidas:
- "qué es ithaka"
- "cómo funciona"
- "tecnología"
- "contacto"
- "características"

## 🔧 Mantenimiento y Logs

### Archivos de Log
- **Consola**: Logs en tiempo real
- **discord_bot.log**: Archivo de log persistente

### Niveles de Logging
- `INFO`: Eventos normales (conexiones, comandos)
- `WARNING`: Situaciones a revisar
- `ERROR`: Errores que requieren atención

## 🔮 Próximos Pasos para Integración IA

### 1. Cuando los Agentes IA estén Listos:

**En `ai_integration.py`:**
```python
# Implementar las funciones placeholder:
async def process_question(self, question: str, context: Dict) -> str:
    # Conectar con agentes IA reales
    pass

async def get_faq_response(self, query: str) -> str:
    # Usar búsqueda vectorial
    pass
```

**En `bot.py`:**
```python
# Reemplazar respuestas hardcodeadas con IA:
from app.discord_bot.ai_integration import get_smart_response

response = await get_smart_response(content, str(message.author.id))
```

### 2. Habilitar Integración:
```python
from app.discord_bot.ai_integration import discord_ai
discord_ai.enable_ai_integration()
```

## 🧪 Testing

### Verificar Configuración:
```bash
python app/discord_bot/test_config.py
```

### Probar Bot en Discord:
1. Invitar bot al servidor
2. Usar comando `!ping` para verificar conexión
3. Probar `!info` y `!ask` para verificar respuestas
4. Mencionar el bot en un canal

## 📝 Personalización

### Agregar Nuevas Respuestas:
**En `responses.py`:**
```python
FAQS = {
    "nueva_pregunta": "nueva respuesta",
    # ...
}
```

### Agregar Nuevos Comandos:
**En `bot.py`:**
```python
@bot.command(name='nuevo_comando', help='Descripción')
async def nuevo_comando(ctx):
    await ctx.send("Respuesta")
```

## 🛡️ Seguridad y Permisos

### Permisos Mínimos Requeridos:
- Send Messages
- Read Message History
- Use Slash Commands
- Embed Links
- Add Reactions

### Configuración de Seguridad:
- ✅ Validación de mensajes
- ✅ Prevención de recursión infinita
- ✅ Manejo seguro de errores
- ✅ Logs de actividad

## 📞 Soporte y Troubleshooting

### Problemas Comunes:

1. **Bot no se conecta**:
   - Verificar DISCORD_TOKEN en .env
   - Confirmar que el token sea válido

2. **Bot no responde**:
   - Verificar permisos en Discord
   - Confirmar "Message Content Intent" habilitado

3. **Errores de comando**:
   - Verificar prefijo de comandos
   - Revisar logs para detalles

### Logs para Debugging:
```bash
tail -f discord_bot.log
```

## ✅ Checklist de Implementación

- [x] Bot básico implementado
- [x] Configuración completada
- [x] Dependencias instaladas
- [x] Sistema de respuestas hardcodeadas
- [x] Comandos básicos funcionando
- [x] Manejo de errores implementado
- [x] Logging configurado
- [x] Interface para IA preparada
- [x] Documentación completa
- [x] Scripts de verificación
- [x] Estructura modular lista

## 🎯 Estado Final

**El bot de Discord está completamente implementado y listo para usar.**

**Funciona de forma independiente con respuestas hardcodeadas y está arquitectónicamente preparado para la integración futura con agentes IA sin necesidad de refactoring mayor.**

**Para ejecutar inmediatamente:**
```bash
cd /Users/erik/Desktop/reto-winter-2025-ithaka-backend
source .venv/bin/activate
python app/discord_bot/main.py
```
