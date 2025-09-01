import argparse
from labeler.pipeline import run_labeling

def main():
    parser = argparse.ArgumentParser(description="Etiquetar NombreActividad (Año==2025) con Azure OpenAI.")
    parser.add_argument("--input", default="data/raw/actividades.xlsx", help="Ruta al Excel de entrada.")
    parser.add_argument("--sheet", default=None, help="Nombre de la hoja (opcional).")
    parser.add_argument("--output", default=None, help="Ruta de salida (opcional).")
    args = parser.parse_args()

    out = run_labeling(args.input, args.output, args.sheet)
    print(f"Listo. Archivo generado: {out}")

if __name__ == "__main__":
    main()
