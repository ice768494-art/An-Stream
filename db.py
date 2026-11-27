import json
import os
import time

from info import DATABASE_NAME, DATABASE_URI


class JsonDB:
    """Fallback storage. NOTE: Render wipes local files on every redeploy."""

    def __init__(self, path="data.json"):
        self.path = path
        self.d = {"users": {}, "banned": [], "files": []}
        if os.path.exists(path):
            try:
                with open(path) as f:
                    self.d.update(json.load(f))
            except Exception:
                pass

    def _save(self):
        try:
            with open(self.path, "w") as f:
                json.dump(self.d, f)
        except Exception:
            pass

    async def add_user(self, uid, name=""):
        if str(uid) in self.d["users"]:
            return False
        self.d["users"][str(uid)] = {"name": name, "joined": time.time()}
        self._save()
        return True

    async def remove_user(self, uid):
        self.d["users"].pop(str(uid), None)
        self._save()

    async def total_users(self):
        return len(self.d["users"])

    async def all_user_ids(self):
        return [int(k) for k in self.d["users"]]

    async def recent_users(self, n=10):
        items = sorted(self.d["users"].items(), key=lambda kv: kv[1].get("joined", 0), reverse=True)[:n]
        return [{"id": int(k), "name": v.get("name", ""), "joined": v.get("joined", 0)} for k, v in items]

    async def ban(self, uid):
        if uid not in self.d["banned"]:
            self.d["banned"].append(uid)
            self._save()

    async def unban(self, uid):
        if uid in self.d["banned"]:
            self.d["banned"].remove(uid)
            self._save()

    async def is_banned(self, uid):
        return uid in self.d["banned"]

    async def banned_count(self):
        return len(self.d["banned"])

    async def add_file(self, rec):
        self.d["files"].append(rec)
        self.d["files"] = self.d["files"][-500:]
        self._save()

    async def total_files(self):
        return len(self.d["files"])

    async def recent_files(self, n=10):
        return list(reversed(self.d["files"][-n:]))


class MongoDB:
    def __init__(self, uri, name):
        from motor.motor_asyncio import AsyncIOMotorClient

        database = AsyncIOMotorClient(uri)[name]
        self.users = database.users
        self.banned = database.banned
        self.files = database.files

    async def add_user(self, uid, name=""):
        r = await self.users.update_one(
            {"_id": uid}, {"$setOnInsert": {"name": name, "joined": time.time()}}, upsert=True
        )
        return r.upserted_id is not None

    async def remove_user(self, uid):
        await self.users.delete_one({"_id": uid})

    async def total_users(self):
        return await self.users.count_documents({})

    async def all_user_ids(self):
        return [d["_id"] async for d in self.users.find({}, {"_id": 1})]

    async def recent_users(self, n=10):
        out = []
        async for d in self.users.find().sort("joined", -1).limit(n):
            out.append({"id": d["_id"], "name": d.get("name", ""), "joined": d.get("joined", 0)})
        return out

    async def ban(self, uid):
        await self.banned.update_one({"_id": uid}, {"$set": {"t": time.time()}}, upsert=True)

    async def unban(self, uid):
        await self.banned.delete_one({"_id": uid})

    async def is_banned(self, uid):
        return await self.banned.find_one({"_id": uid}) is not None

    async def banned_count(self):
        return await self.banned.count_documents({})

    async def add_file(self, rec):
        await self.files.insert_one(dict(rec))

    async def total_files(self):
        return await self.files.count_documents({})

    async def recent_files(self, n=10):
        out = []
        async for d in self.files.find().sort("time", -1).limit(n):
            out.append({k: d.get(k) for k in ("msg_id", "name", "size", "user", "time")})
        return out


db = MongoDB(DATABASE_URI, DATABASE_NAME) if DATABASE_URI else JsonDB()
