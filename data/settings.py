# This file stores all user preferences:
import json
import os

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
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump({
            "CHANNEL_ID": CHANNEL_ID,
            "LOG_PATH": LOG_PATH,
        }, f, indent=4)

# Load saved values OR use defaults
_config = load_config()
CHANNEL_ID = _config.get("CHANNEL_ID", None)
LOG_PATH = _config.get("LOG_PATH", None)
# EXAMPLE: LOG_PATH = r"C:\Users\MyName\curseforge\minecraft\Instances\COBBLEVERSE - Pokemon Adventure [Cobblemon]\logs\latest.log"
