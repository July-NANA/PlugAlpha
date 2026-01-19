
# Polymarket MCP (FastMCP Edition)

A **Model Context Protocol (MCP)** server for interacting with **Polymarket CLOB**, built with **FastMCP**, supporting **HTTP / SSE / stdio** transports.

This MCP allows AI agents and MCP-compatible clients (e.g. **Cherry Studio**, **MCP Inspector**) to **read Polymarket markets and data**, with optional support for authenticated actions.

---

## ✨ Features

* ✅ MCP-compliant server (FastMCP)
* ✅ Supports **HTTP / SSE / stdio** transports
* ✅ Read Polymarket markets (list markets, market metadata)
* ✅ Uses official **Polymarket CLOB API**
* ✅ Works inside **Docker / Dev Container**
* ✅ Compatible with **Cherry Studio** and **MCP Inspector**
* ⚠️ Trading endpoints require private key & API credentials (opt-in)

---

## 📦 Project Structure

```text
polymarket-mcp/
├─ src/
│  └─ polymarket_mcp/
│     ├─ server.py        # FastMCP server entry
│     └─ __init__.py
├─ requirements.txt
├─ README.md
└─ .env.example
```

---

## 🔧 Requirements

* Python **3.10+** (tested with 3.14)
* Polymarket CLOB API access
* Optional: Docker / Dev Container
* Optional: `uv` (recommended)

---

## 📥 Installation

### Option 1: Using `uv` (recommended)

```bash
uv venv
uv pip install -r requirements.txt
```

### Option 2: Using pip

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
# Required for authenticated endpoints
POLYMARKET_API_KEY=your_api_key
POLYMARKET_API_SECRET=your_api_secret
POLYMARKET_API_PASSPHRASE=your_api_passphrase

# Ethereum address used as funder
POLYMARKET_FUNDER=0xYourEthereumAddress

# Optional: private key (required only for signing / trading)
POLYMARKET_PRIVATE_KEY=0xYourPrivateKey
```

> ⚠️ **Security note**
> Do NOT commit `.env` or private keys to version control.

---

## 🚀 Running the MCP Server

### HTTP transport (recommended for GUI tools)

```bash
fastmcp run src/polymarket_mcp/server.py \
  --transport http \
  --host 0.0.0.0 \
  --port 3333
```

Server will be available at:

```
http://127.0.0.1:3333/mcp
```

---

### SSE transport

```bash
fastmcp run src/polymarket_mcp/server.py \
  --transport sse \
  --host 0.0.0.0 \
  --port 3333
```

---

### stdio transport (CLI / agent embedding)

```bash
fastmcp run src/polymarket_mcp/server.py
```

---

## 🧪 Testing with MCP Inspector

Install the inspector:

```bash
npx @modelcontextprotocol/inspector
```

Run with HTTP transport:

```bash
npx @modelcontextprotocol/inspector \
  --transport http \
  --server-url http://127.0.0.1:3333/mcp
```

---

## 🍒 Using with Cherry Studio

1. Open **Cherry Studio**
2. Add a new MCP server
3. Choose **HTTP** transport
4. Set URL:

```text
http://127.0.0.1:3333/mcp
```

5. Import via JSON or manual configuration
6. Tools such as `list-markets` should become available

---

## 🛠 Available Tools (Example)

* `list-markets`

  * Parameters:

    * `limit`
    * `offset`
  * Returns:

    * Market metadata
    * Condition IDs
    * Status, volume, tokens, etc.

> Note:
> Some historical or resolved markets may still appear depending on Polymarket API behavior.

---

## ⚠️ Market Status Notes

Polymarket CLOB API **does not strictly align** with `active / resolved / closed` labels.

* `active=true` does **not always** mean tradable
* Many markets returned by the API may already be closed
* Filtering by status is **best-effort**

This is a known Polymarket API behavior, not an MCP bug.

---

## 🔐 Security & Permissions

* Read-only endpoints work **without private key**
* Trading / signing endpoints require:

  * `POLYMARKET_PRIVATE_KEY`
  * API credentials
* It is recommended to:

  * Disable trading tools by default
  * Explicitly allow them in controlled environments only

---

## 🧠 Why FastMCP?

FastMCP provides:

* Clean MCP abstractions
* Native HTTP / SSE support
* Better interoperability with modern MCP clients
* Easier deployment in Docker & cloud environments

---

## 🗺 Roadmap


- [ ] Read-only mode flag
- [ ] Explicit trading enable switch
- [ ] Market search by slug / condition ID
- [ ] Orderbook snapshot tools
- [ ] Agent-safe permission layers

---

## 📄 License

AGPL v3 License

---
