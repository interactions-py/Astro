import os
import typing
from pathlib import Path

import interactions as ipy
import yaml

__all__ = ("ASTRO_COLOR", "SRC_PATH", "LanguageRole", "MetadataTyping", "METADATA")

ASTRO_COLOR = ipy.Color(0x5865F2)

# we want to be absolutely sure this path is correct, so we
# do a bit of complicated path logic to get the src folder
SRC_PATH = Path(__file__).parent.parent.absolute().as_posix()


class LanguageRole(typing.TypedDict):
    id: int
    emoji: str


class MetadataTyping(typing.TypedDict):
    guild: int
    roles: dict[str, int]
    language_roles: dict[str, LanguageRole]
    channels: dict[str, int]
    autogenerated_tag: int


METADATA_PATH = os.environ.get("METADATA_PATH", f"{SRC_PATH}/metadata.yml")
with open(METADATA_PATH, "r") as file:
    METADATA: MetadataTyping = yaml.safe_load(file)
