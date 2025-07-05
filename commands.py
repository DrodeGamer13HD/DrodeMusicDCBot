import discord
from discord.ext import commands
import random
import asyncio
from personality import PersonalityEngine
import logging

logger = logging.getLogger(__name__)

async def setup_commands(bot):
    """Setup all bot commands"""
    
    @bot.command(name='zoa', aliases=['zoar'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def mock_user(ctx, *, target=None):
        """Zoa um usuário específico ou aleatório"""
        if target:
            # Try to find mentioned user
            if ctx.message.mentions:
                target_user = ctx.message.mentions[0]
            else:
                # Try to find by name
                target_user = discord.utils.find(
                    lambda m: target.lower() in m.display_name.lower(), 
                    ctx.guild.members
                )
        else:
            # Random user from server
            target_user = random.choice([m for m in ctx.guild.members if not m.bot])
        
        if not target_user:
            await ctx.reply("Não achei essa pessoa! Você inventou? 🤔")
            return
        
        try:
            async with ctx.typing():
                prompt = f"""
                Faça uma zoação amigável e engraçada sobre {target_user.display_name}.
                Seja criativo mas respeitoso. Use humor brasileiro.
                Máximo 2 frases.
                """
                
                if bot.personality.has_api and bot.personality.client:
                    response = bot.personality.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"""
                        Faça uma zoação amigável e engraçada sobre {target_user.display_name}.
                        Seja criativo mas respeitoso. Use humor brasileiro.
                        Máximo 2 frases. Fale português do Brasil.
                        """
                    )
                    roast = response.text.strip() if response.text else None
                else:
                    roast = None
                
                if roast:
                    await ctx.reply(f"{target_user.mention} {roast}")
                else:
                    # Fallback responses
                    fallback_roasts = [
                        f"{target_user.mention} Você é legal, mas sua internet não! 😂",
                        f"{target_user.mention} Parece que seu Wi-Fi é pior que minha IA! 🤖",
                        f"{target_user.mention} Sua conexão deve estar pior que meu senso de humor! 📡"
                    ]
                    await ctx.reply(random.choice(fallback_roasts))
                
        except Exception as e:
            logger.error(f"Erro no comando zoa: {e}")
            fallback_roasts = [
                f"{target_user.mention} Você é legal, mas sua internet não! 😂",
                f"{target_user.mention} Parece que seu Wi-Fi é pior que minha IA! 🤖",
                f"{target_user.mention} Sua conexão deve estar pior que meu senso de humor! 📡"
            ]
            await ctx.reply(random.choice(fallback_roasts))
    
    @bot.command(name='piada', aliases=['joke'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tell_joke(ctx):
        """Conta uma piada"""
        try:
            async with ctx.typing():
                if bot.personality.has_api and bot.personality.client:
                    response = bot.personality.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents="""
                        Conte uma piada curta e engraçada em português brasileiro.
                        Pode ser sobre tecnologia, games, ou cotidiano.
                        Máximo 3 frases. Fale português do Brasil.
                        """
                    )
                    joke = response.text.strip() if response.text else None
                else:
                    joke = None
                
                if joke:
                    await ctx.reply(f"🎭 {joke}")
                else:
                    fallback_jokes = [
                        "Por que o bot cruzou a estrada? Para chegar do outro lado do servidor! 🤖",
                        "Qual é o cúmulo da preguiça? Usar um bot para contar piadas! 😂",
                        "Minha IA está com bug, mas meu humor está funcionando! 🔧"
                    ]
                    await ctx.reply(random.choice(fallback_jokes))
                
        except Exception as e:
            logger.error(f"Erro no comando piada: {e}")
            fallback_jokes = [
                "Por que o bot cruzou a estrada? Para chegar do outro lado do servidor! 🤖",
                "Qual é o cúmulo da preguiça? Usar um bot para contar piadas! 😂",
                "Minha IA está com bug, mas meu humor está funcionando! 🔧"
            ]
            await ctx.reply(random.choice(fallback_jokes))
    
    @bot.command(name='elogio', aliases=['compliment'])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def compliment_user(ctx, *, target=None):
        """Faz um elogio (às vezes meio zoeiro)"""
        target_user = ctx.author
        
        if target:
            if ctx.message.mentions:
                target_user = ctx.message.mentions[0]
            else:
                target_user = discord.utils.find(
                    lambda m: target.lower() in m.display_name.lower(), 
                    ctx.guild.members
                )
        
        if not target_user:
            target_user = ctx.author
        
        try:
            async with ctx.typing():
                # Sometimes make it a backhanded compliment
                is_backhanded = random.random() < 0.3
                
                if bot.personality.has_api and bot.personality.client:
                    response = bot.personality.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"""
                        Faça um {'elogio meio duvidoso e engraçado' if is_backhanded else 'elogio genuíno mas divertido'} 
                        para {target_user.display_name}.
                        Seja criativo e use humor brasileiro.
                        Máximo 2 frases. Fale português do Brasil.
                        """
                    )
                    compliment = response.text.strip() if response.text else None
                else:
                    compliment = None
                
                if compliment:
                    await ctx.reply(f"{target_user.mention} {compliment}")
                else:
                    fallback_compliments = [
                        f"{target_user.mention} Você é quase tão legal quanto eu! 🤖",
                        f"{target_user.mention} Sua existência torna este servidor 3% melhor! 📈",
                        f"{target_user.mention} Você é a prova de que até humanos podem ser legais! 👨‍💻"
                    ]
                    await ctx.reply(random.choice(fallback_compliments))
                
        except Exception as e:
            logger.error(f"Erro no comando elogio: {e}")
            fallback_compliments = [
                f"{target_user.mention} Você é quase tão legal quanto eu! 🤖",
                f"{target_user.mention} Sua existência torna este servidor 3% melhor! 📈",
                f"{target_user.mention} Você é a prova de que até humanos podem ser legais! 👨‍💻"
            ]
            await ctx.reply(random.choice(fallback_compliments))
    
    @bot.command(name='status', aliases=['info'])
    async def bot_status(ctx):
        """Mostra informações sobre o bot"""
        embed = discord.Embed(
            title="🤖 Status do Bot Zoeiro",
            color=0x00ff00,
            description="Um bot português que usa IA para zoar com vocês!"
        )
        
        embed.add_field(
            name="📊 Estatísticas",
            value=f"Servidores: {len(bot.guilds)}\nUsuários: {len(set(bot.get_all_members()))}",
            inline=True
        )
        
        embed.add_field(
            name="🧠 IA",
            value="Powered by GPT-4o",
            inline=True
        )
        
        embed.add_field(
            name="⚡ Comandos",
            value="`!zoa` - Zoa alguém\n`!piada` - Conta piada\n`!elogio` - Faz elogio\n`!help` - Ajuda",
            inline=False
        )
        
        embed.set_footer(text="Feito com 💙 e muito café ☕")
        
        await ctx.reply(embed=embed)
    
    @bot.command(name='conversa', aliases=['chat'])
    @commands.cooldown(2, 30, commands.BucketType.user)
    async def start_conversation(ctx, *, topic=None):
        """Inicia uma conversa sobre um tópico"""
        if not topic:
            await ctx.reply("Sobre o que você quer conversar? Exemplo: `!conversa games`")
            return
        
        try:
            async with ctx.typing():
                if bot.personality.has_api and bot.personality.client:
                    response = bot.personality.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"""
                        Inicie uma conversa interessante e divertida sobre: {topic}
                        Faça uma pergunta ou comentário provocativo para gerar discussão.
                        Seja engraçado e use gírias brasileiras.
                        Máximo 2 frases. Fale português do Brasil.
                        """
                    )
                    conversation_starter = response.text.strip() if response.text else None
                else:
                    conversation_starter = None
                
                if conversation_starter:
                    await ctx.reply(f"💬 {conversation_starter}")
                else:
                    await ctx.reply(f"Hmm, {topic}? Interessante! O que vocês acham sobre isso? Alguém aí manja? 🤔")
                
        except Exception as e:
            logger.error(f"Erro no comando conversa: {e}")
            await ctx.reply(f"Hmm, {topic}? Interessante! O que vocês acham sobre isso? Alguém aí manja? 🤔")


import os
import discord
from discord.ext import commands
import asyncio
import re
import subprocess  # Importar subprocess para depuração de FFmpeg

# --- Configuração do Caminho do FFmpeg ---
FFMPEG_EXECUTABLE_PATH = "/nix/store/sahkv39jnsgwr7drg3ih7rlyhds7js35-jellyfin-ffmpeg-6.0.1-6-bin/bin/ffmpeg"  # Atualize este caminho se for diferente!

# --- Configuração do Bot ---
PREFIX = '!'
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# --- Funções Auxiliares ---
def get_stream_url_from_m3u(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if line.startswith('http://') or line.startswith('https://'):
                        return line
        return None
    except FileNotFoundError:
        print(f"Erro: Arquivo M3U '{file_path}' não encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao ler arquivo M3U '{file_path}': {e}")
        return None

def get_stream_url_from_pls(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'File1=(http[s]?://[^\n]+)', content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            return None
    except FileNotFoundError:
        print(f"Erro: Arquivo PLS '{file_path}' não encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao ler arquivo PLS '{file_path}': {e}")
        return None

# --- Eventos do Bot ---
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name} ({bot.user.id})')
    print('-----------------------------------------')
    print('Para adicionar o bot ao seu servidor, use este link:')
    print(f'https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot')
    print('-----------------------------------------')
    await bot.change_presence(activity=discord.Game(name=f"{PREFIX}help para comandos"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Desculpe, esse comando não existe. Tente `!help` para ver os comandos disponíveis.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Faltou um argumento para este comando. Verifique a sintaxe: `{ctx.command.usage or 'Verifique !help'}`")
    elif isinstance(error, commands.NotOwner):
        await ctx.send("Você não tem permissão para usar este comando.")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.author.send("Este comando não pode ser usado em mensagens diretas.")
    else:
        print(f"Ocorreu um erro no comando {ctx.command}: {error}")
        await ctx.send(f"Ops! Ocorreu um erro inesperado ao executar o comando. Erro: `{error}`")

# --- Comandos do Bot ---
@bot.command(name='entrar', help='Faz o bot entrar no seu canal de voz atual.')
async def entrar_command(ctx):
    if not ctx.author.voice:
        await ctx.send("Você precisa estar em um canal de voz para me chamar!")
        return

    channel = ctx.author.voice.channel
    try:
        if ctx.voice_client:
            if ctx.voice_client.channel.id == channel.id:
                await ctx.send("Eu já estou conectado a este canal de voz.")
                return
            else:
                await ctx.voice_client.disconnect()

        await channel.connect()
        await ctx.send(f"Entrei no canal de voz: **{channel.name}**")
    except discord.errors.ClientException:
        await ctx.send("Eu já estou conectado a um canal de voz (erro inesperado, verifique).")
    except Exception as e:
        await ctx.send(f"Não consegui entrar no canal de voz. Erro: `{e}`")

@bot.command(name='sair', help='Faz o bot sair do canal de voz atual.')
async def sair_command(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Saí do canal de voz.")
    else:
        await ctx.send("Eu não estou em nenhum canal de voz para sair.")

@bot.command(name='tocar', help='Começa a tocar o arquivo .m3u de stream. Requer que o bot já esteja no canal.')
async def tocar_command(ctx):
    if not ctx.voice_client:
        await ctx.send("Eu não estou conectado a um canal de voz. Use `!entrar` primeiro.")
        return

    m3u_file_path = "radio.m3u"  # Caminho do arquivo M3U
    stream_url = get_stream_url_from_m3u(m3u_file_path)

    if not stream_url:
        await ctx.send(f"Erro: O arquivo M3U '{m3u_file_path}' não contém um stream válido.")
        return

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Parando a reprodução atual e iniciando o stream...")

    try:
        # Usando o stream URL com FFmpegOpusAudio
        source = discord.FFmpegOpusAudio(stream_url, executable=FFMPEG_EXECUTABLE_PATH)
        ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)
        await ctx.send(f"Tocando o stream '{stream_url}' em **{ctx.voice_client.channel.name}**! 🎶")

    except Exception as e:
        await ctx.send(f"Ocorreu um erro ao tentar iniciar a reprodução do stream: `{e}`.")
        print(f"Erro na reprodução do stream: {e}")

@bot.command(name='parar', help='Para a reprodução do áudio.')
async def parar_command(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send('Reprodução interrompida.')
    else:
        await ctx.send('Não estou tocando nada no momento.')

# --- Inicia o Bot ---
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

if DISCORD_TOKEN:
    bot.run(DISCORD_TOKEN)
else:
    print("ERRO: O token do Discord não foi encontrado nas variáveis de ambiente.")
    print("Por favor, adicione 'DISCORD_TOKEN' nos Secrets do Replit com o token do seu bot.")
