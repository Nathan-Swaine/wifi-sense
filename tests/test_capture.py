from datetime import datetime, timezone

from wifi_sense.capture import parse_netsh_scan


def test_parse_netsh_scan_anonymizes_bssid_and_converts_signal():
    output = """SSID 1 : office\n    BSSID 1 : AA:BB:CC:DD:EE:FF\n         Signal             : 80%\n         Channel            : 36\n"""
    result = parse_netsh_scan(output, "Wi-Fi", "test", datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert len(result) == 1
    assert result[0].identifier != "AA:BB:CC:DD:EE:FF"
    assert result[0].rssi_dbm == -60
    assert result[0].channel == 36