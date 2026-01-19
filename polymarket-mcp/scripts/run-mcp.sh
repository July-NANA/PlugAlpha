#!/usr/bin/env bash
set -euo pipefail

MCP_TRANSPORT="${MCP_TRANSPORT:-stdio}"

export MCP_TRANSPORT

uv run polymarket-mcp
