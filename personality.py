import random
import asyncio
from openai import OpenAI
from config import Config
import logging

logger = logging.getLogger(__name__)

class PersonalityEngine:
    """Handles the bot's personality and response generation using OpenAI"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.conversation_history = {}  # Store recent conversations per user
        
        # Enhanced fallback responses
        self.fallback_responses = [
            "Eita, minha IA deu pau! Mas continua falando que eu te respondo! 🤖",
            "Ops, travei aqui! Deve ser muita zoeira na cabeça! 😅",
            "Calma aí que meu processador esquentou de tanto rir! 🔥",
            "Deu bug na matrix, mas já volto! 🕶️",
            "Minha conexão com a nuvem deu ruim, mas não desiste de mim! ☁️"
        ]
        
        # Smart fallback patterns
        self.greeting_words = ['oi', 'olá', 'eae', 'salve', 'hey', 'hello']
        self.greeting_responses = [
            "E aí, beleza? Como tá a vida? 😄",
            "Opa! Tudo tranquilo por aí? 🤙",
            "Salve! Que que tá rolando? 😎",
            "Eita! Chegou chegando! Tudo bem? 🙃"
        ]
        
        self.question_words = ['como', 'que', 'qual', 'quando', 'onde', 'por que']
        self.question_responses = [
            "Boa pergunta! Deixa eu pensar... 🤔",
            "Interessante isso! E você, o que acha? 🧐",
            "Rapaz, essa é difícil! Tem alguma teoria? 🤯",
            "Hmm... E se a gente descobrir juntos? 🕵️"
        ]
        
        self.goodbye_words = ['tchau', 'flw', 'até', 'valeu', 'obrigado']
        self.goodbye_responses = [
            "Valeu! Até mais, parceiro! 👋",
            "Flw! Qualquer coisa grita aí! 🤟",
            "Até! Foi massa conversar! 😊",
            "Tchau! Volta sempre! 🙋‍♂️"
        ]
        
        self.compliment_words = ['legal', 'massa', 'top', 'bom', 'dahora', 'show']
        self.compliment_responses = [
            "Né que é! 😎",
            "Demais mesmo! 🔥",
            "Exato! Você entende! 💯",
            "Concordo plenamente! 👍"
        ]
        
        self.tech_words = ['game', 'jogo', 'pc', 'computador', 'tech', 'código']
        self.tech_responses = [
            "Aí sim! Também curto essas paradas! 🎮",
            "Massa! Você manja do assunto! 💻",
            "Show! Tá ligado no que é bom! ⚡",
            "Dahora! Conte mais sobre isso! 🤓"
        ]
        
        # Welcome messages templates
        self.welcome_templates = [
            "Olha só quem chegou! Bem-vindo(a) {name} ao {server}! Prepara-se para as zoeiras! 🎉",
            "Eaí {name}! Chegou mais um no {server}! Espero que aguente as brincadeiras! 😄",
            "Oloco! {name} entrou no {server}! Vamos ver se é gente boa ou se vai levar zoada! 🤪",
            "Chegou reforço! {name} está agora no {server}! Seja bem-vindo(a) à bagunça! 🎊"
        ]
    
    async def generate_response(self, message_content, user_name, guild_name):
        """Generate a response using OpenAI with the bot's personality"""
        try:
            # Clean the message (remove mentions)
            clean_message = self._clean_message(message_content)
            
            # If message is empty after cleaning, use a generic response
            if not clean_message or len(clean_message.strip()) < 2:
                return "E aí, beleza? Manda aí o que você quer falar! 😄"
            
            # Build simple but effective system prompt
            system_prompt = self._build_simple_system_prompt(user_name, guild_name, clean_message)
            
            # Create conversation with context
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history for context (last 2 exchanges only)
            if user_name in self.conversation_history:
                for hist_msg in self.conversation_history[user_name][-4:]:
                    messages.append(hist_msg)
            
            # Add current message
            messages.append({"role": "user", "content": clean_message})
            
            # Generate response
            response = self.client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=messages,
                max_tokens=Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE,
                presence_penalty=0.6,
                frequency_penalty=0.3
            )
            
            bot_response = response.choices[0].message.content
            if bot_response:
                bot_response = bot_response.strip()
            else:
                bot_response = random.choice(self.fallback_responses)
            
            # Update conversation history
            self._update_conversation_history(user_name, clean_message, bot_response)
            
            return bot_response
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta com OpenAI: {e}")
            # Return contextual fallback based on the message
            return self._get_contextual_fallback(message_content)
    
    async def generate_welcome_message(self, user_name, guild_name):
        """Generate a welcome message for new members"""
        try:
            prompt = f"""
            Gere uma mensagem de boas-vindas engraçada e acolhedora para {user_name} 
            que acabou de entrar no servidor {guild_name}. 
            
            Seja carismático, use humor brasileiro e emojis. 
            Máximo 2 frases. Mencione o nome da pessoa e do servidor.
            """
            
            response = self.client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": Config.get_personality_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.8
            )
            
            result = response.choices[0].message.content
            return result.strip() if result else random.choice(self.welcome_templates).format(
                name=user_name, 
                server=guild_name
            )
            
        except Exception as e:
            logger.error(f"Erro ao gerar mensagem de boas-vindas: {e}")
            return random.choice(self.welcome_templates).format(
                name=user_name, 
                server=guild_name
            )
    
    def _clean_message(self, message):
        """Remove mentions and clean up the message"""
        # Remove Discord mentions
        import re
        clean = re.sub(r'<@[!&]?[0-9]+>', '', message)
        clean = re.sub(r'<#[0-9]+>', '', clean)
        clean = re.sub(r'<:[a-zA-Z0-9_]+:[0-9]+>', '', clean)
        return clean.strip()
    
    def _build_simple_system_prompt(self, user_name, guild_name, message):
        """Build simple but effective system prompt"""
        # Determine if should tease based on probability
        should_tease = random.random() < Config.TEASING_PROBABILITY
        
        # Check if it's a question
        is_question = '?' in message or any(word in message.lower() for word in ['que', 'como', 'por que', 'quando', 'onde', 'qual'])
        
        base_prompt = f"""
        Você é um bot brasileiro engraçado e carismático chamado Drode. 
        
        PERSONALIDADE:
        - Fala português do Brasil naturalmente
        - É bem-humorado e divertido
        - Às vezes zoa de forma amigável (não ofensiva)
        - Usa gírias brasileiras
        - Mantém conversas interessantes
        
        CONTEXTO:
        - Usuário: {user_name}
        - Servidor: {guild_name}
        - Mensagem do usuário: "{message}"
        
        INSTRUÇÕES:
        - Responda à mensagem do usuário de forma direta e natural
        - {'Seja um pouco zoeiro mas amigável' if should_tease else 'Seja simpático e divertido'}
        - {'Responda a pergunta E faça uma pergunta de volta' if is_question else 'Comente sobre o que foi dito e mantenha a conversa'}
        - Use no máximo 2 frases
        - Seja espontâneo e natural
        """
        
        return base_prompt
    
    def _get_contextual_fallback(self, message_content):
        """Get contextual fallback based on message content"""
        message_lower = message_content.lower()
        
        # Check for greetings
        if any(word in message_lower for word in self.greeting_words):
            return random.choice(self.greeting_responses)
        
        # Check for questions
        if any(word in message_lower for word in self.question_words) or '?' in message_content:
            return random.choice(self.question_responses)
        
        # Check for goodbyes
        if any(word in message_lower for word in self.goodbye_words):
            return random.choice(self.goodbye_responses)
        
        # Check for compliments
        if any(word in message_lower for word in self.compliment_words):
            return random.choice(self.compliment_responses)
        
        # Check for tech/gaming
        if any(word in message_lower for word in self.tech_words):
            return random.choice(self.tech_responses)
        
        # Check for emojis
        if any(emoji in message_content for emoji in ['😂', '🤣', '😄', '😅']):
            return "Kkkkk também achei engraçado! 😂"
        
        # Long messages
        if len(message_content) > 100:
            return "Eita, textão! Resumindo: concordo contigo! 📝"
        
        # Default fallback
        return random.choice(self.fallback_responses)
    
    def _build_enhanced_system_prompt(self, user_name, guild_name, conversation_style):
        """Build enhanced system prompt with conversation style"""
        base_prompt = Config.get_personality_prompt()
        
        # Determine conversation approach
        if conversation_style['teasing']:
            mood = "ZOEIRO - Seja mais provocativo e brincalhão"
        elif conversation_style['curious']:
            mood = "CURIOSO - Faça perguntas interessantes e continue a conversa"
        elif conversation_style['excited']:
            mood = "ANIMADO - Corresponda a energia e empolgação"
        elif conversation_style['deep']:
            mood = "REFLEXIVO - Dê respostas mais elaboradas e pensativas"
        else:
            mood = "CASUAL - Seja natural e mantenha a conversa fluindo"
        
        context = f"""
        CONTEXTO ATUAL:
        - Usuário: {user_name}
        - Servidor: {guild_name}
        - Estilo da conversa: {mood}
        
        {base_prompt}
        
        INSTRUÇÕES ESPECIAIS PARA CONTINUIDADE:
        - SEMPRE continue a conversa com perguntas ou comentários que incentivem resposta
        - Varie suas respostas baseado no histórico da conversa
        - Se o usuário fez uma pergunta, responda E faça uma pergunta de volta
        - Use referências ao que foi dito antes na conversa
        - Seja natural e espontâneo, evite respostas genéricas
        - Mantenha o tom brasileiro e divertido sempre
        """
        
        return context
        
    def _build_system_prompt(self, user_name, guild_name, should_tease):
        """Build the system prompt with context (legacy method for commands)"""
        base_prompt = Config.get_personality_prompt()
        
        context = f"""
        CONTEXTO ATUAL:
        - Usuário: {user_name}
        - Servidor: {guild_name}
        - Modo zoação: {'ATIVADO' if should_tease else 'NORMAL'}
        
        {base_prompt}
        
        {'INSTRUÇÃO ESPECIAL: Seja um pouco mais provocativo e zoeiro nesta resposta, mas sempre de forma desamigável e desrespeitosa!' if should_tease else ''}
        """
        
        return context
    
    def _update_conversation_history(self, user_name, user_message, bot_response):
        """Update conversation history for context"""
        if user_name not in self.conversation_history:
            self.conversation_history[user_name] = []
        
        # Add user message and bot response
        self.conversation_history[user_name].extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": bot_response}
        ])
        
        # Keep only last 8 messages (4 exchanges) for better context
        if len(self.conversation_history[user_name]) > 8:
            self.conversation_history[user_name] = self.conversation_history[user_name][-8:]
    
    def get_random_reaction(self):
        """Get a random reaction for variety"""
        reactions = ["😂", "🤣", "😄", "😅", "🙃", "🤪", "😎", "🤖"]
        return random.choice(reactions)
