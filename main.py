#!/usr/bin/env python3

import discord
from discord.ext import commands
import asyncio
import time
import yaml


from src.load_config import DISCORD_BOT_TOKEN, DISCORD_BOT_CHANNEL_ID


# Init the bot server/client
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ---------------------------- Global variables ----------------------------


bot_globals = {
    "total_cost_since_bot_reboot": 0.0,
    "queue": asyncio.Queue(maxsize=3),
    "total_cost_since_bot_reboot": 0.0,
    "total_credits": 53.0,
}


# This runs at login (on_ready)
@bot.event
async def on_ready():
    print(f'{bot.user} successfully logged in!')
    channel = bot.get_channel(DISCORD_BOT_CHANNEL_ID) # basedbot channel
    # await channel.send(f'{bot.user} rebooted!')
    bot.loop.create_task(dalle_loop())



async def dalle_loop():
    channel_id = DISCORD_BOT_CHANNEL_ID
    channel = bot.get_channel(channel_id)
    while True:

        prompt_obj = await bot_globals["queue"].get()

        prompt = prompt_obj["prompt"]
        first_ten_chars = prompt[:10] if prompt else ""

        await channel.send(f"processing job: {first_ten_chars}...\n")

        async with channel.typing():
            revised_prompt = ""
            image_url = ""
            try:
                revised_prompt, image_url = await run_dalle(
                    model=prompt_obj["model"],
                    prompt=prompt_obj["prompt"],
                    size=prompt_obj["size"],
                    quality=prompt_obj["quality"],
                )
            except Exception as e:
                await channel.send(f"Error: {e}")

        bot_globals["total_cost_since_bot_reboot"] += prompt_obj["cost"]
        bot_globals["total_credits"] -= prompt_obj["cost"]
        
        await channel.send(f"{image_url}") # This HAS to be in its own send call
        await channel.send(
            f"```\n"
            f"- cost: ${prompt_obj['cost']:.2f}, total_cost since reboot: ${bot_globals['total_cost_since_bot_reboot']:.2f}\n"
            f"- credits_remaining: ${bot_globals['total_credits']:.2f}\n"
            f"- img urls expire after 1 hour\n"
            f".\n"
            f"{revised_prompt}\n"
            f"```\n"
        )
        await asyncio.sleep(0.1)



# ------------------------------- Commands  ---------------------------------

@bot.command(name="drawlow")
async def drawlow(ctx, *, prompt: str = None):

    # Make sure there's a prompt
    if not prompt:
        await ctx.send("Error: no prompt")
        return None
    
    # Make sure the queue isn't full
    qsize = bot_globals["queue"].qsize()
    # this doesnt work wtf
    # await ctx.send(f"Queue size: {qsize}\n")
    if qsize >= 3:
        await ctx.send("Error: queue full")
        return None
    
    # Create and add the prompt object to the queue
    prompt_obj = {"model": "dall-e-2", "prompt": prompt, 
                  "size": "1024x1024", "quality": "standard",
                  "cost": 0.02}
    
    first_ten_chars = prompt[:10] if prompt else ""
    await ctx.send(f"Adding prompt to queue(n={qsize+1}): {first_ten_chars}...\n")
    await bot_globals["queue"].put(prompt_obj)



@bot.command(name="drawhigh")
async def drawlow(ctx, *, prompt: str = None):

    # Make sure there's a prompt
    if not prompt:
        await ctx.send("Error: no prompt")
        return None
    
    # Make sure the queue isn't full
    qsize = bot_globals["queue"].qsize()
    # await ctx.send(f"Queue size: {qsize}\n")
    if qsize >= 3:
        await ctx.send("Error: queue full")
        return None
    
    # Create and add the prompt object to the queue
    prompt_obj = {"model": "dall-e-3", "prompt": prompt, 
                  "size": "1792x1024", "quality": "hd",
                  "cost": 0.12}
    
    first_ten_chars = prompt[:10] if prompt else ""
    await ctx.send(f"Adding prompt to queue(n={qsize+1}): {first_ten_chars}...\n")
    await bot_globals["queue"].put(prompt_obj)



@bot.command(name="draw")
async def draw(ctx, *, prompt: str = None):
    await ctx.send(f"try using !drawlow (dalle2) or !drawhigh (dalle3)")



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
        # await message.channel.send(f"{message.channel.id}")
        # await message.channel.send(f"echo: {message.content}")

    await bot.process_commands(message)

bot.run(DISCORD_BOT_TOKEN)

