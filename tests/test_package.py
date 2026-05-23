import safegrove as sg


def test_top_level_package_exports_community():
    assert sg.Community is not None
    assert isinstance(sg.Community(), sg.Community)
