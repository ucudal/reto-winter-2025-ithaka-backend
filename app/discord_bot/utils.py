"""
Utilidades para el Discord Bot

Este módulo contiene funciones de utilidad para el bot de Discord.
"""

import discord
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def create_embed(
    title: str = None,
    description: str = None,
    color: discord.Color = discord.Color.blue(),
    fields: List[Dict[str, Any]] = None,
    footer: str = None,
    thumbnail_url: str = None,
    image_url: str = None
) -> discord.Embed:
    """
    Crea un embed de Discord con los parámetros especificados.
    
    Args:
        title: Título del embed
        description: Descripción del embed
        color: Color del embed
        fields: Lista de campos {name, value, inline}
        footer: Texto del footer
        thumbnail_url: URL de la imagen thumbnail
        image_url: URL de la imagen principal
        
    Returns:
        discord.Embed configurado
    """
    embed = discord.Embed(color=color)
    
    if title:
        embed.title = title
    if description:
        embed.description = description
    if footer:
        embed.set_footer(text=footer)
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    if image_url:
        embed.set_image(url=image_url)
    
    if fields:
        for field in fields:
            embed.add_field(
                name=field.get("name", "Campo"),
                value=field.get("value", "Valor"),
                inline=field.get("inline", True)
            )
    
    return embed

def format_code_block(code: str, language: str = "python") -> str:
    """
    Formatea código en un bloque de código de Discord.
    
    Args:
        code: El código a formatear
        language: El lenguaje para syntax highlighting
        
    Returns:
        Código formateado para Discord
    """
    return f"```{language}\n{code}\n```"

def truncate_text(text: str, max_length: int = 2000) -> str:
    """
    Trunca texto para que no exceda los límites de Discord.
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima permitida
        
    Returns:
        Texto truncado si es necesario
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."

def parse_mentions(content: str, bot_id: int) -> str:
    """
    Limpia las menciones del contenido del mensaje.
    
    Args:
        content: Contenido del mensaje
        bot_id: ID del bot para remover su mención
        
    Returns:
        Contenido limpio sin menciones
    """
    # Remover mención del bot
    content = content.replace(f'<@{bot_id}>', '')
    content = content.replace(f'<@!{bot_id}>', '')
    
    # Limpiar espacios extra
    return content.strip()

def is_command_message(content: str, prefix: str) -> bool:
    """
    Verifica si un mensaje es un comando.
    
    Args:
        content: Contenido del mensaje
        prefix: Prefijo de comandos
        
    Returns:
        True si es un comando
    """
    return content.strip().startswith(prefix)

def get_user_permissions(member: discord.Member) -> List[str]:
    """
    Obtiene una lista de permisos de un miembro.
    
    Args:
        member: Miembro de Discord
        
    Returns:
        Lista de nombres de permisos
    """
    permissions = []
    
    if member.guild_permissions.administrator:
        permissions.append("Administrator")
    if member.guild_permissions.manage_guild:
        permissions.append("Manage Server")
    if member.guild_permissions.manage_channels:
        permissions.append("Manage Channels")
    if member.guild_permissions.manage_messages:
        permissions.append("Manage Messages")
    if member.guild_permissions.kick_members:
        permissions.append("Kick Members")
    if member.guild_permissions.ban_members:
        permissions.append("Ban Members")
    
    return permissions

def format_uptime(seconds: int) -> str:
    """
    Formatea tiempo de actividad en un formato legible.
    
    Args:
        seconds: Segundos de actividad
        
    Returns:
        Tiempo formateado (ej: "2d 3h 45m")
    """
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if not parts:  # Si es menos de un minuto
        parts.append(f"{seconds}s")
    
    return " ".join(parts)

class MessageValidator:
    """Validador para mensajes de Discord."""
    
    @staticmethod
    def is_valid_length(text: str, max_length: int = 2000) -> bool:
        """Verifica si el texto no excede la longitud máxima."""
        return len(text) <= max_length
    
    @staticmethod
    def contains_forbidden_content(text: str) -> bool:
        """Verifica si el texto contiene contenido prohibido."""
        forbidden_patterns = [
            "discord.gg/",  # Enlaces de invitación
            "@everyone",
            "@here"
        ]
        
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in forbidden_patterns)
    
    @staticmethod
    def is_spam(text: str) -> bool:
        """Detección básica de spam."""
        # Verificar repetición excesiva de caracteres
        if len(set(text)) / len(text) < 0.3 and len(text) > 10:
            return True
        
        # Verificar demasiados emojis
        emoji_count = sum(1 for char in text if ord(char) > 127)
        if emoji_count > len(text) * 0.5:
            return True
        
        return False

def create_error_embed(error_message: str, title: str = "Error") -> discord.Embed:
    """
    Crea un embed de error estandardizado.
    
    Args:
        error_message: Mensaje de error
        title: Título del error
        
    Returns:
        Embed de error
    """
    return create_embed(
        title=f"❌ {title}",
        description=error_message,
        color=discord.Color.red()
    )

def create_success_embed(message: str, title: str = "Éxito") -> discord.Embed:
    """
    Crea un embed de éxito estandardizado.
    
    Args:
        message: Mensaje de éxito
        title: Título del éxito
        
    Returns:
        Embed de éxito
    """
    return create_embed(
        title=f"✅ {title}",
        description=message,
        color=discord.Color.green()
    )

def create_info_embed(message: str, title: str = "Información") -> discord.Embed:
    """
    Crea un embed de información estandardizado.
    
    Args:
        message: Mensaje informativo
        title: Título de la información
        
    Returns:
        Embed informativo
    """
    return create_embed(
        title=f"ℹ️ {title}",
        description=message,
        color=discord.Color.blue()
    )
