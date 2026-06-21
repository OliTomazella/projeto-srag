# config.py
import os

# Pega automaticamente a pasta raiz do projeto
ROOT = os.path.dirname(os.path.abspath(__file__))

# Camadas
BRONZE = os.path.join(ROOT, "Data", "01-Bronze")
PRATA  = os.path.join(ROOT, "Data", "02-Prata")
GOLD   = os.path.join(ROOT, "Data", "03-Gold")

# Arquivos de entrada
SRAG_2023 = os.path.join(BRONZE, "INFLUD23-23-03-2026.csv")
SRAG_2024 = os.path.join(BRONZE, "INFLUD24-23-03-2026.csv")

# Arquivos de saída Silver
SRAG_SILVER = os.path.join(PRATA, "srag_limpo.parquet")

# Arquivos de saída Gold
SRAG_GOLD = os.path.join(GOLD, "srag_agregado.parquet")

# Configurações do CSV
CSV_DELIM    = ";"
CSV_ENCODING = "latin1"
