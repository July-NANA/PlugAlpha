import os
from pathlib import Path

from dotenv import load_dotenv
from eth_account import Account
from py_clob_client.client import ClobClient


HOST = os.getenv("POLYMARKET_CLOB_HOST", "https://clob.polymarket.com")
CHAIN_ID = int(os.getenv("POLYMARKET_CHAIN_ID", "137"))  # Polygon mainnet


def load_env():
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)


def require_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing {name}")
    return v.strip()


def validate_key_and_funder(private_key: str, funder: str):
    derived = Account.from_key(private_key).address
    if derived.lower() != funder.lower():
        raise RuntimeError(
            "Private key does not match funder address.\n"
            f"Derived: {derived}\n"
            f"Env funder: {funder}"
        )


def main():
    load_env()

    private_key = require_env("POLYMARKET_PRIVATE_KEY")
    funder = require_env("POLYMARKET_FUNDER")

    validate_key_and_funder(private_key, funder)

    client = ClobClient(
        host=HOST,
        chain_id=CHAIN_ID,
        key=private_key,
        funder=funder,
    )

    # ✅ correct method name for your installed version
    creds = client.create_or_derive_api_creds()

    # api_key = getattr(creds, "apiKey", None) or getattr(creds, "api_key", None)
    # secret = getattr(creds, "secret", None)
    # passphrase = getattr(creds, "passphrase", None)
    api_key = creds.api_key
    secret = creds.api_secret
    passphrase = creds.api_passphrase

    # print("API_KEY:", api_key)
    # print("SECRET:", secret)
    # print("PASSPHRASE:", passphrase)
    # print("FUNDER:", funder)


    print("OK. Derived/loaded API credentials:")
    print("API_KEY:", api_key)
    print("SECRET:", secret)
    print("PASSPHRASE:", passphrase)
    print("FUNDER:", funder)

    # print("CREDS TYPE:", type(creds))
    # print("CREDS DIR:", [a for a in dir(creds) if not a.startswith("_")])
    # print("CREDS REPR:", creds)
    # try:
    #     print("CREDS DICT:", creds.__dict__)
    # except Exception:
    #     pass



if __name__ == "__main__":
    main()
