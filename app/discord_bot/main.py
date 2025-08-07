"""
Punto de entrada principal para el Discord Bot

Este script permite ejecutar el bot de Discord de forma independiente
o como parte de la aplicación principal.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.discord_bot.bot_basic import run_basic_bot  # Versión sin privileged intents
from app.discord_bot.config import DISCORD_TOKEN

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('discord_bot.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Función principal para ejecutar el bot."""
    logger.info("=== INICIANDO ITHAKA DISCORD BOT ===")
    
    # Verificar configuración
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN no está configurado en las variables de entorno")
        logger.error("Por favor, configura el token en el archivo .env")
        sys.exit(1)
    
    try:
        # Ejecutar el bot (versión básica sin privileged intents)
        run_basic_bot()
    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
