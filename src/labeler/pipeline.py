import os
import pandas as pd
from tqdm import tqdm
from typing import Optional
from .azure_client import get_client
from .config import load_settings
from .classifier import classify

def run_labeling(input_path: str, output_path: Optional[str] = None, sheet_name: Optional[str] = None) -> str:
    cfg = load_settings()
    client = get_client()
    deployment = cfg["deployment"]

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"No existe el archivo: {input_path}")

    df = pd.read_excel(input_path, sheet_name=sheet_name)

    # Validaciones mínimas
    for col in ("Año", "NombreActividad"):
        if col not in df.columns:
            raise ValueError(f"Falta la columna requerida: {col}")

    # Filtrar Año == 2025
    df = df[df["Año"] == 2025].copy()

    # Etiquetar fila a fila
    etiquetas = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Etiquetando"):
        texto = str(row.get("NombreActividad", "")).strip()
        labels = classify(client, deployment, texto)
        etiquetas.append(" | ".join(labels))

    df["etiqueta"] = etiquetas

    # Path de salida
    if not output_path:
        base = os.path.splitext(os.path.basename(input_path))[0]
        os.makedirs("data/processed", exist_ok=True)
        output_path = os.path.join("data/processed", f"{base}_etiquetado_2025.xlsx")

    df.to_excel(output_path, index=False)
    return output_path
