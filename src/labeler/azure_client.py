import httpx
from openai import AzureOpenAI
from .config import load_settings

def get_client() -> AzureOpenAI:
    cfg = load_settings()
    if not cfg["endpoint"] or not cfg["api_key"] or not cfg["deployment"]:
        missing = [k for k in ["endpoint","api_key","deployment"] if not cfg[k]]
        raise RuntimeError(f"Faltan variables de entorno: {', '.join(missing)}")
    return AzureOpenAI(
        api_key=cfg["api_key"],
        api_version=cfg["api_version"],
        azure_endpoint=cfg["endpoint"],
        http_client=httpx.Client(verify=False),
    )
