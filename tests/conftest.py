import pytest
import os
import shutil


@pytest.fixture(scope="module", autouse=True)
def tmp_directory():
    dir_path = '/tmp/accordion'
    shutil.rmtree(dir_path, ignore_errors=True)
    os.makedirs(dir_path)
    yield dir_path
    shutil.rmtree(dir_path, ignore_errors=True)
