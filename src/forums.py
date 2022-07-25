from interactions import MISSING, File, Route, WebSocketClient, Client as _Client, InteractionType
from typing import List, Optional, Dict, Tuple, Any
from aiohttp import MultipartWriter


def monkeypatch(client):
    setattr(client._http, "create_forum_thread", create_thread_in_forum)


class Client(_Client):
    def __init__(self, token, **kwargs):
        super().__init__(token, **kwargs)
        self._websocket: WebSocketClient = ModalSelectWebSocketClient(token=token, intents=self._intents)


class ModalSelectWebSocketClient(WebSocketClient):

    def _dispatch_event(self, event: str, data: dict) -> None:
        # sourcery skip: extract-method, merge-nested-ifs
        if (event == "INTERACTION_CREATE" and data.get("type") and data["type"] != InteractionType.MODAL_SUBMIT) or event != "INTERACTION_CREATE":
            super()._dispatch_event(event, data)
        elif data.get("type"):
            self._dispatch.dispatch("raw_socket_create", data)
            path: str = "interactions"
            path += ".models" if event == "INTERACTION_CREATE" else ".api.models"
            _context = self._WebSocketClient__contextualize(data)
            _name: str = ""
            __args: list = [_context]
            __kwargs: dict = {}

            _name = f"modal_{_context.data.custom_id}"

            if _context.data._json.get("components"):
                for component in _context.data.components:
                    if component.get("components"):
                        for _value in component["components"]:
                            if _value.get("value"):
                                __args.append(_value["value"])
                            if _value.get("values"):
                                __args.append(_value["values"])
                    else:
                        __args.append([_value.value for _value in component.components][0])

            self._dispatch.dispatch("on_modal", _context)

            self._dispatch.dispatch(_name, *__args, **__kwargs)
            self._dispatch.dispatch("on_interaction", _context)
            self._dispatch.dispatch("on_interaction_create", _context)


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

