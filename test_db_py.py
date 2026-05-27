from db import generate_id
from etl import check_status, check_tx_type

def test_generate_id_is_string():
    result = generate_id()
    assert isinstance(result, str)


def test_generate_id_is_unique():
    id1 = generate_id()
    id2 = generate_id()
    assert id1 != id2

def test_check_status_valid():
    assert check_status("paid") == "paid"
    assert check_status("open") == "open"
    assert check_status("cancelled") == "cancelled"


def test_check_status_invalid():
    assert check_status("UNKNOWN") is None
    assert check_status("") is None
    assert check_status("random") is None


def test_check_tx_type_valid():
    assert check_tx_type("SALE") == "SALE"
    assert check_tx_type("REFUND") == "REFUND"


def test_check_tx_type_invalid():
    assert check_tx_type("UNKNOWN") is None
    assert check_tx_type("") is None