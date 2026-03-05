import os, base64, requests, time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from .config import DEFAULT_PARAMS

load_dotenv()


def create_session():
    """Create a requests session with retry and connection pooling."""
    session = requests.Session()

    # Retry failed requests (rate limit or server errors)
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"]
    )

    adapter = HTTPAdapter(
        max_retries=retries,
        pool_connections=20,
        pool_maxsize=20
    )

    session.mount("https://", adapter)
    return session


# Shared HTTP session for all API calls
session = create_session()


# API configuration from environment variables
TOKEN_URL = os.getenv("IDT_TOKEN_URL")
API_BASE = os.getenv("IDT_API_BASE")

CLIENT_ID = os.getenv("IDT_CLIENT_ID")
CLIENT_SECRET = os.getenv("IDT_CLIENT_SECRET")
USERNAME = os.getenv("IDT_USERNAME")
PASSWORD = os.getenv("IDT_PASSWORD")


# Cache token to avoid requesting it repeatedly
_token_cache = {"token": None, "exp": 0.0}


def get_access_token():
    """Get OAuth access token (cached until expiry)."""
    now = time.time()

    # Return cached token if still valid
    if _token_cache["token"] and now < (_token_cache["exp"] - 30):
        return _token_cache["token"]

    # Encode client credentials for Basic Auth
    basic = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "password",
        "scope": "test",
        "username": USERNAME,
        "password": PASSWORD,
    }

    r = session.post(TOKEN_URL, headers=headers, data=data, timeout=30)
    r.raise_for_status()
    js = r.json()

    # Save token and expiry time
    _token_cache["token"] = js["access_token"]
    _token_cache["exp"] = now + float(js.get("expires_in", 1800))

    return _token_cache["token"]


def analyze_sequence(seq, params):
    """Call IDT OligoAnalyzer API to analyze a single sequence."""

    token = get_access_token()

    url = f"{API_BASE}/v1/OligoAnalyzer/Analyze"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Build request payload with default parameter fallback
    payload = {
        "Sequence": seq,
        "NaConc": params.get("NaConc", DEFAULT_PARAMS["NaConc"]),
        "MgConc": params.get("MgConc", DEFAULT_PARAMS["MgConc"]),
        "dNTPsConc": params.get("dNTPsConc", DEFAULT_PARAMS["dNTPsConc"]),
        "OligoConc": params.get("OligoConc", DEFAULT_PARAMS["OligoConc"]),
        "NucleotideType": params.get("NucleotideType", DEFAULT_PARAMS["NucleotideType"])
    }

    r = session.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()

    return r.json()


def analyze_hairpin_batch(seq_batch, params):
    """Call IDT API to calculate hairpin structures for multiple sequences."""

    token = get_access_token()

    url = f"{API_BASE}/v1/OligoAnalyzer/HairpinBatch"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "Sequences": seq_batch,
        "Parameters": {
            "NaConc": params.get("NaConc", DEFAULT_PARAMS["NaConc"]),
            "MgConc": params.get("MgConc", DEFAULT_PARAMS["MgConc"]),
            "FoldingTemp": params.get("FoldingTemp", DEFAULT_PARAMS["FoldingTemp"]),
            "NucleotideType": params.get("NucleotideType", DEFAULT_PARAMS["NucleotideType"]),
        },
    }

    r = session.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()

    return r.json()


def analyze_self_dimer(seq):
    """Call IDT API to calculate self-dimer interactions."""

    token = get_access_token()

    url = f"{API_BASE}/v1/OligoAnalyzer/SelfDimer"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    r = session.post(
        url,
        headers=headers,
        params={"primary": seq},
        timeout=30
    )

    r.raise_for_status()

    return r.json()