# MAIN - MC2JTD
# Creator: @TristanofJugdral

import discord
from discord.ext import commands
import asyncio
import os

TOKEN = input("Enter your Discord bot token: ").strip()

intents = discord.Intents.default()
intents.message_content = True # read chat
bot = commands.Bot(
    command_prefix="mc2jtd.", # prefix: mc2jtd.
    intents=intents,
    help_command=None
) 


# Load cogs
async def load_cogs():
    
    # Receive and send messages from server
    await bot.load_extension("cogs.msg_receive")
    print("Loaded cogs/msg_receive.py")
    
    # Basic commands
    await bot.load_extension("cogs.basic_commands")
    print("Loaded cogs/basic_commands.py")

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    # await load_cogs()
    # await bot.tree.sync() # this is for slash-commands. Atm we're using prefixes
# bot.run(TOKEN)

# Note: Make sure to load the "cogs" files before starting the bot up
async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())
