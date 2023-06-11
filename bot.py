import os
import importlib
import logging
import discord
from discord.utils import find
from config.settings import DISCORD_TOKEN

logging.basicConfig(level=logging.INFO)
logging.getLogger('discord').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

commands = {}

commands['setchannel'] = importlib.import_module('commands.setchannel')


for filename in os.listdir('./commands'):
    if filename.endswith('.py'):
        commands[filename[:-3]] = importlib.import_module(f'commands.{filename[:-3]}')

async def send_message(message, user_message):
    try:
        if user_message.startswith('!'):
            command = user_message[1:].lower()
            if command in commands:
                await commands[command].execute(message, [])
    except Exception as e:
        logging.error(e)


def run_discord_bot():
    TOKEN = DISCORD_TOKEN
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')

    @client.event
    async def on_guild_join(guild):
        print(f'{client.user} has joined {guild.name}!')
        channel = guild.system_channel
        if channel is None or not channel.permissions_for(guild.me).send_messages:
            # If the bot can't send messages in the system channel, find another one
            channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
        if channel is not None:
            await channel.send('Hello {}!'.format(guild.name))
            await channel.send('Please setup a channel for signals with !setchannel <channel_id>')

    @client.event
    async def on_message(message):
        # check if the message is from the bot itself
        if message.author == client.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username}: {user_message} ({channel})')

        if user_message.startswith('!'):
            # split the user message into command and arguments
            command = user_message[1:].lower().split(' ')[0]
            args = user_message[1:].lower().split(' ')[1:]

            # Check if the command exists in the commands dictionary
            if command in commands:
                module = commands[command]
                await module.execute(message, args)
            else:
                await send_message(message, user_message)
        else:
            await send_message(message, user_message)

    client.run(TOKEN)

