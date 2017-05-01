import pytest
import collections

import virtool.job_manager


class MockQueue:

    def __init__(self):
        self.messages = collections.deque()

    def put(self, message):
        self.messages.append(message)

    def get(self):
        return self.messages.popleft()

    def empty(self):
        return len(self.messages) == 0


class MockSettings:

    def __init__(self):
        self._data = {
            "db_name": "test",
            "db_host": "localhost",
            "db_port": 27017,
            "rebuild_index_inst": 2,
            "proc": 4,
            "mem": 8
        }

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key):
        return self._data[key]

    def update(self, update_dict):
        self._data.update(update_dict)

    def as_dict(self):
        return dict(self._data)


@pytest.fixture
def test_job_manager(mocker, loop, test_motor):

    manager = virtool.job_manager.Manager(loop, test_motor, MockSettings(), mocker.stub(name="dispatch"))

    yield manager

    manager.close()


@pytest.fixture
def test_queue(monkeypatch):

    mock_queue = MockQueue()

    monkeypatch.setattr("multiprocessing.Queue", lambda: mock_queue)

    return mock_queue


@pytest.fixture
def mock_job_class(monkeypatch, mocker):
    # Mock the :class:`.RebuildIndex` job class so we can see what calls are made on it and its returned instance.
    mock_obj = mocker.Mock()
    mock_class = mocker.Mock(name="RebuildIndex", return_value=mock_obj)

    monkeypatch.setattr("virtool.job_classes.TASK_CLASSES", {
        "rebuild_index": mock_class
    })

    return mock_class, mock_obj


@pytest.fixture
def test_job(static_time):
    return {
        "_id": "4c530449",
        "user_id": "igboyes",
        "proc": 10,
        "mem": 16,
        "task": "rebuild_index",
        "args": {
            "name": None,
            "username": "igboyes",
            "sample_id": "1e01a382",
            "analysis_id": "e410429b",
            "algorithm": "nuvs",
            "index_id": "465428b0"
        },
        "status": [
            {
                "error": None,
                "timestamp": static_time,
                "state": "waiting",
                "stage": None,
                "progress": 0
            },
            {
                "error": None,
                "timestamp": static_time,
                "state": "running",
                "stage": None,
                "progress": 0
            },
            {
                "error": None,
                "timestamp": static_time,
                "state": "running",
                "stage": "mk_analysis_dir",
                "progress": 0.091
            },
            {
                "error": None,
                "timestamp": static_time,
                "state": "complete",
                "stage": "import_results",
                "progress": 1.0
            }
        ]
    }
