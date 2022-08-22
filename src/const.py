import os
import pathlib

MOD_ID = "MODERATION"
TAGS_ID = "TAGS"

TOKEN = os.environ["token"]
MONGO_DB_URL = os.environ["MONGO_DB_URL"]

# we want to be absolutely sure this path is correct, so we
# do a bit of complicated path logic to get the src folder
src_path = pathlib.Path(__file__).parent.absolute().as_posix()
EXTENSIONS = [
    file.replace(".py", "")
    for file in os.listdir(f"{src_path}/exts")
    if not file.startswith("_") and not file.startswith("gg")
]

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
        "help": 996211499364262039,
        "helpers": 820672900583522335,
        "action-logs": 789041087149899796,
        "mod-logs": 808734093754892358,
    },
}
