from pyrogram.types import Message

MEDIA_ATTRS = ("video", "document", "audio", "animation", "voice", "video_note")


def get_media(message: Message):
    for attr in MEDIA_ATTRS:
        media = getattr(message, attr, None)
        if media:
            return media
    return None


def get_name(message: Message) -> str:
    media = get_media(message)
    if not media:
        return "file"
    return getattr(media, "file_name", None) or f"{media.file_unique_id}.bin"


def get_hash(message: Message) -> str:
    media = get_media(message)
    return media.file_unique_id[:6] if media else ""


def get_media_file_size(message: Message) -> int:
    media = get_media(message)
    return getattr(media, "file_size", 0) or 0


def get_mime(message: Message) -> str:
    media = get_media(message)
    return getattr(media, "mime_type", None) or "application/octet-stream"
