from typing import Any, Literal
import json
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from py_clob_client.client import ClobClient
from py_clob_client.constants import END_CURSOR, POLYGON

# Load environment variables
load_dotenv()

mcp = FastMCP("polymarket_predictions")


StatusOption = Literal["any", "open", "closed", "active", "resolved"]
SourceOption = Literal["auto", "markets", "sampling"]

# Initialize CLOB client
def get_clob_client() -> ClobClient:
    host = os.getenv("CLOB_HOST", "https://clob.polymarket.com")
    key = os.getenv("KEY")  # Private key exported from polymarket UI
    funder = os.getenv("FUNDER")  # Funder address from polymarket UI
    chain_id = POLYGON
    
    client = ClobClient(
        host,
        key=key,
        chain_id=POLYGON,
        funder=funder,
        signature_type=1,
    )
    client.set_api_creds(client.create_or_derive_api_creds())
    return client

def format_market_info(market_data: dict) -> str:
    """Format market information into a concise string."""
    try:
        if not market_data or not isinstance(market_data, dict):
            return "No market information available"
            
        condition_id = market_data.get('condition_id', 'N/A')
        title = market_data.get('title', 'N/A')
        status = market_data.get('status', 'N/A')
        resolution_date = market_data.get('resolution_date', 'N/A')
            
        return (
            f"Condition ID: {condition_id}\n"
            f"Title: {title}\n"
            f"Status: {status}\n"
            f"Resolution Date: {resolution_date}\n"
            "---"
        )
    except Exception as e:
        return f"Error formatting market data: {str(e)}"

def format_market_list(markets_data: list) -> str:
    """Format list of markets into a concise string."""
    try:
        if not markets_data:
            return "No markets available"
            
        formatted_markets = ["Available Markets:\n"]
        
        for market in markets_data:
            try:
                volume = float(market.get('volume', 0))
                volume_str = f"${volume:,.2f}"
            except (ValueError, TypeError):
                volume_str = f"${market.get('volume', 0)}"
                
            formatted_markets.append(
                f"Condition ID: {market.get('condition_id', 'N/A')}\n"
                f"Description: {market.get('description', 'N/A')}\n"
                f"Category: {market.get('category', 'N/A')}\n"
                f"Tokens: {market.get('question', 'N/A')}\n"
                f"Question: {market.get('active', 'N/A')}\n"
                f"Rewards: {market.get('rewards', 'N/A')}\n"
                f"Active: {market.get('active', 'N/A')}\n"
                f"Closed: {market.get('closed', 'N/A')}\n"
                f"Slug: {market.get('market_slug', 'N/A')}\n"
                f"Min Incentive size: {market.get('min_incentive_size', 'N/A')}\n"
                f"Max Incentive size: {market.get('max_incentive_spread', 'N/A')}\n"
                f"End date: {market.get('end_date_iso', 'N/A')}\n"
                f"Start time: {market.get('game_start_time', 'N/A')}\n"
                f"Min order size: {market.get('minimum_order_size', 'N/A')}\n"
                f"Max tick size: {market.get('minimum_tick_size', 'N/A')}\n"
                f"Volume: {volume_str}\n"
                "---\n"
            )
        
        return "\n".join(formatted_markets)
    except Exception as e:
        return f"Error formatting markets list: {str(e)}"

def format_market_prices(market_data: dict) -> str:
    """Format market prices into a concise string."""
    try:
        if not market_data or not isinstance(market_data, dict):
            return market_data
            
        formatted_prices = [
            f"Current Market Prices for {market_data.get('title', 'Unknown Market')}\n"
        ]
        
        # Extract price information from market data
        # Note: Adjust this based on actual CLOB client response structure
        current_price = market_data.get('current_price', 'N/A')
        formatted_prices.append(
            f"Current Price: {current_price}\n"
            "---\n"
        )
        
        return "\n".join(formatted_prices)
    except Exception as e:
        return f"Error formatting price data: {str(e)}"

def format_market_history(history_data: dict) -> str:
    """Format market history data into a concise string."""
    try:
        if not history_data or not isinstance(history_data, dict):
            return "No historical data available"
            
        formatted_history = [
            f"Historical Data for {history_data.get('title', 'Unknown Market')}\n"
        ]
        
        # Format historical data points
        # Note: Adjust this based on actual CLOB client response structure
        for point in history_data.get('history', [])[-5:]:
            formatted_history.append(
                f"Time: {point.get('timestamp', 'N/A')}\n"
                f"Price: {point.get('price', 'N/A')}\n"
                "---\n"
            )
        
        return "\n".join(formatted_history)
    except Exception as e:
        return f"Error formatting historical data: {str(e)}"

def market_matches_status(market: dict, status: str) -> bool:
    """Match a status filter against market fields returned by the CLOB API."""
    if not status or not isinstance(market, dict):
        return True

    status = status.lower()
    active = market.get("active")
    closed = market.get("closed")
    resolved = market.get("resolved")

    if status == "open":
        return bool(active) and not bool(closed) and not bool(resolved)
    if status == "active":
        return bool(active)
    if status == "closed":
        return bool(closed)
    if status == "resolved":
        return bool(resolved)

    market_status = market.get("status")
    if isinstance(market_status, str):
        return market_status.lower() == status

    return False

def normalize_market_response(markets_data: Any) -> tuple[list, str | None]:
    """Normalize CLOB responses into (markets, next_cursor)."""
    if isinstance(markets_data, str):
        try:
            markets_data = json.loads(markets_data)
        except json.JSONDecodeError:
            return [], None

    if isinstance(markets_data, list):
        return markets_data, None

    if isinstance(markets_data, dict):
        data = markets_data.get("data")
        if isinstance(data, list):
            return data, markets_data.get("next_cursor")

    return [], None

def collect_markets(fetch_page, limit: int, offset: int) -> list:
    """Collect markets across pages until limit+offset is satisfied or cursor ends."""
    target = max(limit + offset, 0)
    next_cursor = "MA=="
    seen = set()
    results = []

    while next_cursor and next_cursor not in seen:
        seen.add(next_cursor)
        page_data = fetch_page(next_cursor)
        markets, next_cursor = normalize_market_response(page_data)
        results.extend(markets)
        if len(results) >= target or next_cursor == END_CURSOR:
            break

    return results

def _limit_offset_valid(limit: int, offset: int) -> str | None:
    if limit < 1 or limit > 100:
        return "limit must be between 1 and 100"
    if offset < 0:
        return "offset must be >= 0"
    return None


@mcp.tool(name="get-market-info", description="Get detailed information about a specific prediction market")
async def get_market_info(market_id: str) -> str:
    if not market_id:
        return "Missing market_id parameter"

    client = get_clob_client()
    try:
        market_data = client.get_market(market_id)
    except Exception as exc:
        return f"Error executing tool: {str(exc)}"

    return format_market_info(market_data)


@mcp.tool(name="list-markets", description="Get a list of prediction markets with optional filters")
async def list_markets(
    *,
    status: StatusOption = "any",
    limit: int = 10,
    offset: int = 0,
    source: SourceOption = "auto",
) -> str:
    validation_error = _limit_offset_valid(limit, offset)
    if validation_error:
        return validation_error

    status_value = None if status == "any" else status
    if source == "auto":
        source = "sampling" if status_value in {"open", "active"} else "markets"

    client = get_clob_client()

    def fetch_page(next_cursor: str):
        if source == "sampling":
            return client.get_sampling_markets(next_cursor)
        return client.get_markets(next_cursor)

    try:
        markets_data = collect_markets(fetch_page, limit=limit, offset=offset)
    except Exception as exc:
        return f"Error executing tool: {str(exc)}"

    if status_value:
        markets_data = [
            market for market in markets_data if market_matches_status(market, status_value)
        ]

    markets_data = markets_data[offset:offset + limit]
    return format_market_list(markets_data)


@mcp.tool(name="get-market-prices", description="Get current prices and trading information for a market")
async def get_market_prices(market_id: str) -> str:
    if not market_id:
        return "Missing market_id parameter"

    client = get_clob_client()
    try:
        market_data = client.get_market(market_id)
    except Exception as exc:
        return f"Error executing tool: {str(exc)}"

    return format_market_prices(market_data)


@mcp.tool(name="get-market-history", description="Get historical price and volume data for a market")
async def get_market_history(
    market_id: str,
    timeframe: Literal["1d", "7d", "30d", "all"] = "7d",
) -> str:
    if not market_id:
        return "Missing market_id parameter"

    client = get_clob_client()
    try:
        market_data = client.get_market(market_id)
    except Exception as exc:
        return f"Error executing tool: {str(exc)}"

    history_text = format_market_history(market_data)
    return f"Time Period: {timeframe}\n{history_text}"


def main() -> None:
    """Main entry point for the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()
