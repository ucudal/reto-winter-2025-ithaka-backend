"""
Ejecutar la versión completa del Discord Bot (con privileged intents)

Este script ejecuta la versión completa del bot que requiere privileged intents
habilitados en el Discord Developer Portal.
"""

import sys
import logging
from pathlib import Path

# Agregar el directorio raíz al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.discord_bot.bot import run_bot
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
    """Función principal para ejecutar la versión completa del bot."""
    logger.info("=== INICIANDO ITHAKA DISCORD BOT (VERSIÓN COMPLETA) ===")
    
    # Verificar configuración
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN no está configurado en las variables de entorno")
        logger.error("Por favor, configura el token en el archivo .env")
        sys.exit(1)
    
    logger.info("⚠️  ATENCIÓN: Esta versión requiere privileged intents habilitados")
    logger.info("📋 Verifica que hayas habilitado 'Message Content Intent' en:")
    logger.info("   https://discord.com/developers/applications/")
    logger.info("")
    logger.info("🔄 Si tienes errores de intents, usa: python app/discord_bot/main.py")
    logger.info("   (versión básica sin privileged intents)")
    logger.info("")
    
    try:
        # Ejecutar el bot completo
        run_bot()
    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario")
    except Exception as e:
        if "privileged intents" in str(e):
            logger.error("❌ ERROR: Privileged intents no habilitados")
            logger.error("")
            logger.error("🔧 SOLUCIÓN:")
            logger.error("1. Ve a https://discord.com/developers/applications/")
            logger.error("2. Selecciona tu aplicación")
            logger.error("3. Ve a la sección 'Bot'")
            logger.error("4. Habilita 'MESSAGE CONTENT INTENT'")
            logger.error("5. Guarda los cambios y reinicia el bot")
            logger.error("")
            logger.error("💡 ALTERNATIVA: Usa la versión básica:")
            logger.error("   python app/discord_bot/main.py")
        else:
            logger.error(f"Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
