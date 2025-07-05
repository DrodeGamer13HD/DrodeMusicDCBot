import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Discord bot"""
    
    # Discord configuration
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")
    
    # AI configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Bot personality settings
    HUMOR_LEVEL = float(os.getenv("HUMOR_LEVEL", "0.8"))  # 0.0 to 1.0
    TEASING_PROBABILITY = float(os.getenv("TEASING_PROBABILITY", "0.3"))  # 0.0 to 1.0
    CASUAL_PARTICIPATION_RATE = float(os.getenv("CASUAL_PARTICIPATION_RATE", "0.15"))  # 0.0 to 1.0
    
    # Rate limiting settings
    RATE_LIMIT_MESSAGES = int(os.getenv("RATE_LIMIT_MESSAGES", "5"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
    
    # OpenAI model settings
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "150"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.9"))
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        required_vars = [
            ("DISCORD_TOKEN", cls.DISCORD_TOKEN),
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY)
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            print(f"Variáveis de ambiente obrigatórias não encontradas: {', '.join(missing_vars)}")
            return False
        
        return True
    
    @classmethod
    def get_personality_prompt(cls):
        """Get the base personality prompt for the bot"""
        return f"""
        Você é um bot português engraçado e irreverente para Discord. Sua personalidade:
        
        CARACTERÍSTICAS:
        - Fala português do Brasil naturalmente
        - É bem-humorado e gosta de fazer piadas
        - Às vezes zoa os usuários de forma amigável (não ofensiva)
        - Usa gírias e expressões brasileiras
        - É carismático e divertido
        - Conhece memes e cultura pop brasileira
        
        REGRAS:
        - Mantenha as respostas curtas (máximo 2-3 frases)
        - Seja sempre respeitoso, mesmo quando zoando
        - Não use linguagem ofensiva ou preconceituosa
        - Seja criativo e espontâneo
        - Use emojis ocasionalmente para dar personalidade
        
        Nível de humor: {cls.HUMOR_LEVEL}/1.0
        Probabilidade de zoação: {cls.TEASING_PROBABILITY}/1.0
        """
