"""
Configuración alternativa del Discord Bot sin privileged intents

Esta versión del bot funciona sin requerir privileged intents habilitados
en el Discord Developer Portal.
"""

import logging
import discord
from discord.ext import commands

from app.discord_bot.config import (
    DISCORD_TOKEN, 
    COMMAND_PREFIX, 
    BOT_NAME, 
    BOT_DESCRIPTION
)
from app.discord_bot.responses import get_contextual_response, get_random_response, GREETINGS

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IthakaBotBasic(commands.Bot):
    """
    Bot de Discord básico sin privileged intents.
    
    Esta versión funciona sin necesidad de configurar intents especiales
    en el Discord Developer Portal.
    """
    
    def __init__(self):
        # Configurar intents básicos sin privileged intents
        intents = discord.Intents.default()
        # NO configurar message_content = True para evitar privileged intent
        
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            description=BOT_DESCRIPTION,
            intents=intents
        )
        
    async def on_ready(self):
        """Evento que se ejecuta cuando el bot está listo."""
        logger.info(f'{self.user.name} se ha conectado a Discord!')
        logger.info(f'Bot ID: {self.user.id}')
        logger.info(f'Servidores conectados: {len(self.guilds)}')
        
        # Cambiar el estado del bot
        activity = discord.Game(name="Ayudando con Ithaka")
        await self.change_presence(status=discord.Status.online, activity=activity)
        
        logger.info("🤖 Bot listo para recibir comandos!")
        logger.info("⚠️  NOTA: Para leer contenido de mensajes, habilita 'Message Content Intent' en Discord Developer Portal")
    
    async def on_member_join(self, member):
        """Evento que se ejecuta cuando un nuevo miembro se une al servidor."""
        try:
            embed = discord.Embed(
                title="¡Bienvenido/a al servidor!",
                description=f"Hola {member.mention}, {get_random_response(GREETINGS)}",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="¿Cómo empezar?",
                value=f"Usa `{COMMAND_PREFIX}help` para ver todos los comandos disponibles.",
                inline=False
            )
            
            # Intentar enviar DM, si falla, enviar en canal general
            try:
                await member.send(embed=embed)
                logger.info(f"Mensaje de bienvenida enviado por DM a {member.name}")
            except discord.Forbidden:
                # Si no se puede enviar DM, intentar enviar en canal general
                if member.guild.system_channel:
                    await member.guild.system_channel.send(embed=embed)
                    logger.info(f"Mensaje de bienvenida enviado en canal general para {member.name}")
                else:
                    logger.warning(f"No se pudo enviar mensaje de bienvenida a {member.name}")
                    
        except Exception as e:
            logger.error(f"Error enviando mensaje de bienvenida: {e}")
    
    async def on_message(self, message):
        """Evento que se ejecuta cuando se recibe un mensaje."""
        # Log de todos los mensajes para debugging
        logger.info(f"📨 Mensaje recibido de {message.author.name}: '{message.content}'")
        logger.info(f"   Canal: {message.channel.name if hasattr(message.channel, 'name') else 'DM'}")
        logger.info(f"   Es bot: {message.author.bot}")
        logger.info(f"   Es del bot: {message.author == self.user}")
        
        # Ignorar mensajes del propio bot
        if message.author == self.user:
            logger.info("   ⏭️  Ignorando mensaje del propio bot")
            return
        
        # Log antes de procesar comandos
        logger.info("   🔍 Procesando comandos...")
        
        # Procesar comandos primero
        await self.process_commands(message)
        
        # Solo responder si el bot es mencionado directamente o es un DM
        # (ya que no podemos leer el contenido completo sin privileged intents)
        if self.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
            logger.info("   💬 Bot mencionado o DM detectado")
            try:
                # Sin privileged intents, el contenido puede estar vacío
                # Así que usamos una respuesta genérica amigable
                response = get_random_response(GREETINGS)
                
                embed = discord.Embed(
                    description=f"{response}\n\nUsa `{COMMAND_PREFIX}help` para ver mis comandos disponibles.",
                    color=discord.Color.green()
                )
                embed.set_footer(text=f"{BOT_NAME} • Versión básica")
                
                await message.reply(embed=embed)
                logger.info(f"   ✅ Respuesta automática enviada a {message.author.name}")
                
            except Exception as e:
                logger.error(f"   ❌ Error respondiendo a mensaje: {e}")
        else:
            logger.info("   ⏭️  No es mención ni DM, no respondiendo automáticamente")
    
    async def on_command_error(self, ctx, error):
        """Manejo de errores de comandos."""
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(
                title="Comando no encontrado",
                description=f"No reconozco ese comando. Usa `{COMMAND_PREFIX}help` para ver los comandos disponibles.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Argumento faltante",
                description=f"Faltan argumentos para este comando. Usa `{COMMAND_PREFIX}help {ctx.command}` para más información.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        else:
            logger.error(f"Error en comando: {error}")
            embed = discord.Embed(
                title="Error",
                description="Ocurrió un error inesperado. Por favor, inténtalo de nuevo.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

# Instancia del bot básico
bot_basic = IthakaBotBasic()

# Comandos del bot (mismos que la versión completa)
@bot_basic.command(name='ping', help='Verifica si el bot está respondiendo')
async def ping(ctx):
    """Comando para verificar la latencia del bot."""
    logger.info(f"🏓 Comando PING ejecutado por {ctx.author.name}")
    latency = round(bot_basic.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latencia: {latency}ms",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)
    logger.info(f"✅ Respuesta PING enviada a {ctx.author.name}")

@bot_basic.command(name='info', help='Información sobre el bot y el proyecto Ithaka')
async def info(ctx):
    """Comando que muestra información sobre el bot."""
    logger.info(f"ℹ️ Comando INFO ejecutado por {ctx.author.name}")
    embed = discord.Embed(
        title=f"ℹ️ {BOT_NAME}",
        description=BOT_DESCRIPTION,
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🔧 Tecnología",
        value="Python, discord.py, FastAPI, PostgreSQL",
        inline=True
    )
    embed.add_field(
        name="🌐 Proyecto",
        value="Ithaka - Educación con IA",
        inline=True
    )
    embed.add_field(
        name="📞 Soporte",
        value=f"Usa `{COMMAND_PREFIX}help` para más comandos",
        inline=False
    )
    embed.add_field(
        name="⚠️ Configuración",
        value="Para funcionalidad completa, habilita 'Message Content Intent' en Discord Developer Portal",
        inline=False
    )
    embed.set_footer(text="Desarrollado para el proyecto Ithaka")
    await ctx.send(embed=embed)
    logger.info(f"✅ Respuesta INFO enviada a {ctx.author.name}")

@bot_basic.command(name='ask', help='Haz una pregunta al bot')
async def ask(ctx, *, question=None):
    """Comando para hacer preguntas al bot."""
    if question is None:
        embed = discord.Embed(
            title="❓ Pregunta requerida",
            description=f"Por favor, proporciona una pregunta. Ejemplo: `{COMMAND_PREFIX}ask qué es ithaka`",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return
    
    response = get_contextual_response(question)
    
    embed = discord.Embed(
        title="🤖 Respuesta",
        description=response,
        color=discord.Color.purple()
    )
    embed.add_field(
        name="❓ Tu pregunta",
        value=question,
        inline=False
    )
    embed.set_footer(text="💡 En el futuro, estaré conectado a agentes IA más avanzados")
    
    await ctx.send(embed=embed)

@bot_basic.command(name='status', help='Muestra el estado del bot')
async def status(ctx):
    """Comando que muestra el estado del bot."""
    guild_count = len(bot_basic.guilds)
    user_count = sum(guild.member_count for guild in bot_basic.guilds)
    
    embed = discord.Embed(
        title="📊 Estado del Bot",
        color=discord.Color.green()
    )
    embed.add_field(name="🏠 Servidores", value=guild_count, inline=True)
    embed.add_field(name="👥 Usuarios", value=user_count, inline=True)
    embed.add_field(name="📡 Estado", value="🟢 En línea", inline=True)
    embed.add_field(
        name="🔮 Funcionalidades futuras",
        value="• Integración con agentes IA\n• Respuestas más inteligentes\n• Análisis de contexto avanzado",
        inline=False
    )
    embed.add_field(
        name="⚙️ Configuración",
        value="Modo básico (sin privileged intents)",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot_basic.command(name='setup', help='Información sobre configuración avanzada')
async def setup(ctx):
    """Comando que explica cómo configurar privileged intents."""
    embed = discord.Embed(
        title="⚙️ Configuración Avanzada",
        description="Para habilitar todas las funcionalidades del bot:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="1. Discord Developer Portal",
        value="Ve a https://discord.com/developers/applications/",
        inline=False
    )
    embed.add_field(
        name="2. Selecciona tu aplicación",
        value="Encuentra tu bot en la lista de aplicaciones",
        inline=False
    )
    embed.add_field(
        name="3. Ve a la sección Bot",
        value="En el menú lateral, selecciona 'Bot'",
        inline=False
    )
    embed.add_field(
        name="4. Habilitar Privileged Gateway Intents",
        value="• ✅ MESSAGE CONTENT INTENT\n• ⬜ SERVER MEMBERS INTENT (opcional)\n• ⬜ PRESENCE INTENT (opcional)",
        inline=False
    )
    embed.add_field(
        name="5. Reiniciar el bot",
        value="Guarda los cambios y reinicia el bot",
        inline=False
    )
    embed.set_footer(text="Con privileged intents, el bot podrá leer mensajes completos y responder de forma más inteligente")
    
    await ctx.send(embed=embed)

def run_basic_bot():
    """Función para ejecutar la versión básica del bot."""
    try:
        logger.info("Iniciando Discord Bot (versión básica)...")
        logger.info("⚠️  Ejecutando sin privileged intents")
        logger.info("💡 Para funcionalidad completa, usar bot.py después de configurar intents")
        bot_basic.run(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Error al ejecutar el bot: {e}")
        raise

if __name__ == "__main__":
    run_basic_bot()
