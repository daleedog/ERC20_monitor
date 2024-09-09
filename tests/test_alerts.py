from unittest.mock import Mock
from erc20_monitor import alerts


def test_send_discord_alert():
    # Mock the Discord client
    mock_discord_client = Mock()

    # Simulate sending an alert
    alert_message = "Large transfer detected!"
    alerts.send_discord_alert(mock_discord_client, alert_message)

    # Ensure the send message function was called
    mock_discord_client.send_message.assert_called_once_with(alert_message)
