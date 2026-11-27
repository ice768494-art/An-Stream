import time

from info import ADMINS


async def grant(db, uid, days):
    """Grant or extend premium. Returns the new expiry timestamp."""
    current = await db.premium_expiry(uid)
    expires = max(current or 0, time.time()) + days * 86400
    await db.add_premium(uid, expires)
    return expires


async def has_premium(db, uid):
    if uid in ADMINS:
        return True
    return (await db.premium_expiry(uid)) is not None


def fmt_date(ts):
    return time.strftime("%d %b %Y", time.gmtime(ts or 0))
