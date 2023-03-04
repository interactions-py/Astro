import enum
import typing
from datetime import datetime

from beanie import Document, Indexed

__all__ = "Tag"


class Tag(Document):
    name: typing.Annotated[str, Indexed(str)]
    author_id: str
    description: str
    created_at: datetime
    last_edited_at: typing.Optional[datetime] = None
