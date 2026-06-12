# data/settings.py
# This file stores all user preferences

# @TristanofJugdral (Ver. 1.3.3 | 11 June 2026)

import json
import os
import time

# Store data
CONFIG_FILE = "config.json"

# Bot behaviour settings
settings = {
    # Message toggles
    "showPlayerMessages": True,
    "showSystemMessages": True,
    "anonymousMode": False,
    "censorEnabled": True,

    # Notification toggles
    "showSpawns": True,
    "showDespawns": True,
    "showCaptures": True,
    "showLegendary": True,
    "showUltraBeast": True,
    "showParadox": True,
    "showShiny": True,
}

# Any PLAYER messages with these words will not send when censor is on
FILTERED_PLAYER = [
    "nigger",
    "niggers",
    "nigga",
    "niggas",
]

# Any SYSTEM messages with these words will not send when censor is on
FILTERED_SYSTEM = [
    "fainting",
]



# Load persistent config from config.json
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {}

# Create config.json
def save_config():
    with open(CONFIG_FILE, "w") as file:
        json.dump({
            "CHANNEL_ID": CHANNEL_ID,
            "SFTP_HOST": SFTP_HOST,
            "SFTP_PORT": SFTP_PORT,
            "SFTP_USERNAME": SFTP_USERNAME,
            "SFTP_PASSWORD": SFTP_PASSWORD,
            "AUTHORISED_ROLES": AUTHORISED_ROLES,
            "LOG_PATH": LOG_PATH,
            "SFTP_LOG_PATH": SFTP_LOG_PATH,
        }, file, indent=4)

# ==== Load saved values OR use defaults ====
start_time = time.time()
_config = load_config()
CHANNEL_ID = _config.get("CHANNEL_ID", None)

# SFTP
SFTP_HOST = _config.get("SFTP_HOST", None)
SFTP_PORT = _config.get("SFTP_PORT", 2022) # Check this in server IP
SFTP_USERNAME = _config.get("SFTP_USERNAME", None)
SFTP_PASSWORD = _config.get("SFTP_PASSWORD", None)
AUTHORISED_ROLES = _config.get("AUTHORISED_ROLES", [])

# PATH ~ e.g, LOG_PATH = r"C:\Users\MyName\curseforge\minecraft\Instances\COBBLEVERSE - Pokemon Adventure [Cobblemon]\logs\latest.log"
LOG_PATH = _config.get("LOG_PATH", None)
SFTP_LOG_PATH = _config.get("SFTP_LOG_PATH", "/logs/latest.log")
