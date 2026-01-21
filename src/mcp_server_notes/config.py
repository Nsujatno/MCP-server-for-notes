import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve the project root (assuming standard src layout locally)
# src/mcp_server_notes/config.py -> src/mcp_server_notes -> src -> root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

# Load .env from project root if it exists, otherwise rely on system env vars or current dir .env
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

VAULT_PATH_STR = os.getenv("OBSIDIAN_VAULT_PATH")

if not VAULT_PATH_STR:
    raise ValueError("OBSIDIAN_VAULT_PATH not found in .env file or environment variables")
    
VAULT_PATH = Path(VAULT_PATH_STR)

def ensure_path():
    if not VAULT_PATH.exists():
        raise RuntimeError(f"The vault at {VAULT_PATH} does not exist")
    return VAULT_PATH
