import os
from dotenv import load_dotenv


##############################################
## Secrets

DISCORD_BOT_TOKEN        = os.getenv("DISCORD_BOT_TOKEN",          "")
OPENAI_PROJECT_NAME      = os.getenv("OPENAI_PROJECT_NAME",        "")
OPENAI_PROJECT_API_KEY   = os.getenv("OPENAI_PROJECT_API_KEY",     "")
DISCORD_BOT_CHANNEL_ID   = os.getenv("DISCORD_BOT_CHANNEL_ID",     "")

DISCORD_BOT_CHANNEL_ID = int(DISCORD_BOT_CHANNEL_ID)

print("Loaded secrets")
