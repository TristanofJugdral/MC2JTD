# cogs/sftp_reader.py
# Connects to BisectHosting and reads Minecraft logs remotely

# Creator: @TristanofJugdral (Ver. 1.1.3 | 8 June 2026)

import paramiko     # .SSHClient() and .AutoAddPolicy()
import asyncio
import re
from discord.ext import commands
import data.settings as config
from utils.censor_words import censor_message

class SFTPReader(commands.Cog):
    def __init__(self, bot):        
        self.bot = bot
        self.watch_task = None      # Background task that reads the log
        self.ssh_client = None      # SSH connection to BisectHosting
        self.sftp_client = None     # SFTP file browser on top of SSH
        self.remote_file = None     # Log file we're reading
        self.connected = False      # Connection status tracker
        self._credentials_warned = False # Check if error has already a warning message
        self._connect_attempts = 0  # Number of attempts to connect
        self._last_connect_error = None # Error message

    async def cog_load(self): # Start watching
        self.watch_task = asyncio.create_task(self.watch_log())

    async def cog_unload(self):
        # ...clean up once the cog is unloaded
        if self.watch_task:
            self.watch_task.cancel()
        self.disconnect()

    def connect(self):
        """
        Connects to BisectHosting using SFTP
        
        SSH = the secure tunnel
        SFTP = file transfer running inside the tunnel
        
        Placeholder credentials (in config):
        SFTP_HOST = "node123.bisecthosting.com" ← your server's address
        SFTP_PORT = 2022                        ← BisectHosting's SFTP port
        SFTP_USERNAME = "your_username"         ← your BisectHosting username
        SFTP_PASSWORD = "your_password"         ← your BisectHosting password
        SFTP_LOG_PATH = "/logs/latest.log"      ← path to log on their server
        """
        try:
            self.ssh_client = paramiko.SSHClient()

            # paramiko.AutoAddPolicy() = Automatically trust BisectHosting's server identity
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.ssh_client.connect(
                hostname=config.SFTP_HOST.strip(),
                port=config.SFTP_PORT,
                username=config.SFTP_USERNAME,
                password=config.SFTP_PASSWORD,
                timeout=10  # ...give up after 10 seconds
            )

            # Open SFTP session on top of SSH connection and remote file for reading
            self.sftp_client = self.ssh_client.open_sftp()
            self.remote_file = self.sftp_client.open(config.SFTP_LOG_PATH, "r")
            self.remote_file.seek(0, 2) # (Go to the end of the file)
            self.connected = True
            print(f"SFTP connected to {config.SFTP_HOST}")
            return True
        # E.1
        except Exception as e:
            self._last_connect_error = e
            self.connected = False
            return False

    def disconnect(self):
        """
        Cleanly closes all connections.
        Always close connections you open — like turning off a tap!
        """
        try: # close all available files: 
            if self.remote_file:
                self.remote_file.close()
            if self.sftp_client:
                self.sftp_client.close()
            if self.ssh_client:
                self.ssh_client.close()
            self.connected = False
            print("SFTP successfully disconnected")
        # E.2
        except Exception as e:
            self._last_connect_error = e
            self.connected = False
            return False

    async def watch_log(self):
        """
        Main loop — continuously reads new lines from the remote log file.
        Runs as a background task the entire time the bot is running.
        """
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():

            # Wait until credentials are configured
            # if (!HOST || !USERNAME || !PASSWORD || !LOG_PATH) {
            if not config.SFTP_HOST or not config.SFTP_USERNAME or not config.SFTP_PASSWORD or not config.SFTP_LOG_PATH:
                await asyncio.sleep(5)
                continue

            # Connect if it is not already connected
            if not self.connected:
                if not self.connect():
                    self._connect_attempts += 1
                    
                    if self._connect_attempts <= 3:
                        print(f"SFTP connection failed: {self._last_connect_error} | Attempt {self._connect_attempts}/3")

                    await asyncio.sleep(10)
                    continue
                
            self._connect_attempts = 0  # Reset afterwards
                
            try:
                while not self.bot.is_closed():
                    channel = self.bot.get_channel(config.CHANNEL_ID)

                    # LINE and CHANNEL check: 
                    line = self.remote_file.readline()
                    if line:
                        if channel is None:
                            await asyncio.sleep(2)
                            continue
                        await self.process_line(line, channel)
                        
                    await asyncio.sleep(0.5)
            # E.3
            except Exception as e:
                print(f"SFTP read error: {e}")
                self.disconnect()
                await asyncio.sleep(5)  # Wait a bit before reconnecting

    async def process_line(self, line, channel): # Actually read message
        """
        Processes a single log line and sends to Discord if relevant.
        Identical logic to msg_receive.py — just the source of lines differs.
        """
        # Read PLAYER messages
        # Pattern: [CHAT] <Name> Hello!
        playerMatch = re.search(r'\[CHAT\] <(\w+)> (.+)', line)
        if playerMatch and config.settings["showPlayerMessages"]:

            # NAME (anonymous check)
            username = playerMatch.group(1)
            if config.settings["anonymousMode"]:
                username = ""
                
            # MESSAGE (censor check)
            message = playerMatch.group(2)
            if config.settings["censorEnabled"]:
                message = censor_message(message, config.FILTERED_PLAYER)
                
            await channel.send(f"**{username}**: {message}")

        # Read SYSTEM messages - (Pokemon spawns, captures, etc.)
        # Pattern: [System] [CHAT] The Shiny Ralts spawned...
        systemMatch = re.search(r'\[System\] \[CHAT\] (.+)', line)

        if systemMatch and config.settings["showSystemMessages"]:
            message = systemMatch.group(1)

            # Remove Minecraft colour codes like §6 §r
            message = re.sub(r'§.', '', message)

            # Censor (if allowed)
            if config.settings["censorEnabled"]:
                message = censor_message(message, config.FILTERED_SYSTEM)

            # Check notification event type
            eventAllowed = False
            
            if "spawned" in message and config.settings["showSpawns"]:
                eventAllowed = True
            elif "despawned" in message and config.settings["showDespawns"]:
                eventAllowed = True
            elif "captured" in message and config.settings["showCaptures"]:
                eventAllowed = True

            if not eventAllowed:
                return

            shinyIcon = ""
            rarityIcon = ""
            
            presentTraits = [] # Present categories go here

            # Shiny category
            if "Shiny" in message:
                shinyIcon = "✨"
                presentTraits.append("showShiny")

            # Rarity categories
            if "Legendary" in message:
                rarityIcon = "🔴"
                presentTraits.append("showLegendary")
                
            elif "Ultra Beast" in message:
                rarityIcon = "🟣"
                presentTraits.append("showUltraBeast")
                
            elif "Paradox" in message:
                rarityIcon = "🟡"
                presentTraits.append("showParadox")

            # Send if any matching trait is enabled
            if presentTraits:
                specialAllowed = any(config.settings[key] for key in presentTraits)
            else:
                specialAllowed = True

            if specialAllowed:
                await channel.send(f"{shinyIcon}{rarityIcon} *{message}*")

async def setup(bot):
    await bot.add_cog(SFTPReader(bot))
