#!/usr/bin/env python3

import discord
import asyncio
import time
import yaml
from pprint import pformat, pprint
import functools

from src.load_config import DISCORD_BOT_TOKEN, DISCORD_BOT_CHANNEL_ID
from src.schema import DalleRequest, DalleRequestLow, DalleRequestHigh, DalleRequestTest
from src.dalle import run_dalle_1

# Concurrency paradigms:
# - asyncio: async/await
# - threading: threading.Thread
# - threading: concurrent.futures.ThreadPoolExecutor
# - CSP: queue.Queue?


# What the hell is going on with this discord.py library. All behavior is
# abstracted to obscurity and the source code is borderline unreadable.
#
# We chose to use discord.Client instead of discord.bot because discord.bot
# uses even more syntactic "sugar" and further obscures the underlying logic.
#
# God have mercy on the poor souls who venture into discord.py source code.
#

q1 = asyncio.Queue(maxsize=3)

class BasedBotClient(discord.Client):
    """https://discordpy.readthedocs.io/en/stable/api.html#client"""

    # meh do we want to inherit...?
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.queue = asyncio.Queue()

    async def on_ready(self):
        """This runs when the bot logs in"""
        print('Logged on as', self.user)
        channel = self.get_channel(DISCORD_BOT_CHANNEL_ID)

        async def my_loop():
            # this allows us to hot reload the loop body with jurigged
            while True:
                await self.iterate_once()

        self.loop.create_task(my_loop())


    async def iterate_once(self):
        channel = self.get_channel(DISCORD_BOT_CHANNEL_ID)
        
        # print(f"{time.time()}> iterating. qsize={q1.qsize()}")

        # make the bot show that it's typing
        # async with channel.typing():
        #     await asyncio.sleep(1)

        # consume an item from the queue
        try:
            item: DalleRequest = q1.get_nowait()
        except asyncio.QueueEmpty:
            await asyncio.sleep(0.1)
            return None
        
        print(f"consumed item from queue: {item.prompt}")

        # get the response in another thread
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, lambda: run_dalle_1(item))

        await channel.send(f"{result.url}")
        await channel.send(
            f"```\n"
            f"revised_prompt: {result.revised_prompt}\n"
            f"```\n"
        )
        await asyncio.sleep(0.1)


    async def on_message(self, message):
        """This runs every time a message is sent in the server"""
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'ping':
            await message.channel.send('pong')

        if message.content.startswith("!info"):
            await message.channel.send(
                f"```\n"
                f"commands: !info, !ping, !dalletest, !dallelow, !dallehigh\n"
                f"total_credits: NotImplementedError\n"
                f"qsize={q1.qsize()}\n"
                f"```\n"
            )

        # TODO: make this more friendly (match/case?)
        if message.content.startswith('!dalletest '):
            msg = message.content.replace('!dalletest ', '')
            item = DalleRequestTest(prompt=msg, response_format="url")
            try:
                q1.put_nowait(item)
            except asyncio.QueueFull:
                await message.channel.send(
                    f"```\n"
                    f"queue is full. wait for jobs to finish.\n"
                    f"qsize={q1.qsize()}\n"
                    f"```\n"
                )
                return None
            await message.channel.send(
                f"```\n"
                f"added prompt: {item.prompt}\n"
                f"cost: {item.cost}\n"
                f"qsize={q1.qsize()}\n"
                f"```\n"
            )

        if message.content.startswith('!dallelow '):
            msg = message.content.replace('!dallelow ', '')
            item = DalleRequestLow(prompt=msg, response_format="url")
            try:
                q1.put_nowait(item)
            except asyncio.QueueFull:
                await message.channel.send(
                    f"```\n"
                    f"queue is full. wait for jobs to finish.\n"
                    f"qsize={q1.qsize()}\n"
                    f"```\n"
                )
                return None
            await message.channel.send(
                f"```\n"
                f"added prompt: {item.prompt}\n"
                f"cost: {item.cost}\n"
                f"qsize={q1.qsize()}\n"
                f"```\n"
            )
        
        if message.content.startswith('!dallehigh '):
            msg = message.content.replace('!dallehigh ', '')
            item = DalleRequestHigh(prompt=msg, response_format="url")
            try:
                q1.put_nowait(item)
            except asyncio.QueueFull:
                await message.channel.send(
                    f"```\n"
                    f"queue is full. wait for jobs to finish.\n"
                    f"qsize={q1.qsize()}\n"
                    f"```\n"
                )
                return None
            await message.channel.send(
                f"```\n"
                f"added prompt: {item.prompt}\n"
                f"cost: {item.cost}\n"
                f"qsize={q1.qsize()}\n"
                f"```\n"
            )
                


intents = discord.Intents.default()
intents.message_content = True
client = BasedBotClient(intents=intents)
client.run(DISCORD_BOT_TOKEN)
