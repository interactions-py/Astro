import dotenv
import os

global TOKEN
global EXTENSIONS
global METADATA
global MONGO_DB_URL
global TAGS_ID
global MOD_ID

MOD_ID = "MODERATION"
TAGS_ID = "TAGS"
TOKEN = dotenv.get_key("../.env", "token")
MONGO_DB_URL = dotenv.get_key("../.env", "MONGO_DB_URL")
EXTENSIONS = [file.replace(".py", "") for file in os.listdir("exts") if not file.startswith("_")]
METADATA = {
    "guild": 789032594456576001,
    "roles": {
        "Changelog pings": 789773555792740353,
        "External Changelog pings": 989950290927190117,
        "Helper": 818861272484806656,
        "Moderator": 789041109208793139,
        "한국어": {"id": 791532197281529937, "emoji": "🇰🇷"},
        "Русский": {"id": 823502288726261781, "emoji": "🇷🇺"},
        "Deutsch": {"id": 853004334945796149, "emoji": "🇩🇪"},
        "Français": {"id": 876494510723588117, "emoji": "🇫🇷"},
        "हिंदी": {"id": 876854835721429023, "emoji": "🇮🇳"},
        "Italiano": {"id": 880657156213461042, "emoji": "🇮🇹"},
        "Polskie": {"id": 880657302812766209, "emoji": "🇵🇱"},
        "Español": {"id": 905859809662889994, "emoji": "🇪🇸"},
        "Україна": {"id": 959472357414666250, "emoji": "🇺🇦"},
    },
    "channels": {
        "information": 789033206769778728,
        "help": 898281873946579034,
        "helpers": 820672900583522335,
        "action-logs": 789041087149899796,
        "mod-logs": 808734093754892358,
    },
}
