from onlyfilms import manager


def test_get_films(fake_db):
    result, total = manager.get_films()

    assert len(result) == 10
    assert total == 10
