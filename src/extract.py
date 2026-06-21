# src/extract.py
import sys
import os
import requests
import logging
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BRONZE, SRAG_2023, SRAG_2024

logger = logging.getLogger(__name__)

# URLs diretas do S3 do OpenDataSUS
URLS = {
    SRAG_2023: "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2023/INFLUD23-23-03-2026.csv",
    SRAG_2024: "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2024/INFLUD24-23-03-2026.csv",
}

def extract():
    print("📥 Verificando arquivos na Bronze...")
    os.makedirs(BRONZE, exist_ok=True)

    for destino, url in URLS.items():
        if os.path.exists(destino):
            print(f"   ✅ Já existe: {Path(destino).name}")
            continue

        print(f"   ⬇️  Baixando {Path(destino).name}...")
        try:
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            with open(destino, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"   ✅ Salvo em: {destino}")

        except Exception as e:
            logger.error("❌ Falha ao baixar %s: %s", url, e)
            print(f"   ⚠️  Coloque o arquivo manualmente em: {destino}")

if __name__ == "__main__":
    extract()