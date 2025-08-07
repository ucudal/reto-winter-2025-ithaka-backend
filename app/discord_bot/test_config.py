"""
Script de prueba para verificar la configuración del Discord Bot

Este script verifica que la configuración esté correcta antes de ejecutar el bot.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_configuration():
    """Prueba la configuración del bot."""
    print("🔍 Verificando configuración del Discord Bot...")
    
    # Test 1: Variables de entorno
    print("\n1. Verificando variables de entorno...")
    try:
        from app.discord_bot.config import DISCORD_TOKEN, COMMAND_PREFIX
        
        if DISCORD_TOKEN:
            print(f"   ✅ DISCORD_TOKEN: Configurado (longitud: {len(DISCORD_TOKEN)})")
        else:
            print("   ❌ DISCORD_TOKEN: No configurado")
            return False
            
        print(f"   ✅ COMMAND_PREFIX: {COMMAND_PREFIX}")
        
    except Exception as e:
        print(f"   ❌ Error cargando configuración: {e}")
        return False
    
    # Test 2: Importar módulos
    print("\n2. Verificando módulos...")
    try:
        import discord
        print(f"   ✅ discord.py: {discord.__version__}")
        
        from app.discord_bot.bot import IthakaBot
        print("   ✅ IthakaBot: Importado correctamente")
        
        from app.discord_bot.responses import get_contextual_response
        print("   ✅ Módulo de respuestas: Importado correctamente")
        
    except Exception as e:
        print(f"   ❌ Error importando módulos: {e}")
        return False
    
    # Test 3: Respuestas básicas
    print("\n3. Verificando sistema de respuestas...")
    try:
        response = get_contextual_response("hola")
        print(f"   ✅ Respuesta de prueba: {response[:50]}...")
        
    except Exception as e:
        print(f"   ❌ Error en sistema de respuestas: {e}")
        return False
    
    # Test 4: Instanciar bot (sin conectar)
    print("\n4. Verificando instancia del bot...")
    try:
        bot = IthakaBot()
        print(f"   ✅ Bot instanciado: {bot.__class__.__name__}")
        print(f"   ✅ Prefijo de comandos: {bot.command_prefix}")
        
    except Exception as e:
        print(f"   ❌ Error instanciando bot: {e}")
        return False
    
    print("\n✅ Todas las verificaciones pasaron correctamente!")
    print("\n📋 Información del bot:")
    print(f"   • Prefijo de comandos: {COMMAND_PREFIX}")
    print(f"   • Token configurado: {'Sí' if DISCORD_TOKEN else 'No'}")
    print(f"   • Version discord.py: {discord.__version__}")
    
    print("\n🚀 El bot está listo para ejecutarse!")
    print("   Para ejecutar: python app/discord_bot/main.py")
    
    return True

def test_token_validity():
    """Prueba si el token es válido (sin conectar)."""
    print("\n🔑 Verificando formato del token...")
    
    from app.discord_bot.config import DISCORD_TOKEN
    
    if not DISCORD_TOKEN:
        print("   ❌ Token no configurado")
        return False
    
    # Verificar formato básico del token
    parts = DISCORD_TOKEN.split('.')
    if len(parts) != 3:
        print("   ⚠️  Formato de token inválido (debe tener 3 partes separadas por puntos)")
        return False
    
    print("   ✅ Formato de token parece válido")
    print("   ℹ️  Para verificar completamente, ejecuta el bot y verifica la conexión")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 VERIFICACIÓN DE CONFIGURACIÓN - ITHAKA DISCORD BOT")
    print("=" * 60)
    
    success = test_configuration()
    
    if success:
        test_token_validity()
        print("\n" + "=" * 60)
        print("✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        
        print("\n📖 Próximos pasos:")
        print("1. Invita el bot a tu servidor de Discord")
        print("2. Ejecuta: python app/discord_bot/main.py")
        print("3. Prueba los comandos en Discord")
        
    else:
        print("\n" + "=" * 60)
        print("❌ CONFIGURACIÓN INCOMPLETA")
        print("=" * 60)
        print("\n🔧 Por favor, revisa los errores anteriores y:")
        print("1. Configura DISCORD_TOKEN en el archivo .env")
        print("2. Verifica que todas las dependencias estén instaladas")
        print("3. Vuelve a ejecutar este script")
