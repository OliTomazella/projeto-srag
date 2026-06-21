import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import duckdb
from config import SRAG_SILVER, GOLD
from saude_publica import obitos_por_estado, comparativo_anos, pressao_uti
from hospital import HospitalEngine

def load():
    con = duckdb.connect()
    print("=" * 50)
    print("📊 PRATA → GOLD")
    print("=" * 50)

    # Saúde Pública
    print("\n🔍 Saúde Pública...")
    df1 = obitos_por_estado(con, SRAG_SILVER)
    df2 = comparativo_anos(con, SRAG_SILVER)
    df3 = pressao_uti(con, SRAG_SILVER)

    print(df1.head(10).to_string())
    print(df2.to_string())
    print(df3.head(10).to_string())

    df1.to_parquet(os.path.join(GOLD, "obitos_por_estado.parquet"), index=False, compression='zstd')
    df2.to_parquet(os.path.join(GOLD, "comparativo_anos.parquet"), index=False, compression='zstd')
    df3.to_parquet(os.path.join(GOLD, "pressao_uti.parquet"), index=False, compression='zstd')

    # Hospital
    print("\n🏥 Hospital...")
    engine = HospitalEngine(con, SRAG_SILVER)
    resultados = engine.todas_as_analises()

    for nome, df in resultados.items():
        print(f"\n📊 {nome}:")
        print(df.to_string())
        df.to_parquet(
            os.path.join(GOLD, f"hospital_{nome}.parquet"),
            index=False,
            compression='zstd'
        )

    print("\n✅ Gold gerada!")

if __name__ == "__main__":
    load()