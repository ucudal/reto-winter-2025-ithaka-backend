"""
Discord Bot Principal para Ithaka

Este módulo contiene la implementación principal del bot de Discord.
Maneja eventos, comandos y respuestas automáticas.
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

class IthakaBot(commands.Bot):
    """
    Bot de Discord personalizado para el proyecto Ithaka.
    """
    
    def __init__(self):
        # Configurar intents básicos sin privileged intents
        intents = discord.Intents.default()
        intents.message_content = True  # Privileged intent - necesario para leer mensajes
        intents.members = False  # Deshabilitar para evitar privileged intent
        intents.presences = False  # Deshabilitar para evitar privileged intent
        
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
    
    async def on_member_join(self, member):
        """Evento que se ejecuta cuando un nuevo miembro se une al servidor."""
        # Crear mensaje directo de bienvenida
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
            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            
            await member.send(embed=embed)
            logger.info(f"Mensaje de bienvenida enviado a {member.name}")
        except discord.Forbidden:
            # El usuario tiene los DMs deshabilitados
            logger.warning(f"No se pudo enviar DM a {member.name}")
    
    async def on_message(self, message):
        """Evento que se ejecuta cuando se recibe un mensaje."""
        # Ignorar mensajes del propio bot
        if message.author == self.user:
            return
        
        # Procesar comandos primero
        await self.process_commands(message)
        
        # Si el mensaje menciona al bot o es un DM, responder automáticamente
        if self.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
            # Remover la mención del bot del mensaje
            content = message.content.replace(f'<@{self.user.id}>', '').strip()
            
            # Obtener respuesta contextual
            response = get_contextual_response(content)
            
            # Crear embed para la respuesta
            embed = discord.Embed(
                description=response,
                color=discord.Color.green()
            )
            embed.set_footer(text=f"{BOT_NAME} • Versión básica")
            
            await message.reply(embed=embed)
            logger.info(f"Respuesta automática enviada a {message.author.name}")
    
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

# Instancia global del bot
bot = IthakaBot()

# Comandos del bot
@bot.command(name='ping', help='Verifica si el bot está respondiendo')
async def ping(ctx):
    """Comando para verificar la latencia del bot."""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latencia: {latency}ms",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='info', help='Información sobre el bot y el proyecto Ithaka')
async def info(ctx):
    """Comando que muestra información sobre el bot."""
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
    embed.set_footer(text="Desarrollado para el proyecto Ithaka")
    await ctx.send(embed=embed)

@bot.command(name='ask', help='Haz una pregunta al bot')
async def ask(ctx, *, question):
    """Comando para hacer preguntas al bot."""
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

@bot.command(name='status', help='Muestra el estado del bot')
async def status(ctx):
    """Comando que muestra el estado del bot."""
    guild_count = len(bot.guilds)
    user_count = sum(guild.member_count for guild in bot.guilds)
    
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
    
    await ctx.send(embed=embed)

def run_bot():
    """Función para ejecutar el bot."""
    try:
        logger.info("Iniciando Discord Bot...")
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Error al ejecutar el bot: {e}")
        raise

if __name__ == "__main__":
    run_bot()
