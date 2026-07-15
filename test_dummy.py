def test_fail():
    assert 1==2

def test_import_failure():
    raise ImportError("Simulated module failure")
