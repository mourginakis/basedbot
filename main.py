#!/usr/bin/env python3

import io
import base64
import discord
import asyncio
import time
import yaml
from pprint import pformat, pprint
import functools
from dataclasses import dataclass
from src.load_config import DISCORD_BOT_TOKEN, DISCORD_BOT_CHANNEL_ID, DISCORD_BOT_CHANNEL_ID_CHAT
from src.schema import DalleRequest, DalleRequestLow, DalleRequestHigh, DalleRequestTest
from src.dalle import run_dalle_1
from src.chatgpt import gpt4o_memory, gpt4o1_memory, gptimage1

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


@dataclass
class GptImageRequest:
    """Request a GPT image"""
    prompt: str
    quality: str



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

        # consume an item from the queue
        try:
            item = q1.get_nowait()
        except asyncio.QueueEmpty:
            await asyncio.sleep(0.1)
            return None
        
        print(f"consumed item from queue: {item.prompt}")

        # make the bot show that it's typing (this doesn't really work too well)
        async with channel.typing():
            # get the response in another thread
            loop = asyncio.get_running_loop()

            if isinstance(item, DalleRequest):
                result = await loop.run_in_executor(None, lambda: run_dalle_1(item))
                await channel.send(f"{result.url}")

            elif isinstance(item, GptImageRequest):
                try:
                    result = await loop.run_in_executor(None, lambda: gptimage1(item.prompt, item.quality))
                    await channel.send(file=discord.File(io.BytesIO(result), filename="image.png"))
                except Exception as e:
                    await channel.send(f"❌ Error generating image: {e}")

            # result = await loop.run_in_executor(None, lambda: run_dalle_1(item))

        # await channel.send(f"{result.url}")

        # how to send b64 images
        # not_needed = "data:image/png;base64," + "" # what is this for?
        # b64img = "iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAAESUlEQVR4Ae3Bzes49gAH8PfevrHUEElNrclTTUpEI4cfK2UHioOkHWw4acdhFO1nReawdlIuSK2tbGurJW5CsZVmFw8H5aHtoLHUHpL5Mz6H9+v1uuLer93zUg664cVf5aQ3P/TVnPSefjMnffd1j+akm+99X076+9W/zUlXvfu6nNQAsxpgVgPMaoBZDTCrAWY1wKwGmNUAsxpgVgPMaoBZDTCrAWY1wKwGmNUAsxpgVgPMaoBZDTCrAWY1wKwGmNUAsxpgVgPMaoBZDTCrAWY1wKyLr//l6Zz08g/+Oyfd+JMv5qQ/PfNMTnq8N+akj950a0767FfuzEkPP/mOnNQAsxpgVgPMaoBZDTCrAWY1wKwGmNUAsxpgVgPMaoBZDTCrAWY1wKwGmNUAsxpgVgPMaoBZDTCrAWY1wKwGmNUAsxpgVgPMaoBZDTCrAWY1wKyLV9z1YE568tr7c9Idl27JSS/c/kxOuvanv8tJ3/jDP3PSF26/LSfd+aPP5KQGmNUAsxpgVgPMaoBZDTCrAWY1wKwGmNUAsxpgVgPMaoBZDTCrAWY1wKwGmNUAsxpgVgPMaoBZDTCrAWY1wKwGmNUAsxpgVgPMaoBZDTCrAWZdvP/hJ3LSc5ceykn3Pf/jnPSua+7OSa+/44Gc9MjVX85Jb7z06Zx08ezlnNQAsxpgVgPMaoBZDTCrAWY1wKwGmNUAsxpgVgPMaoBZDTCrAWY1wKwGmNUAsxpgVgPMaoBZDTCrAWY1wKwGmNUAsxpgVgPMaoBZDTCrAWY1wKyLWz/8kZz0vSd+k5Nue/C/OenSO5/OSVf98vc56dVvuy8n/e/PT+ekm5/6R05qgFkNMKsBZjXArAaY1QCzGmBWA8xqgFkNMKsBZjXArAaY1QCzGmBWA8xqgFkNMKsBZjXArAaY1QCzGmBWA8xqgFkNMKsBZjXArAaY1QCzGmDWxSOvfVlOunzNz3PSm37wnxz13E056QO/+FhOeva2f+Wkv17ckJOu/PjjOakBZjXArAaY1QCzGmBWA8xqgFkNMKsBZjXArAaY1QCzGmBWA8xqgFkNMKsBZjXArAaY1QCzGmBWA8xqgFkNMKsBZjXArAaY1QCzGmBWA8xqgFkX133rNTnp8i3X56RX3f3HnHT/Y5/MSe99w/U56e1PvTUn/fpT385J37n28zmpAWY1wKwGmNUAsxpgVgPMaoBZDTCrAWY1wKwGmNUAsxpgVgPMaoBZDTCrAWY1wKwGmNUAsxpgVgPMaoBZDTCrAWY1wKwGmNUAsxpgVgPMaoBZV9zz/b+9lIPe8sAjOenRH96Rk55/7MWc9IkPPZiTvvSzK3PSC/lcTnrl7XflpAaY1QCzGmBWA8xqgFkNMKsBZjXArAaY1QCzGmBWA8xqgFkNMKsBZjXArAaY1QCzGmBWA8xqgFkNMKsBZjXArAaY1QCzGmBWA8xqgFkNMKsBZv0fOZRkC3kHXSEAAAAASUVORK5CYII="
        # await channel.send(file=discord.File(io.BytesIO(base64.b64decode(b64img)), filename="image.png"))

        # await channel.send(
        #     f"```\n"
        #     f"revised_prompt: {result.revised_prompt}\n"
        #     f"```\n"
        # )
        await asyncio.sleep(0.1)


    async def on_message(self, message):
        """This runs every time a message is sent in the server"""
        # don't respond to ourselves
        if message.author == self.user:
            return None

        if message.content == 'ping':
            await message.channel.send('pong')
            return None

        if message.content.startswith("!info"):
            await message.channel.send(
                f"```\n"
                f"commands: !info, !ping, !dalletest, !dallelow, !dallehigh\n"
                f"more_commands: !gptimglow !gptimgmed !gptimghigh\n"
                f"total_credits: NotImplementedError\n"
                f"this channel.id: {message.channel.id}\n"
                f"qsize={q1.qsize()}\n"
                f"```\n"
            )
            return None
        
        if message.channel.id == DISCORD_BOT_CHANNEL_ID:
            pass

        if message.channel.id == DISCORD_BOT_CHANNEL_ID_CHAT:

            if message.content.startswith('!ignore '):
                return None

            # TODO: make this asynchronous or use CSP and another thread
            await message.channel.send("🐧💭")
            msg = message.content
            response = gpt4o_memory(msg)
            # repeat the first 10 characters of the prompt
            concatted = msg[:10] if msg else ""
            await message.channel.send(
                f"```\n"
                f"{response}\n"
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
            return None

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
            return None
        
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
            return None
        
        if message.content.startswith('!gptimglow '):
            msg = message.content.replace('!gptimglow ', '')
            item = GptImageRequest(prompt=msg, quality="low")
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
                f"cost: $0.011\n"
                f"qsize={q1.qsize()}\n"
                f"```\n"
            )
            return None
        
        if message.content.startswith('!gptimgmed '):
            msg = message.content.replace('!gptimgmed ', '')
            item = GptImageRequest(prompt=msg, quality="medium")
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
                f"cost: $0.042\n"
                f"qsize={q1.qsize()}\n"
                f"```\n"
            )
            return None
        
        if message.content.startswith('!gptimghigh '):
            msg = message.content.replace('!gptimghigh ', '')
            item = GptImageRequest(prompt=msg, quality="high")
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
                f"cost: $0.167\n"
                f"qsize={q1.qsize()}\n"
                f"```\n"
            )
            return None


intents = discord.Intents.default()
intents.message_content = True
client = BasedBotClient(intents=intents)
client.run(DISCORD_BOT_TOKEN)
