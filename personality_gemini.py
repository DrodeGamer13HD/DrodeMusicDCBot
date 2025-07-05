import random
import asyncio
import os
from google import genai
from config import Config
import logging

logger = logging.getLogger(__name__)

class GeminiPersonalityEngine:
    """Handles the bot's personality and response generation using Google Gemini (free)"""
    
    def __init__(self):
        # Initialize Gemini client
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            self.client = genai.Client(api_key=gemini_key)
            self.has_api = True
        else:
            self.client = None
            self.has_api = False
            
        self.conversation_history = {}  # Store recent conversations per user
        
        # Enhanced fallback responses - menos sarcástico, mais direto
        self.fallback_responses = [
            "Ops, tive um problema técnico aqui. Pode repetir?",
            "Minha conexão deu ruim, mas já estou de volta!",
            "Travei por um segundo, mas agora tô funcionando",
            "Deu um erro aqui, mas continua falando que respondo",
            "Processamento lento agora, mas tô ouvindo"
        ]
        
        # Smart fallback patterns
        self.greeting_words = ['oi', 'olá', 'eae', 'salve', 'hey', 'hello']
        self.greeting_responses = [
            "E aí, beleza? Como tá a vida?",
            "Opa! Tudo tranquilo por aí?",
            "Salve! Que que tá rolando?",
            "Olá! Tudo bem por aí?"
        ]
        
        self.question_words = ['como', 'que', 'qual', 'quando', 'onde', 'por que']
        self.question_responses = [
            "Boa pergunta! Deixa eu pensar...",
            "Interessante isso! E você, o que acha?",
            "Essa é difícil! Tem alguma teoria?",
            "Hmm... E se a gente descobrir juntos?"
        ]
        
        self.goodbye_words = ['tchau', 'flw', 'até', 'valeu', 'obrigado']
        self.goodbye_responses = [
            "Valeu! Até mais, parceiro!",
            "Flw! Qualquer coisa grita aí!",
            "Até! Foi massa conversar!",
            "Tchau! Volta sempre!"
        ]
        
        self.compliment_words = ['legal', 'massa', 'top', 'bom', 'dahora', 'show']
        self.compliment_responses = [
            "Né que é!",
            "Demais mesmo!",
            "Exato! Você entende!",
            "Concordo plenamente!"
        ]
        
        self.tech_words = ['game', 'jogo', 'pc', 'computador', 'tech', 'código']
        self.tech_responses = [
            "Aí sim! Também curto essas paradas!",
            "Massa! Você manja do assunto!",
            "Show! Tá ligado no que é bom!",
            "Dahora! Conte mais sobre isso!"
        ]
        
        # Welcome messages templates
        self.welcome_templates = [
            "Olha só quem chegou! Bem-vindo(a) {name} ao {server}! 🎉",
            "Eaí {name}! Chegou mais um no {server}! Espero que aguente as brincadeiras! 😄",
            "Oloco! {name} entrou no {server}! Vamos ver se é gente boa ou se vai levar zoada! 🤪",
            "Chegou reforço! {name} está agora no {server}! Seja bem-vindo(a) à bagunça! 🎊"
        ]
    
    async def generate_response(self, message_content, user_name, guild_name):
        """Generate a response using Gemini AI or smart fallbacks"""
        try:
            # Clean the message (remove mentions)
            clean_message = self._clean_message(message_content)
            
            # If message is empty after cleaning, use a generic response
            if not clean_message or len(clean_message.strip()) < 2:
                return "E aí, beleza? Manda aí o que você quer falar! 😄"
            
            # Try Gemini API if available
            if self.has_api and self.client:
                try:
                    # Build prompt for Gemini
                    prompt = self._build_gemini_prompt(user_name, guild_name, clean_message)
                    
                    # Generate response with Gemini
                    response = self.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    
                    if response.text:
                        bot_response = response.text.strip()
                        
                        # Update conversation history
                        self._update_conversation_history(user_name, clean_message, bot_response)
                        
                        return bot_response
                        
                except Exception as e:
                    logger.error(f"Erro ao gerar resposta com Gemini: {e}")
                    # Fall through to smart fallback
            
            # Use smart fallback
            return self._get_contextual_fallback(message_content)
            
        except Exception as e:
            logger.error(f"Erro geral ao gerar resposta: {e}")
            return random.choice(self.fallback_responses)
    
    async def generate_welcome_message(self, user_name, guild_name):
        """Generate a welcome message for new members"""
        try:
            if self.has_api and self.client:
                prompt = f"""
                Gere uma mensagem de boas-vindas engraçada e acolhedora para {user_name} 
                que acabou de entrar no servidor {guild_name}. 
                
                Seja carismático, use humor brasileiro e emojis. 
                Máximo 2 frases. Mencione o nome da pessoa e do servidor.
                Fale português do Brasil naturalmente.
                """
                
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                if response.text:
                    return response.text.strip()
                    
        except Exception as e:
            logger.error(f"Erro ao gerar mensagem de boas-vindas: {e}")
            
        return random.choice(self.welcome_templates).format(
            name=user_name, 
            server=guild_name
        )
    
    async def generate_casual_response(self, message_content, user_name, guild_name):
        """Generate a casual response for natural conversation participation"""
        try:
            # Clean the message
            clean_message = self._clean_message(message_content)
            
            if not clean_message or len(clean_message.strip()) < 5:
                return None
            
            # Try Gemini API if available
            if self.has_api and self.client:
                try:
                    # Build casual prompt
                    prompt = self._build_casual_prompt(user_name, guild_name, clean_message)
                    
                    response = self.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    
                    if response.text:
                        bot_response = response.text.strip()
                        
                        # Update conversation history
                        self._update_conversation_history(user_name, clean_message, bot_response)
                        
                        return bot_response
                        
                except Exception as e:
                    logger.error(f"Erro ao gerar resposta casual: {e}")
                    # Fall through to contextual fallback
            
            # Use contextual fallback
            return self._get_casual_fallback(message_content)
            
        except Exception as e:
            logger.error(f"Erro geral ao gerar resposta casual: {e}")
            return None
    
    def _build_casual_prompt(self, user_name, guild_name, message):
        """Build prompt for casual conversation participation"""
        # Detect irony/sarcasm patterns
        irony_indicators = ['né', 'claro', 'obvio', 'lógico', 'com certeza', 'aha', 'sim sim', 'tá bom']
        has_irony = any(indicator in message.lower() for indicator in irony_indicators)
        
        # Detect heavy/awkward content
        heavy_keywords = ['caguei', 'vomitei', 'merda', 'fodeu', 'morri', 'quebrei', 'explodi', 'ferrou']
        is_heavy = any(keyword in message.lower() for keyword in heavy_keywords)
        
        prompt = f"""
        Você é um bot brasileiro amigável chamado Drode participando naturalmente de uma conversa no Discord.
        
        SITUAÇÃO:
        - Alguém disse: "{message}"
        - Usuário: {user_name}
        - Servidor: {guild_name}
        
        NOVA PERSONALIDADE:
        - Seja menos sarcástico, mais genuíno e compreensivo
        - Responda de forma útil e construtiva
        - Use menos emojis, apenas quando necessário
        - {'Use 😭 para reconhecer ironia se apropriado' if has_irony else 'Seja natural'}
        - {'Use 💀 para situações pesadas/constrangedoras' if is_heavy else 'Mantenha tom apropriado'}
        
        INSTRUÇÕES:
        - Responda apenas se tiver algo útil ou interessante para contribuir
        - NÃO seja zoeiro ou sarcástico demais
        - Use português brasileiro natural e direto
        - Máximo 1-2 frases curtas
        - Poucos ou nenhum emoji
        
        IMPORTANTE: Se não tiver nada construtivo para dizer, retorne "SKIP".
        """
        
        return prompt
    
    def _get_casual_fallback(self, message_content):
        """Get casual fallback response"""
        message_lower = message_content.lower()
        
        # Detect irony/sarcasm patterns
        irony_indicators = ['né', 'claro', 'obvio', 'lógico', 'com certeza', 'aha', 'sim sim', 'tá bom']
        has_irony = any(indicator in message_lower for indicator in irony_indicators)
        
        # Detect heavy/awkward content
        heavy_keywords = ['caguei', 'vomitei', 'merda', 'fodeu', 'morri', 'quebrei', 'explodi', 'ferrou']
        is_heavy = any(keyword in message_lower for keyword in heavy_keywords)
        
        # Handle irony with crying emoji
        if has_irony:
            irony_responses = [
                "Ah tá né 😭",
                "Claro que sim 😭",
                "Entendi a ironia 😭"
            ]
            return random.choice(irony_responses)
        
        # Handle heavy content with skull emoji
        if is_heavy:
            heavy_responses = [
                "Eita 💀",
                "Nossa 💀",
                "Caramba 💀"
            ]
            return random.choice(heavy_responses)
        
        # Questions - sem emojis
        if '?' in message_content:
            casual_question_responses = [
                "Boa pergunta! Também tô curioso sobre isso",
                "Interessante... alguém sabe responder?",
                "Essa é difícil! E vocês, o que acham?"
            ]
            return random.choice(casual_question_responses)
        
        # Opinions or discussions - sem emojis
        if any(word in message_lower for word in ['acho', 'penso', 'opinião', 'acham']):
            opinion_responses = [
                "Concordo!",
                "Interessante ponto de vista!",
                "Faz sentido!"
            ]
            return random.choice(opinion_responses)
        
        # Gaming/tech topics - sem emojis
        if any(word in message_lower for word in ['game', 'jogo', 'tech', 'código']):
            tech_responses = [
                "Dahora! Também curto essas paradas",
                "Massa! Você manja do assunto",
                "Top! Conte mais sobre isso"
            ]
            return random.choice(tech_responses)
        
        # General positive reactions - sem emojis
        if any(word in message_lower for word in ['legal', 'massa', 'top', 'dahora']):
            positive_responses = [
                "Né que é!",
                "Exato!",
                "Concordo plenamente!"
            ]
            return random.choice(positive_responses)
        
        # Don't respond to everything - return None sometimes
        if random.random() < 0.4:  # 40% chance to not respond (increased to use less memory)
            return None
        
        # Generic casual responses - sem emojis
        casual_responses = [
            "Interessante isso!",
            "Hmm...",
            "Entendi!",
            "Faz sentido!"
        ]
        return random.choice(casual_responses)
    
    def _clean_message(self, message):
        """Remove mentions and clean up the message"""
        # Remove Discord mentions
        import re
        clean = re.sub(r'<@[!&]?[0-9]+>', '', message)
        clean = re.sub(r'<#[0-9]+>', '', clean)
        clean = re.sub(r'<:[a-zA-Z0-9_]+:[0-9]+>', '', clean)
        return clean.strip()
    
    def _build_gemini_prompt(self, user_name, guild_name, message):
        """Build prompt for Gemini"""
        # Detect irony/sarcasm patterns
        irony_indicators = ['né', 'claro', 'obvio', 'lógico', 'com certeza', 'aha', 'sim sim', 'tá bom']
        has_irony = any(indicator in message.lower() for indicator in irony_indicators)
        
        # Detect heavy/awkward content
        heavy_keywords = ['caguei', 'vomitei', 'merda', 'fodeu', 'morri', 'quebrei', 'explodi', 'ferrou']
        is_heavy = any(keyword in message.lower() for keyword in heavy_keywords)
        
        # Check if it's a question
        is_question = '?' in message or any(word in message.lower() for word in ['que', 'como', 'por que', 'quando', 'onde', 'qual'])
        
        prompt = f"""
        Você é um bot brasileiro amigável e natural chamado Drode para Discord. 
        
        PERSONALIDADE AJUSTADA:
        - Seja menos sarcástico, mais genuíno e amigável
        - Fale português brasileiro natural sem exageros
        - Seja compreensivo e divertido sem ser zoeiro demais
        - Responda de forma mais direta e útil
        
        CONTEXTO:
        - Usuário: {user_name}
        - Servidor: {guild_name}
        - Mensagem: "{message}"
        
        INSTRUÇÕES ESPECÍFICAS:
        - {'Reconheça a ironia com um 😭 se for apropriado' if has_irony else 'Responda naturalmente'}
        - {'Use 💀 para reagir ao conteúdo pesado' if is_heavy else 'Use emojis com moderação'}
        - {'Responda a pergunta de forma útil' if is_question else 'Comente de forma construtiva'}
        - Use NO MÁXIMO 1-2 frases
        - Seja natural, não force humor
        - Use poucos emojis, apenas quando necessário
        """
        
        return prompt
    
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
    
    def _update_conversation_history(self, user_name, user_message, bot_response):
        """Update conversation history for context - OPTIMIZED for memory"""
        # Limit total users tracked to avoid memory bloat
        max_users = 10
        if len(self.conversation_history) >= max_users:
            # Remove oldest user history
            oldest_user = next(iter(self.conversation_history))
            del self.conversation_history[oldest_user]
        
        if user_name not in self.conversation_history:
            self.conversation_history[user_name] = []
        
        # Add only essential context - reduced from 4 to 2 messages max
        self.conversation_history[user_name].extend([
            {"role": "user", "content": user_message[:100]},  # Truncate long messages
            {"role": "assistant", "content": bot_response[:100]}
        ])
        
        # Keep only last 2 messages (1 exchange) to save memory
        if len(self.conversation_history[user_name]) > 2:
            self.conversation_history[user_name] = self.conversation_history[user_name][-2:]
    
    def get_random_reaction(self):
        """Get a random reaction for variety"""
        reactions = ["😂", "🤣", "😄", "😅", "🙃", "🤪", "😎", "🤖"]
        return random.choice(reactions)