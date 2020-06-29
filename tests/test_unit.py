import os


def test_get_shared_object(get_shared_object):
    lib_path = get_shared_object
    assert os.path.isfile(lib_path), f"{lib_path} does not exist"
