import json
import time
from typing import List
from openai import AzureOpenAI
from .config import load_settings
from .prompts import SYSTEM_PROMPT, USER_TEMPLATE

cfg = load_settings()
ALLOWED_LABELS = cfg["allowed_labels"]

def _closest_fallback(texto: str) -> str:
    t = (texto or "").lower()
    if any(k in t for k in ["política", "politica", "conpes", "norma", "lineamiento", "plan"]):
        return "Politica Publica"
    if any(k in t for k in ["presupuesto", "inversión", "inversion", "bpin", "proyecto"]):
        return "Presupuesto de inversion"
    if any(k in t for k in ["articulación", "articulacion", "gobierno", "planeación", "planeacion", "coordinación", "coordinacion"]):
        return "Articulacion de planeacion y gobierno"
    if any(k in t for k in ["seguimiento", "evaluación", "evaluacion", "indicador", "monitoreo"]):
        return "Seguimiento y evaluacion"
    if any(k in t for k in ["econom", "costos", "impacto", "análisis", "analisis", "proyección", "proyeccion"]):
        return "analisis economico"
    if any(k in t for k in ["regal", "sgr", "regalías", "regalias"]):
        return "regalias"
    return "Politica Publica"

def _force_single_label(client: AzureOpenAI, deployment: str, texto: str) -> str:
    prompt = f"""Elige EXACTAMENTE UNA etiqueta válida de esta lista:
{ALLOWED_LABELS}

Texto: "{texto}"

Responde sólo con JSON: {{"label": "<una etiqueta exacta"}}"""
    resp = client.chat.completions.create(
        model=deployment,
        temperature=0,
        messages=[
            {"role": "system", "content": "Devuelve exactamente una etiqueta de la lista dada, en JSON."},
            {"role": "user", "content": prompt},
        ],
    )
    content = (resp.choices[0].message.content or "").strip()
    s, e = content.find("{"), content.rfind("}")
    if s != -1 and e != -1 and e > s:
        content = content[s:e+1]
    try:
        data = json.loads(content)
        label = str(data.get("label", "")).strip()
        if label in ALLOWED_LABELS:
            return label
    except Exception:
        pass
    return _closest_fallback(texto)

def classify(client: AzureOpenAI, deployment: str, texto: str, retries: int = 3, backoff: float = 1.5) -> List[str]:
    for attempt in range(1, retries + 1):
        try:
            resp = client.chat.completions.create(
                model=deployment,
                temperature=0,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_TEMPLATE.format(texto=texto)},
                ],
            )
            content = (resp.choices[0].message.content or "").strip()
            s, e = content.find("{"), content.rfind("}")
            if s != -1 and e != -1 and e > s:
                content = content[s:e+1]
            data = json.loads(content)
            labels = data.get("labels", [])
            cleaned = []
            for lbl in labels:
                lbl_clean = str(lbl).strip()
                if lbl_clean in ALLOWED_LABELS:
                    cleaned.append(lbl_clean)
            if not cleaned:
                cleaned = [_force_single_label(client, deployment, texto)]
            # Quitar duplicados preservando orden
            return list(dict.fromkeys(cleaned))
        except Exception:
            if attempt == retries:
                return [_closest_fallback(texto)]
            time.sleep(backoff * attempt)
