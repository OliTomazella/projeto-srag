# main.py
import sys
import os
import time
import logging

# Garante que o src/ é encontrado ANTES de qualquer import local
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

from extract import extract
from transform import transform
from load import load


def main():
    print("=" * 60)
    print("🚀 PIPELINE SRAG — BRONZE → SILVER → GOLD")
    print("=" * 60)

    inicio_total = time.time()

    # ETAPA 0: EXTRAÇÃO
    print("\n📥 ETAPA 0: Extração...")
    inicio = time.time()
    try:
        extract()
        print(f"✅ Extração concluída em {time.time() - inicio:.1f}s")
    except Exception as e:
        logger.error("❌ Falha na extração: %s", e)
        sys.exit(1)

    # ETAPA 1: TRANSFORMAÇÃO
    print("\n📦 ETAPA 1: Transformação...")
    inicio = time.time()
    try:
        transform()
        print(f"✅ Transformação concluída em {time.time() - inicio:.1f}s")
    except Exception as e:
        logger.error("❌ Falha na transformação: %s", e)
        sys.exit(1)

    # ETAPA 2: CARGA
    print("\n📦 ETAPA 2: Carga...")
    inicio = time.time()
    try:
        load()
        print(f"✅ Carga concluída em {time.time() - inicio:.1f}s")
    except Exception as e:
        logger.error("❌ Falha na carga: %s", e)
        sys.exit(1)

    # RESUMO FINAL
    total = time.time() - inicio_total
    print("\n" + "=" * 60)
    print(f"✅ PIPELINE CONCLUÍDO EM {total:.1f}s")
    print("=" * 60)
    print("\n📁 Arquivos gerados na Gold:")

    from config import GOLD
    for arquivo in sorted(os.listdir(GOLD)):
        if arquivo.endswith(".parquet"):
            tamanho = os.path.getsize(os.path.join(GOLD, arquivo)) / 1024
            print(f"   • {arquivo} ({tamanho:.1f} KB)")


if __name__ == "__main__":
    main()