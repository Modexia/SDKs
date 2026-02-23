import pytest
import os
import requests_mock
from modexia.client import ModexiaClient, ModexiaAuthError, ModexiaPaymentError

def test_base_url_resolution():
    # 1. Provide explicit base_url
    client = ModexiaClient(api_key="mx_test_123", base_url="http://custom.url", validate=False)
    assert client.base_url == "http://custom.url"

    # 2. Provide ENV var (mocked)
    os.environ["MODEXIA_BASE_URL"] = "http://env.url"
    client = ModexiaClient(api_key="mx_test_123", validate=False)
    assert client.base_url == "http://env.url"
    del os.environ["MODEXIA_BASE_URL"]

    # 3. Key mapping
    client_live = ModexiaClient(api_key="mx_live_123", validate=False)
    assert client_live.base_url == "https://api.modexia.software"

    client_test = ModexiaClient(api_key="mx_test_123", validate=False)
    assert client_test.base_url == "https://sandbox.modexia.software"

    client_local = ModexiaClient(api_key="other_key", validate=False)
    assert client_local.base_url == "http://localhost:3000"

def test_validate_false_avoids_network():
    # Because there's no mocked endpoint, this would throw a connection error if it tried to connect
    client = ModexiaClient(api_key="mx_test_123", validate=False)
    assert client.identity == {}

def test_retrieve_balance_success(requests_mock):
    client = ModexiaClient(api_key="mx_test_123", validate=False)
    requests_mock.get(f"{client.base_url}/api/v1/user/me", json={"data": {"balance": "150.50", "username": "testuser"}})
    
    # Retrieve balance
    assert client.retrieve_balance() == "150.50"
    
    # Test alias
    assert client.get_balance() == "150.50"

def test_retrieve_balance_auth_error(requests_mock):
    client = ModexiaClient(api_key="mx_test_123", validate=False)
    requests_mock.get(f"{client.base_url}/api/v1/user/me", status_code=401, text="Invalid API key")
    
    with pytest.raises(ModexiaAuthError, match="Unauthorized: Invalid API key"):
        client.retrieve_balance()

def test_non_json_error_handling(requests_mock):
    client = ModexiaClient(api_key="mx_test_123", validate=False)
    
    # Simulate an Nginx 502 HTML error page
    html_error = "<html><body>502 Bad Gateway</body></html>"
    requests_mock.get(f"{client.base_url}/api/v1/user/me", status_code=502, text=html_error)
    
    with pytest.raises(ModexiaPaymentError) as exc_info:
        client.retrieve_balance()
    
    assert "HTTP 502" in str(exc_info.value)
    assert "502 Bad Gateway" in str(exc_info.value)

def test_transfer_wait_success(requests_mock):
    client = ModexiaClient(api_key="mx_test_123", validate=False)
    
    # Mock the POST response
    requests_mock.post(f"{client.base_url}/api/v1/agent/pay", json={"success": True, "txId": "txn_123"})
    
    # Mock the GET polling response
    requests_mock.get(f"{client.base_url}/api/v1/agent/transaction/txn_123", [
        {"json": {"state": "PENDING", "txHash": None}},
        {"json": {"state": "COMPLETE", "txHash": "0xabc123"}}
    ])
    
    result = client.transfer(recipient="0xRecipient", amount=10.0, wait=True)
    assert result["success"] is True
    assert result["status"] == "COMPLETE"
    assert result["txHash"] == "0xabc123"

def test_smart_fetch_paywall(requests_mock):
    client = ModexiaClient(api_key="mx_test_123", validate=False)
    target_url = "https://example.com/premium-data"
    
    # 1. Initial request gets 402 Payment Required
    requests_mock.get(target_url, [
        {
            "status_code": 402, 
            "headers": {"WWW-Authenticate": 'L402 amount="1.50" destination="0xCreator"'}
        },
        {
            "status_code": 200, 
            "json": {"secret": "data"}
        }
    ])
    
    # 2. SDK will attempt to pay
    requests_mock.post(f"{client.base_url}/api/v1/agent/pay", json={"success": True, "txId": "txn_402"})
    requests_mock.get(f"{client.base_url}/api/v1/agent/transaction/txn_402", json={"state": "COMPLETE", "txHash": "0xhash"})
    
    # 3. Call smart_fetch
    response = client.smart_fetch(target_url)
    assert response.status_code == 200
    assert response.json() == {"secret": "data"}
    
    # Assert headers were sent correctly on the retry
    last_request = requests_mock.request_history[-1]
    assert last_request.headers.get("Authorization") == "L402 txn_402"
    assert last_request.headers.get("X-Payment-Proof") == "txn_402"
