import os
from dotenv import load_dotenv


##############################################
## Secrets
load_dotenv()

DISCORD_BOT_TOKEN             = os.getenv("DISCORD_BOT_TOKEN",             "")
OPENAI_PROJECT_NAME           = os.getenv("OPENAI_PROJECT_NAME",           "")
OPENAI_PROJECT_API_KEY        = os.getenv("OPENAI_PROJECT_API_KEY",        "")
DISCORD_BOT_CHANNEL_ID        = os.getenv("DISCORD_BOT_CHANNEL_ID",        "")
DEV_MESSAGE                   = os.getenv("DEV_MESSAGE",                   "")
DISCORD_BOT_CHANNEL_ID_CHAT   = os.getenv("DISCORD_BOT_CHANNEL_ID_CHAT",   "")

DISCORD_BOT_CHANNEL_ID         = int(DISCORD_BOT_CHANNEL_ID)
DISCORD_BOT_CHANNEL_ID_CHAT    = int(DISCORD_BOT_CHANNEL_ID_CHAT)

print("Loaded secrets")
