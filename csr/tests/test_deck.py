import csr.deck as deck
from datetime import date


def test__ensure_is_date() -> None:
    assert deck._ensure_is_date("2022-01-01") == date(2022, 1, 1)
    assert deck._ensure_is_date(date(2022, 4, 1)) == date(2022, 4, 1)
