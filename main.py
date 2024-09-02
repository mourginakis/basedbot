#!/usr/bin/env python3

import discord
import asyncio
import time
import yaml

from src.load_config import DISCORD_BOT_TOKEN, DISCORD_BOT_CHANNEL_ID

# Concurrency paradigms:
# - asyncio: async/await
# - threading: threading.Thread
# - threading: concurrent.futures.ThreadPoolExecutor
# - CSP?: queue.Queue


# What the hell is going on with this discord.py library. All behavior is
# abstracted to obscurity and the source code is borderline unreadable.
#
# We chose to use discord.Client instead of discord.bot because discord.bot
# uses even more syntactic "sugar" and further obscures the underlying logic.
#
# God have mercy on the poor souls who venture into discord.py source code.
#

class BasedBotClient(discord.Client):

    """https://discordpy.readthedocs.io/en/stable/api.html#client"""


    async def on_ready(self):
        """This runs when the bot logs in"""
        print('Logged on as', self.user)
        channel = self.get_channel(DISCORD_BOT_CHANNEL_ID)

        async def my_loop():
            # jurigged can't update code in a loop body so we make a 
            # 2nd function call here.
            while True:
                await self.iterate_once()

        self.loop.create_task(my_loop())


    async def iterate_once(self):
        channel = self.get_channel(DISCORD_BOT_CHANNEL_ID)
        async with channel.typing():
            # typing example
                await asyncio.sleep(1)
            
        # send an example message to the channel
        await channel.send(f"timep: {time.time()}")
        await asyncio.sleep(5)

    async def on_message(self, message):
        """This runs every time a message is sent in the server"""
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'ping':
            await message.channel.send('pong')

        if message.content.startswith('!dalletest'):
            await message.channel.send('dalle test')


intents = discord.Intents.default()
intents.message_content = True
client = BasedBotClient(intents=intents)
client.run(DISCORD_BOT_TOKEN)
