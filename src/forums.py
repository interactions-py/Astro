from interactions import MISSING, File, Route
from typing import List, Optional
from aiohttp import MultipartWriter


def monkeypatch(client):
    setattr(client._http, "create_forum_thread", create_thread_in_forum)


async def create_thread_in_forum(
    self,
    channel_id: int,
    name: str,
    auto_archive_duration: int,
    message_payload: dict,
    applied_tags: List[str] = None,
    files: Optional[List[File]] = MISSING,
    rate_limit_per_user: Optional[int] = None,
    reason: Optional[str] = None,
) -> dict:
    """
    From a given Forum channel, create a Thread with a message to start with.
    :param channel_id: The ID of the channel to create this thread in
    :param name: The name of the thread
    :param auto_archive_duration: duration in minutes to automatically archive the thread after recent activity,
        can be set to: 60, 1440, 4320, 10080
    :param message_payload: The payload/dictionary contents of the first message in the forum thread.
    :param files: An optional list of files to send attached to the message.
    :param rate_limit_per_user: Seconds a user has to wait before sending another message (0 to 21600), if given.
    :param reason: An optional reason for the audit log
    :return: Returns a Thread in a Forum object with a starting Message.
    """
    query = {"has_message": "True"}  # TODO: Switch query after new feature breaking release.

    payload = {"name": name, "auto_archive_duration": auto_archive_duration}
    if rate_limit_per_user:
        payload["rate_limit_per_user"] = rate_limit_per_user
    if applied_tags:
        payload["applied_tags"] = applied_tags

    # payload.update(**{'use_nested_fields': 1})

    data = None
    if files is not MISSING and len(files) > 0:

        data = MultipartWriter("form-data")
        part = data.append_json(payload)
        part.set_content_disposition("form-data", name="payload_json")
        payload = None

        for id, file in enumerate(files):
            part = data.append(
                file._fp,
            )
            part.set_content_disposition(
                "form-data", name=f"files[{str(id)}]", filename=file._filename
            )
    else:
        payload.update(message_payload)

    return await self._req.request(
        Route("POST", f"/channels/{channel_id}/threads?has_message=True"),
        json=payload,
        data=data,
        params=query,
        reason=reason,
    )

