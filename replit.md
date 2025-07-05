# Portuguese Discord Bot with ChatGPT

## Overview

This is a Portuguese Discord bot that uses Google Gemini API to create an entertaining and irreverent bot personality. The bot interacts with Discord server members in Brazilian Portuguese, featuring humor, playful teasing, and various fun commands. It's designed to be a community engagement tool that adds personality and entertainment to Discord servers.

**NEW**: The bot now participates naturally in conversations without being mentioned, responding to questions and interesting topics with contextual awareness.

**UPDATED**: Bot personality refined to be less sarcastic, detect irony (😭) and heavy content (💀), use fewer emojis, and optimized for better memory usage.

## System Architecture

### Backend Architecture
- **Framework**: discord.py library for Discord API integration
- **AI Integration**: Google Gemini API (Gemini-2.5-flash model) for intelligent responses - FREE tier available
- **Language**: Python with async/await patterns for concurrent operations
- **Configuration**: Environment variable-based configuration with dotenv support

### Core Components Structure
```
bot.py           # Main bot class and entry point
commands.py      # Command handlers and bot interactions
personality.py   # AI personality engine and response generation
config.py        # Configuration management and validation
utils.py         # Utility classes (rate limiting, message formatting)
```

## Key Components

### 1. PortugueseBot (Main Bot Class)
- Extends discord.py's commands.Bot
- Manages bot lifecycle and event handling
- Integrates personality engine and rate limiting
- Handles Discord intents for message content and member events

### 2. PersonalityEngine
- **Purpose**: Manages AI-powered responses using Google Gemini API
- **Features**: 
  - Context-aware conversations with history tracking
  - Brazilian Portuguese personality - refined to be less sarcastic, more genuine
  - Irony detection with appropriate emoji responses (😭)
  - Heavy content detection with skull emoji (💀)
  - Reduced emoji usage for cleaner conversations
  - Fallback responses for API failures
  - Welcome message generation for new members
  - **NEW**: Natural conversation participation without direct mentions
  - **OPTIMIZED**: Memory-efficient conversation history management
- **Model**: Uses Gemini-2.5-flash with smart contextual prompting

### 3. Command System
- **Prefix-based commands** starting with "!" (configurable)
- **Available commands**:
  - `!zoa` - Playfully tease users
  - `!piada` - Tell jokes
  - `!elogio` - Give compliments
  - `!conversa` - Start conversations
  - `!status` - Show bot information
  - `!help` - List commands
- **Rate limiting**: Built-in cooldowns to prevent spam

### 4. Rate Limiting System
- **User-based limits**: Configurable messages per time window
- **Memory management**: Automatic cleanup of old timestamps
- **Spam prevention**: Protects against abuse while maintaining responsiveness

### 5. Configuration Management
- **Environment variables**: Secure storage of API keys and settings
- **Validation**: Ensures required configuration is present
- **Customizable parameters**: Humor level, teasing probability, rate limits

## Data Flow

### Message Processing Flow
1. **Message Reception**: Discord message received by bot
2. **Rate Limiting**: Check if user is within allowed limits
3. **Command Detection**: Determine if message is a command or mention
4. **Context Building**: Prepare conversation context for AI
5. **AI Processing**: Send to OpenAI API with personality prompt
6. **Response Generation**: Format and send response back to Discord
7. **History Update**: Store conversation context for future interactions

### AI Response Generation
1. **Message Cleaning**: Remove Discord-specific formatting
2. **Personality Injection**: Add Brazilian Portuguese personality traits
3. **Context Addition**: Include server and user information
4. **API Call**: Send to ChatGPT with system prompts
5. **Fallback Handling**: Use predefined responses if API fails

## External Dependencies

### Required APIs
- **Discord Bot API**: For Discord integration and bot functionality
- **Google Gemini API**: For AI-powered responses and personality (FREE tier available)

### Python Packages
- `discord.py`: Discord API wrapper
- `google-genai`: Google Gemini API client
- `python-dotenv`: Environment variable management
- `asyncio`: Asynchronous programming support
- `logging`: Application logging and debugging

### Environment Variables
- `DISCORD_TOKEN`: Discord bot authentication token
- `GEMINI_API_KEY`: Google Gemini API authentication key (FREE tier available)
- `COMMAND_PREFIX`: Bot command prefix (default: "!")
- `HUMOR_LEVEL`: Personality humor intensity (0.0-1.0)
- `TEASING_PROBABILITY`: Chance of playful teasing (0.0-1.0)
- `CASUAL_PARTICIPATION_RATE`: Rate of natural conversation participation (0.0-1.0, default: 0.15)
- `RATE_LIMIT_MESSAGES`: Messages per time window
- `RATE_LIMIT_WINDOW`: Rate limiting time window in seconds

## Deployment Strategy

### Local Development
- Environment variables loaded from `.env` file
- Direct Python execution with `python bot.py`
- Logging configured for development debugging

### Production Considerations
- Secure environment variable management
- Process monitoring and auto-restart capabilities
- Rate limiting to prevent API quota exhaustion
- Error handling and graceful degradation

### Scalability Features
- Stateless design for easy horizontal scaling
- Configurable rate limits per deployment environment
- Modular architecture for feature additions

## Changelog

- July 04, 2025. Refined personality: less sarcastic, detects irony (😭) and heavy content (💀), fewer emojis, memory optimized
- July 04, 2025. Added natural conversation participation - bot now responds to questions and topics without direct mentions
- July 04, 2025. Migrated from OpenAI to Google Gemini API for cost-free operation
- July 03, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.