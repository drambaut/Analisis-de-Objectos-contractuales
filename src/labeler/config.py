import os
from dotenv import load_dotenv

# Etiquetas permitidas
ALLOWED_LABELS = [
    "Politica Publica",
    "Presupuesto de inversion",
    "Articulacion de planeacion y gobierno",
    "Seguimiento y evaluacion",
    "analisis economico",
    "regalias",
]

def load_settings():
    load_dotenv()
    return {
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "").strip(),
        "api_key": os.getenv("AZURE_OPENAI_API_KEY", "").strip(),
        "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip(),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        "allowed_labels": ALLOWED_LABELS,
    }
