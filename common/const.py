import typing
from pathlib import Path

import naff
import yaml

ASTRO_COLOR = naff.Color(0x5865F2)

# we want to be absolutely sure this path is correct, so we
# do a bit of complicated path logic to get the src folder
SRC_PATH = Path(__file__).parent.absolute().as_posix()


class LanguageRole(typing.TypedDict):
    id: int
    emoji: str


class MetadataTyping(typing.TypedDict):
    guild: int
    roles: dict[str, int]
    language_roles: dict[str, LanguageRole]
    channels: dict[str, int]


with open(f"{SRC_PATH}/metadata.yml", "r") as file:
    METADATA: MetadataTyping = yaml.safe_load(file)
