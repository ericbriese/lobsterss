import json
from pathlib import Path

import pytest


@pytest.fixture
def stories():
    return json.loads((Path(__file__).parent / "java_python_test.json").read_text())
