import duckdb
import os

def obitos_por_estado(con, silver):
    return con.sql(f"""
        SELECT
            uf, ano,
            COUNT(*) AS total_casos,
            SUM(CASE WHEN evolucao = 'Óbito' THEN 1 ELSE 0 END) AS total_obitos,
            ROUND(
                SUM(CASE WHEN evolucao = 'Óbito' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
                2
            ) AS taxa_obito_pct
        FROM '{silver}'
        WHERE uf IS NOT NULL
        GROUP BY uf, ano
        ORDER BY ano, taxa_obito_pct DESC
    """).df()

def comparativo_anos(con, silver):
    return con.sql(f"""
        SELECT
            ano,
            COUNT(*) AS total_casos,
            SUM(CASE WHEN evolucao = 'Óbito' THEN 1 ELSE 0 END) AS total_obitos,
            ROUND(
                SUM(CASE WHEN evolucao = 'Óbito' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
                2
            ) AS taxa_obito_pct
        FROM '{silver}'
        GROUP BY ano
        ORDER BY ano
    """).df()

def pressao_uti(con, silver):
    return con.sql(f"""
        SELECT
            uf, ano,
            COUNT(*) AS total_casos,
            SUM(CASE WHEN uti = 'Sim' THEN 1 ELSE 0 END) AS total_uti,
            ROUND(
                SUM(CASE WHEN uti = 'Sim' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
                2
            ) AS taxa_uti_pct
        FROM '{silver}'
        WHERE uf IS NOT NULL
        GROUP BY uf, ano
        ORDER BY ano, taxa_uti_pct DESC
    """).df()