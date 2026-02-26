<div align="center">
  <h1>🚀 Modexia Python SDK</h1>
  <p><b>Lightweight, modern Python client for interacting with the Modexia AgentPay API.</b></p>
  
  [![PyPI version](https://badge.fury.io/py/modexiaagentpay.svg)](https://badge.fury.io/py/modexiaagentpay)
  [![Python versions](https://img.shields.io/pypi/pyversions/modexiaagentpay.svg)](https://pypi.org/project/modexiaagentpay/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

---

Welcome to the **Modexia Python SDK** (`modexiaagentpay`). This SDK is built to give your AI agents and Python applications seamless access to Modexia's wallet and payment infrastructure (USDC). We've open-sourced this client so you can integrate payments with minimal friction!

## 🌟 Get Your API Key

Before you can start transferring funds and managing wallets, you'll need an API key. 

1. Head over to **[modexia.software](https://modexia.software)**
2. Create your developer account
3. Navigate to your dashboard and generate your free `API Key`

## 📚 Check Out the Docs

Our documentation covers everything you need to know to build agentic payment experiences! Be sure to explore our full API documentation and guides at **[modexia.software](https://modexia.software)**.

---

## ✨ Features

- **Built for Agents:** Simple programmatic access to agent wallets and payments.
- **Reliable by Default:** Built-in retry/backoff for HTTP calls to handle network blips.
- **Minimal Surface Area:** Clean, typed interface via `ModexiaClient` with `transfer` and `retrieve_balance`.
- **Lightweight:** Only relies on `requests`.

## 📦 Installation

Install the package directly from PyPI:

```bash
pip install modexiaagentpay
```

*For local editable installation (if you are contributing):*
```bash
pip install -e packages/SDKs/pythonSdk
```

## 🚀 Quick Start

Initialize the client with your Modexia API key and start making transfers instantly.

```python
from modexia import ModexiaClient

# 1. Initialize the client using your API key from modexia.software
client = ModexiaClient(api_key="mx_test_your_api_key_here")

# Note: You can also override the base url, or skip network validation:
# client = ModexiaClient(api_key="...", base_url="https://custom.url", validate=False)
# The client also automatically respects the MODEXIA_BASE_URL environment variable.

# 2. Check your balance
balance = client.retrieve_balance() # Or use `client.get_balance()`
print(f"Current wallet balance: {balance}")

# 3. Make a transfer! 
# (Setting wait=True polls until the transaction is confirmed on-chain)
receipt = client.transfer(
    recipient="0xabc123...", 
    amount=5.0, 
    wait=True
)
print(f"Transfer successful! Receipt: {receipt}")
```

## 🛠 API Overview

The core interactions run through the `ModexiaClient`:

- `ModexiaClient(api_key: str, timeout: int = 15, base_url: Optional[str] = None, validate: bool = True)`
  - `retrieve_balance() -> str`
  - `get_balance() -> str` *(alias for retrieve_balance)*
  - `transfer(recipient: str, amount: float, idempotency_key: Optional[str] = None, wait: bool = True) -> dict`

### Error Handling

We provide clean exceptions for robust error handling in your applications:
- `ModexiaAuthError` — Authentication problems (e.g., invalid API key).
- `ModexiaPaymentError` — Payment or server errors (e.g., insufficient funds).
- `ModexiaNetworkError` — Network/connection failures.

## 🤝 Contributing

We love open source contributions! To contribute to the Modexia Python SDK:

1. Clone the repository and open a PR against the `develop` branch.
2. Keep API names stable — `ModexiaClient` and `transfer(...)` are our canonical surface areas.
3. Run the test suite using `pytest`:

```bash
# From the repository root
pytest -q packages/SDKs/pythonSdk
```

## 📄 License

This SDK is available under the [MIT License](LICENSE).
