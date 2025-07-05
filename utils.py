import time
from collections import defaultdict
from config import Config
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Memory-optimized rate limiter to prevent spam"""
    
    def __init__(self):
        self.user_timestamps = {}  # Changed from defaultdict to regular dict
        self.messages_limit = Config.RATE_LIMIT_MESSAGES
        self.time_window = Config.RATE_LIMIT_WINDOW
        self.max_users = 20  # Limit tracked users to save memory
    
    def check_user(self, user_id):
        """Check if user is within rate limits"""
        current_time = time.time()
        
        # Memory optimization: limit tracked users
        if len(self.user_timestamps) >= self.max_users and user_id not in self.user_timestamps:
            # Remove oldest user entry
            oldest_user = min(self.user_timestamps.keys(), 
                            key=lambda u: max(self.user_timestamps[u]) if self.user_timestamps[u] else 0)
            del self.user_timestamps[oldest_user]
        
        if user_id not in self.user_timestamps:
            self.user_timestamps[user_id] = []
        
        user_times = self.user_timestamps[user_id]
        
        # Remove timestamps outside the time window (memory optimization)
        user_times[:] = [t for t in user_times if current_time - t < self.time_window]
        
        # Check if user has exceeded the limit
        if len(user_times) >= self.messages_limit:
            return False
        
        # Add current timestamp
        user_times.append(current_time)
        return True
    
    def reset_user(self, user_id):
        """Reset rate limit for a specific user"""
        if user_id in self.user_timestamps:
            del self.user_timestamps[user_id]
    
    def get_user_count(self, user_id):
        """Get current message count for user"""
        current_time = time.time()
        user_times = self.user_timestamps[user_id]
        
        # Count messages within time window
        recent_messages = [t for t in user_times if current_time - t < self.time_window]
        return len(recent_messages)

class MessageFormatter:
    """Utility class for formatting Discord messages"""
    
    @staticmethod
    def truncate_message(message, max_length=2000):
        """Truncate message to Discord's character limit"""
        if len(message) <= max_length:
            return message
        
        # Try to truncate at a sentence boundary
        truncated = message[:max_length-3]
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        
        boundary = max(last_period, last_exclamation, last_question)
        
        if boundary > max_length * 0.7:  # If boundary is not too early
            return truncated[:boundary+1]
        else:
            return truncated + "..."
    
    @staticmethod
    def clean_discord_formatting(text):
        """Remove Discord formatting from text"""
        import re
        
        # Remove Discord markdown
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'__(.*?)__', r'\1', text)      # Underline
        text = re.sub(r'~~(.*?)~~', r'\1', text)      # Strikethrough
        text = re.sub(r'`(.*?)`', r'\1', text)        # Inline code
        text = re.sub(r'```[\s\S]*?```', '', text)    # Code blocks
        
        return text.strip()
    
    @staticmethod
    def add_reaction_emoji(text, probability=0.3):
        """Add random emoji to text based on probability"""
        import random
        
        if random.random() < probability:
            emojis = ["😄", "😂", "🤣", "😅", "🙃", "😎", "🤖", "⚡", "🔥", "💫"]
            return f"{text} {random.choice(emojis)}"
        
        return text

class ErrorHandler:
    """Centralized error handling utilities"""
    
    @staticmethod
    def log_api_error(error, context="Unknown"):
        """Log API errors with context"""
        logger.error(f"API Error in {context}: {str(error)}")
        
        # Log specific OpenAI errors
        if hasattr(error, 'response'):
            if hasattr(error.response, 'status_code'):
                logger.error(f"HTTP Status: {error.response.status_code}")
            if hasattr(error.response, 'text'):
                logger.error(f"Response: {error.response.text}")
    
    @staticmethod
    def get_user_friendly_error(error):
        """Convert technical errors to user-friendly messages"""
        error_str = str(error).lower()
        
        if "rate limit" in error_str or "quota" in error_str:
            return "Ops! Estou sendo muito usado agora. Tenta de novo em alguns minutos! ⏰"
        elif "timeout" in error_str or "connection" in error_str:
            return "Minha conexão deu pau! Tenta de novo, vai! 📡"
        elif "authentication" in error_str or "api key" in error_str:
            return "Problema na minha configuração! Chama o admin! 🔧"
        elif "invalid" in error_str:
            return "Alguma coisa tá errada aí! Verifica o que você digitou! 🤔"
        else:
            return "Deu algum erro aqui! Mas não desiste de mim! 🤖💥"

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('bot.log', encoding='utf-8')
        ]
    )
    
    # Set specific log levels for different modules
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
