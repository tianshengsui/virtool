import asyncio

import virtool.db.migrate
import virtool.db.utils
import virtool.samples.db
import virtool.types
import virtool.utils


async def migrate_samples(app: virtool.types.App):
    """
    Automatically update sample documents on application start.

    Recalculate all sample workflow tags and delete unready samples.

    :param app: the application object
    """
    db = app["db"]

    await recalculate_all_workflow_tags(db)
    await virtool.db.utils.delete_unready(db.samples)
    await change_to_subtractions_list(db)
    await add_is_legacy(db)


async def add_is_legacy(db):
    """
    As `is_legacy` field to samples to make it more obvious that they are legacy samples.

    :param db: the application object

    """
    await db.samples.update_many({"files.raw": False}, {
        "$set": {
            "is_legacy": True
        }
    })

    await db.samples.update_many({"files.raw": True}, {
        "$set": {
            "is_legacy": False
        }
    })


async def recalculate_all_workflow_tags(db):
    """
    Recalculate workflow tags for all samples. Works on multiple samples concurrently.

    :param db: the application database object

    """
    sample_ids = await db.samples.distinct("_id")

    for chunk in virtool.utils.chunk_list(sample_ids, 50):
        coros = [virtool.samples.db.recalculate_workflow_tags(db, sample_id) for sample_id in chunk]
        await asyncio.gather(*coros)

