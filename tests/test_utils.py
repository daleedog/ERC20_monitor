from erc20_monitor import utils

def test_format_ethereum_address():
    # Test address formatting utility
    raw_address = '0x123456789abcdef'
    formatted_address = utils.format_address(raw_address)
    assert formatted_address == '0x123456789abcdef'.lower()
