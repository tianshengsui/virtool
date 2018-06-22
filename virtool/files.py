import asyncio
import logging
import os
import shutil

import aionotify

import virtool.db.files
import virtool.utils

#: Files with these extensions will be consumed from the watch folder and be entered into Virtool's file manager.
FILE_EXTENSION_FILTER = (
    ".fq.gz",
    ".fastq.gz",
    ".fq",
    ".fastq"
)

FILES_FLAGS = (
    aionotify.Flags.CLOSE_WRITE |
    aionotify.Flags.CREATE |
    aionotify.Flags.DELETE |
    aionotify.Flags.MOVED_TO |
    aionotify.Flags.MOVED_FROM
)

WATCH_FLAGS = (
    aionotify.Flags.CLOSE_WRITE |
    aionotify.Flags.MOVED_TO
)

#: A dict for mapping inotify type names of interest to simple file operation verbs used in Virtool.
TYPE_NAME_DICT = {
    "CREATE": "create",
    "MOVED_TO": "move",
    "DELETE": "delete",
    "MOVED_FROM": "delete",
    "CLOSE_WRITE": "close"
}


def get_event_type(event):
    flags = aionotify.Flags.parse(event.flags)

    if aionotify.Flags.CREATE in flags or aionotify.Flags.MOVED_TO in flags:
        return "create"

    if aionotify.Flags.DELETE in flags or aionotify.Flags.MOVED_FROM in flags:
        return "delete"

    if aionotify.Flags.CLOSE_WRITE in flags:
        return "close"


def has_read_extension(filename):
    return any(filename.endswith(ext) for ext in FILE_EXTENSION_FILTER)


class Manager:

    def __init__(self, loop, executor, db, files_path, watch_path, clean_interval=20):
        self.loop = loop
        self.executor = executor
        self.db = db
        self.files_path = files_path
        self.watch_path = watch_path
        self.clean_interval = clean_interval

        self.watcher = aionotify.Watcher()

        self.watcher.watch(self.files_path, FILES_FLAGS, alias="files")
        self.watcher.watch(self.watch_path, WATCH_FLAGS, alias="watch")

    async def run(self):
        coros = [
            self.watch()
        ]

        if self.clean_interval is not None:
            coros.append(self.clean())

        return await asyncio.gather(*coros)

    async def clean(self):
        try:
            while True:
                dir_list = os.listdir(self.files_path)
                db_list = await self.db.files.distinct("_id")

                for filename in dir_list:
                    if filename not in db_list:
                        await self.loop.run_in_executor(
                            self.executor,
                            os.remove,
                            os.path.join(self.files_path, filename)
                        )

                db_created_list = await self.db.files.find({"created": True}).distinct("_id")

                await self.db.files.delete_many({
                    "_id": {
                        "$in": [filename for filename in db_created_list if filename not in dir_list]
                    }
                })

                count = 0
                threshold = self.clean_interval / 0.3

                while count < threshold:
                    await asyncio.sleep(0.3, loop=self.loop)

        except asyncio.CancelledError:
            pass

    async def watch(self):
        await self.watcher.setup(self.loop)

        try:
            while True:
                event = await self.watcher.get_event()

                alias = event.alias
                filename = event.name

                if alias == "watch":
                    await self.handle_watch(filename)

                elif alias == "files":
                    event_type = get_event_type(event)

                    if event_type == "delete":
                        await self.handle_file_deletion(filename)

                    elif event_type == "create":
                        await self.handle_file_creation(filename)

                    elif event_type == "close":
                        await self.handle_file_close(filename)

        except asyncio.CancelledError:
            pass

        logging.debug("Stopped file manager")

    async def handle_watch_close(self, filename):
        path = os.path.join(self.watch_path, filename)

        if has_read_extension(filename):
            document = await virtool.db.files.create(self.db, filename, "reads")

            await self.loop.run_in_executor(
                self.executor,
                shutil.copy,
                path,
                os.path.join(self.files_path, document["id"])
            )

        await self.loop.run_in_executor(
            self.executor,
            os.remove,
            path
        )

    async def handle_file_close(self, filename):
        path = os.path.join(self.files_path, filename)

        file_entry = dict(virtool.utils.file_stats(path), filename=filename)

        document = await self.db.files.find_one_and_update({"_id": filename}, {
            "$set": {
                "size": file_entry["size"],
                "ready": True
            }
        }, projection=virtool.db.files.PROJECTION)

        if not document:
            await self.loop.run_in_executor(
                self.executor,
                os.remove,
                path
            )

    async def handle_file_creation(self, filename):
        await self.db.files.update_one({"_id": filename}, {
            "$set": {
                "created": True
            }
        })

    async def handle_file_deletion(self, filename):
        await self.db.files.delete_one({"_id": filename})
