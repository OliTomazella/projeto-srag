import sys
sys.path.append(r"C:\Projeto_SRAG")

import duckdb
from config import SRAG_2023, SRAG_2024, SRAG_SILVER, CSV_DELIM

def transform():
    con = duckdb.connect()
    print("Iniciando transformação...")  # Conexão in-memory do DuckDB

    # Macro reutilizável: lê um CSV e aplica todas as transformações
    def source_query(path: str, ano: str) -> str:
        return f"""
            SELECT
                -- Identificação
                SG_UF_NOT,

                CASE CS_SEXO
                    WHEN 'M' THEN 'Masculino'
                    WHEN 'F' THEN 'Feminino'
                    WHEN 'I' THEN 'Ignorado'
                    ELSE 'Não informado'
                END AS CS_SEXO,

                -- Decodifica idade para anos
                CASE CAST(TRY_CAST(COD_IDADE AS INTEGER) / 1000 AS INTEGER)
                    WHEN 3 THEN (TRY_CAST(COD_IDADE AS INTEGER) % 1000)
                    WHEN 2 THEN ROUND((TRY_CAST(COD_IDADE AS INTEGER) % 1000) / 12.0, 1)
                    WHEN 1 THEN ROUND((TRY_CAST(COD_IDADE AS INTEGER) % 1000) / 365.0, 1)
                    ELSE NULL
                END AS IDADE_ANOS,

                -- Internação
                CASE HOSPITAL
                    WHEN 1 THEN 'Sim' WHEN 2 THEN 'Não'
                    WHEN 9 THEN 'Ignorado' ELSE 'Não informado'
                END AS HOSPITAL,

                CASE UTI
                    WHEN 1 THEN 'Sim' WHEN 2 THEN 'Não'
                    WHEN 9 THEN 'Ignorado' ELSE 'Não informado'
                END AS UTI,

                CASE SUPORT_VEN
                    WHEN 1 THEN 'Sim, invasivo'
                    WHEN 2 THEN 'Sim, não invasivo'
                    WHEN 3 THEN 'Não'
                    ELSE 'Não informado'
                END AS SUPORT_VEN,

                -- Datas
                TRY_CAST(DT_SIN_PRI AS DATE) AS DT_SIN_PRI,
                TRY_CAST(DT_NOTIFIC AS DATE) AS DT_NOTIFIC,
                TRY_CAST(DT_INTERNA AS DATE) AS DT_INTERNA,
                TRY_CAST(DT_EVOLUCA AS DATE) AS DT_EVOLUCA,

                -- Comorbidades
                CASE CARDIOPATI
                    WHEN 1 THEN 'Sim' WHEN 2 THEN 'Não'
                    WHEN 9 THEN 'Ignorado' ELSE 'Não informado'
                END AS CARDIOPATI,

                CASE DIABETES
                    WHEN 1 THEN 'Sim' WHEN 2 THEN 'Não'
                    WHEN 9 THEN 'Ignorado' ELSE 'Não informado'
                END AS DIABETES,

                CASE OBESIDADE
                    WHEN 1 THEN 'Sim' WHEN 2 THEN 'Não'
                    WHEN 9 THEN 'Ignorado' ELSE 'Não informado'
                END AS OBESIDADE,

                CASE PNEUMOPATI
                    WHEN 1 THEN 'Sim' WHEN 2 THEN 'Não'
                    WHEN 9 THEN 'Ignorado' ELSE 'Não informado'
                END AS PNEUMOPATI,

                CASE IMUNODEPRE
                    WHEN 1 THEN 'Sim' WHEN 2 THEN 'Não'
                    WHEN 9 THEN 'Ignorado' ELSE 'Não informado'
                END AS IMUNODEPRE,

                CASE RENAL
                    WHEN 1 THEN 'Sim' WHEN 2 THEN 'Não'
                    WHEN 9 THEN 'Ignorado' ELSE 'Não informado'
                END AS RENAL,

                -- Desfecho
                CASE EVOLUCAO
                    WHEN 1 THEN 'Alta'
                    WHEN 2 THEN 'Óbito'
                    WHEN 3 THEN 'Óbito por outras causas'
                    WHEN 9 THEN 'Ignorado'
                    ELSE 'Não informado'
                END AS EVOLUCAO,

                CASE CLASSI_FIN
                    WHEN 1 THEN 'SRAG não especificado'
                    WHEN 2 THEN 'SRAG por Influenza'
                    WHEN 3 THEN 'SRAG por outro vírus respiratório'
                    WHEN 4 THEN 'SRAG por outro agente etiológico'
                    WHEN 5 THEN 'SRAG não identificado'
                    ELSE 'Não informado'
                END AS CLASSI_FIN,

                '{ano}' AS ANO_NOTIFIC

            FROM read_csv(
                '{path}',
                delim='{CSV_DELIM}',
                header=true,
                types={{'COD_IDADE': 'VARCHAR'}}
            )
            WHERE TRY_CAST(COD_IDADE AS INTEGER) IS NOT NULL
              AND CLASSI_FIN IS NOT NULL
        """

     # Une os dois anos sem repetir nenhuma lógica de transformação
    # Para adicionar 2025: UNION ALL {source_query(SRAG_2025, '2025')}
    query = f"""
        {source_query(SRAG_2023, '2023')}
        UNION ALL
        {source_query(SRAG_2024, '2024')}
    """

    print("Executando transformação...")
    df = con.sql(query).df()

    print(f"Registros transformados: {len(df)}")
    print(f"Colunas: {df.columns.tolist()}")
    print(f"\nAmostra:\n{df.head(3)}")

 # Renomeia colunas para o padrão snake_case da camada Silver
    df = df.rename(columns={
        'SG_UF_NOT'  : 'uf',
        'CS_SEXO'    : 'sexo',
        'IDADE_ANOS' : 'idade_anos',
        'HOSPITAL'   : 'hospitalizado',
        'UTI'        : 'uti',
        'SUPORT_VEN' : 'suporte_ventilatorio',
        'DT_SIN_PRI' : 'dt_primeiros_sintomas',
        'DT_NOTIFIC' : 'dt_notificacao',
        'DT_INTERNA' : 'dt_internacao',
        'DT_EVOLUCA' : 'dt_evolucao',
        'CARDIOPATI' : 'cardiopatia',
        'DIABETES'   : 'diabetes',
        'OBESIDADE'  : 'obesidade',
        'PNEUMOPATI' : 'pneumopatia',
        'IMUNODEPRE' : 'imunodepressao',
        'RENAL'      : 'doenca_renal',
        'EVOLUCAO'   : 'evolucao',
        'CLASSI_FIN' : 'classificacao_final',
        'ANO_NOTIFIC': 'ano',
    })

    df.to_parquet(SRAG_SILVER, index=False, compression='zstd')
    print(f"\nSalvo em: {SRAG_SILVER}")

if __name__ == "__main__":
    transform()