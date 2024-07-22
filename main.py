#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from openai import OpenAI


# Load in secrets/config
load_dotenv()
DISCORD_BOT_TOKEN        = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_PROJECT_NAME      = os.getenv("OPENAI_PROJECT_NAME")
OPENAI_PROJECT_API_KEY   = os.getenv("OPENAI_PROJECT_API_KEY")


# Init the bot server/client

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
openai_client = OpenAI(api_key=OPENAI_PROJECT_API_KEY,
                       project=OPENAI_PROJECT_NAME)



total_cost_since_bot_reboot = 0.0


# Events

@bot.event
async def on_ready():
    print(f'{bot.user} successfully logged in!')



@bot.command(name="greet")
async def greet(ctx):
    await ctx.send("Hello! I'm BasedBot!")


# dalle-3 limit is 7 images per minute
# dalle-2 limit is 50 images per minute
# urls will expire after 1 hour
# https://platform.openai.com/docs/guides/images/usage
# https://platform.openai.com/settings/organization/limits

# 1024x1024, 1792x1024, or 1024x1792 for DALL·E-3 



@bot.command(name="draw")
async def draw(ctx, *, prompt: str = None):

    if not prompt:
        await ctx.send("Error: no prompt")
        return None
    
    # Process the entire prompt
    # all_time_cost += 0.40
    await ctx.send(f"Prompt: {prompt}")
    await ctx.send(f"Working..... Queue now full.")
    await ctx.send(f"todo: implement a typing indicator")
    await ctx.send(f"todo: implement a queue system")

    revised_prompt = ""
    image_url = ""

    try:
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard", # or "hd"
            n=1,
        )
        # todo: try catch
        revised_prompt = response.data[0].revised_prompt
        image_url = response.data[0].url
    except Exception as e:
        await ctx.send(f"Error: {e}")

    global total_cost_since_bot_reboot
    total_cost_since_bot_reboot += 0.04

    await ctx.send(f"{image_url}")
    await ctx.send(
        f"```\n"
        f"{revised_prompt}\n"
        f"-- Image Generation Cost: $0.04 |  Total Cost since bot reboot: ${total_cost_since_bot_reboot:,.2f} --\n"
        f"-- Image URLs will expire after 1 hour. (todo: fix this) --\n.\n"
        f"```\n")
    return None


@bot.command(name="info")
async def draw(ctx):
    await ctx.send(
        f"I'm BasedBot! I run DALLE-3.\n"
        f"We can only run one image at a time.\n"
        f"Max prompt length: 1000 characters.\n"
        f"https://cookbook.openai.com/articles/what_is_new_with_dalle_3\n"
    )
    return None







# ---------------- We probably won't use this ----------------

@bot.event
async def on_message(message):
    # Make sure the Bot doesn't respond to its own messages
    if message.author == bot.user: 
        return None
    
    # Check if the message is in the "basedbot" channel
    if message.channel.name == 'basedbot':
        pass
        # await message.channel.send(f"echo: {message.content}")

    await bot.process_commands(message)

bot.run(DISCORD_BOT_TOKEN)

