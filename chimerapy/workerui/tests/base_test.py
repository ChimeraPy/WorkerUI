import pytest


class BaseTest:
    @pytest.fixture(autouse=True)
    def initdir(self, tmpdir):
        return tmpdir.chdir()
