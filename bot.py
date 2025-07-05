import discord
from discord.ext import commands
import asyncio
import logging
import os
from config import Config
from personality_gemini import GeminiPersonalityEngine
from commands import setup_commands
from utils import RateLimiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PortugueseBot(commands.Bot):
    def __init__(self):
        # Configure bot intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            description="Um bot português engraçado que usa IA para zoar com os membros do servidor!"
        )
        
        # Initialize components
        self.personality = GeminiPersonalityEngine()
        self.rate_limiter = RateLimiter()
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Configurando o bot...")
        
        # Setup commands
        await setup_commands(self)
        
        logger.info("Bot configurado com sucesso!")
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.user} está online e pronto para zoar!')
        logger.info(f'Bot está em {len(self.guilds)} servidores')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="conversas para zoar 😄"
        )
        await self.change_presence(activity=activity)
    
    async def on_message(self, message):
        """Handle incoming messages"""
        # Ignore messages from bots
        if message.author.bot:
            return
        
        # Process commands first
        await self.process_commands(message)
        
        # Check if bot was mentioned, called by name, or if it's a DM
        bot_mentioned = self.user in message.mentions
        is_dm = isinstance(message.channel, discord.DMChannel)
        
        # Check if bot is called by name
        bot_name_mentioned = False
        if self.user:
            bot_names = [self.user.name.lower(), 'drode', 'bot']
            if self.user.display_name:
                bot_names.append(self.user.display_name.lower())
            bot_name_mentioned = any(name in message.content.lower() for name in bot_names)
        
        if bot_mentioned or is_dm or bot_name_mentioned:
            await self.handle_mention_or_dm(message)
        # NEW: Participate in conversations naturally
        elif await self.should_participate_in_conversation(message):
            await self.participate_in_conversation(message)
    
    async def handle_mention_or_dm(self, message):
        """Handle mentions and direct messages"""
        try:
            # Check rate limiting
            if not self.rate_limiter.check_user(message.author.id):
                await message.reply("Calma aí, amigão! Você está falando muito rápido. Espera um pouquinho! 😅")
                return
            
            # Show typing indicator
            async with message.channel.typing():
                # Generate response using personality engine
                response = await self.personality.generate_response(
                    message.content,
                    message.author.display_name,
                    message.guild.name if message.guild else "DM"
                )
                
                # Send response
                await message.reply(response)
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            await message.reply("Ops! Algo deu errado na minha cabeça. Tenta de novo! 🤖💥")
    
    async def should_participate_in_conversation(self, message):
        """Determine if the bot should participate in this conversation"""
        import random
        
        # Don't participate if it's a command
        if message.content.startswith(self.command_prefix):
            return False
        
        # Don't participate if message is too short
        if len(message.content.strip()) < 10:
            return False
        
        # Higher chance for questions
        if '?' in message.content:
            return random.random() < (Config.CASUAL_PARTICIPATION_RATE * 2)  # 2x rate for questions
        
        # Keywords that trigger participation
        trigger_keywords = [
            'alguém', 'algum', 'opinião', 'acham', 'pensam', 'sabem', 'conhecem',
            'ajuda', 'dica', 'sugestão', 'recomenda', 'indica', 'melhor',
            'pior', 'legal', 'massa', 'dahora', 'top', 'ruim', 'chato',
            'game', 'jogo', 'filme', 'série', 'música', 'comida', 'anime',
            'python', 'código', 'programação', 'tech', 'ia', 'ai', 'bot',
            'engraçado', 'funny', 'piada', 'meme', 'rir', 'kkkk', 'haha'
        ]
        
        message_lower = message.content.lower()
        if any(keyword in message_lower for keyword in trigger_keywords):
            return random.random() < Config.CASUAL_PARTICIPATION_RATE  # Configurable rate
        
        # Random participation for general messages
        return random.random() < (Config.CASUAL_PARTICIPATION_RATE * 0.3)  # Lower rate for general messages
    
    async def participate_in_conversation(self, message):
        """Participate naturally in conversations"""
        try:
            # Check rate limiting (more lenient for natural participation)
            if not self.rate_limiter.check_user(message.author.id):
                return
            
            # Show typing indicator
            async with message.channel.typing():
                # Generate contextual response
                response = await self.personality.generate_casual_response(
                    message.content,
                    message.author.display_name,
                    message.guild.name if message.guild else "DM"
                )
                
                if response:
                    await message.reply(response)
                    
        except Exception as e:
            logger.error(f"Erro ao participar da conversa: {e}")
    
    async def on_member_join(self, member):
        """Welcome new members with a funny message"""
        try:
            # Find system channel or general channel
            channel = member.guild.system_channel
            if not channel:
                # Try to find a general channel
                for ch in member.guild.text_channels:
                    if 'geral' in ch.name.lower() or 'general' in ch.name.lower():
                        channel = ch
                        break
            
            if channel:
                welcome_msg = await self.personality.generate_welcome_message(
                    member.display_name,
                    member.guild.name
                )
                await channel.send(welcome_msg)
                
        except Exception as e:
            logger.error(f"Erro ao dar boas-vindas: {e}")
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.reply("Esse comando não existe, meu chapa! Use `!help` para ver os comandos disponíveis. 🤔")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("Faltou alguma coisa aí! Verifica os argumentos do comando. 😉")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f"Calma aí! Espera mais {error.retry_after:.1f} segundos. ⏰")
        else:
            logger.error(f"Erro em comando: {error}")
            await ctx.reply("Deu ruim aqui! Tenta de novo mais tarde. 🛠️")

async def main():
    """Main function to run the bot"""
    # Validate configuration
    if not Config.validate():
        logger.error("Configuração inválida! Verifica as variáveis de ambiente.")
        return
    
    # Create and run bot
    bot = PortugueseBot()
    
    try:
        await bot.start(Config.DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error("Token do Discord inválido!")
    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
