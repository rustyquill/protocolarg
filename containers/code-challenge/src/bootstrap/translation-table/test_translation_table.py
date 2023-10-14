import pytest
from translation_table import encode_data, decode_data

@pytest.fixture()
def abc_data():
    return "abcdefghijklmnopqrstuvwxyz"

@pytest.fixture()
def abc_encoded_data():
    return "🜁🜾🜓🝖🜃🜂🜚🜘🜜jk🜪🜐🜕🝆🜎🝁🜻🜏🜩🝕🜊🜄xy🝍"

def test_encode_data(abc_data, abc_encoded_data):
    """ ensure the abc string is encoded correctly """

    assert encode_data(abc_data) == abc_encoded_data

def test_decode_data(abc_data, abc_encoded_data):
    """ ensure the abc string is decoded correctly """

    assert decode_data(abc_encoded_data) == abc_data

def test_encode_data_uppercase(abc_data, abc_encoded_data):
    """ ensure the abc string is encoded correctly """

    assert encode_data(abc_data.upper()) == abc_encoded_data

