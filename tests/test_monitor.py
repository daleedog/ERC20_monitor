import pytest
from erc20_monitor import erc20_monitor

def test_large_transfer_detection():
    # Test a large transfer scenario
    large_transfer = {
        'args': {'from': '0x123', 'to': '0x456', 'value': 1000000},
        'blockNumber': 12345678
    }
    result = erc20_monitor.check_large_transfer(large_transfer, threshold=100000)
    assert result is True

def test_normal_transfer_detection():
    # Test a normal transfer that shouldn't trigger an alert
    normal_transfer = {
        'args': {'from': '0x123', 'to': '0x456', 'value': 5000},
        'blockNumber': 12345678
    }
    result = erc20_monitor.check_large_transfer(normal_transfer, threshold=100000)
    assert result is False
