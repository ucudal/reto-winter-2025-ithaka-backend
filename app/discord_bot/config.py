"""
Configuración del Discord Bot

Este módulo contiene la configuración necesaria para el bot de Discord.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Token del bot de Discord (OBLIGATORIO)
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Prefijo de comandos (por defecto: !)
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')

# Validar configuración crítica
if not DISCORD_TOKEN:
    raise ValueError(
        "DISCORD_TOKEN no está configurado. "
        "Por favor, configura el token en el archivo .env"
    )

# Configuración del bot
BOT_NAME = "Ithaka Bot"
BOT_DESCRIPTION = "Bot de Discord para el proyecto Ithaka"
BOT_VERSION = "1.0.0"
