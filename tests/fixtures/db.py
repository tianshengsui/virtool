import pytest
import pymongo
import motor.motor_asyncio
from aiohttp.test_utils import make_mocked_coro

import virtool.db.iface


class MockDeleteResult:

    def __init__(self, deleted_count):
        self.deleted_count = deleted_count


@pytest.fixture()
def test_db_name(worker_id):
    return "vt-test-{}".format(worker_id)


@pytest.fixture
def test_db(test_db_name):
    client = pymongo.MongoClient()
    client.drop_database(test_db_name)

    yield client[test_db_name]

    client.drop_database(test_db_name)


@pytest.fixture
def test_motor(test_db, test_db_name, loop):
    client = motor.motor_asyncio.AsyncIOMotorClient(io_loop=loop)
    loop.run_until_complete(client.drop_database(test_db_name))
    yield client[test_db_name]
    loop.run_until_complete(client.drop_database(test_db_name))


@pytest.fixture
def test_dbi(test_motor, loop):
    i = virtool.db.iface.DB(test_motor, make_mocked_coro(), loop)
    loop.run_until_complete(i.connect())
    return i


@pytest.fixture
def create_delete_result():
    return MockDeleteResult
