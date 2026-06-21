# src/hospital.py
import duckdb
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class HospitalEngine:
    """
    Motor de análise hospitalar.
    Recebe a conexão e o caminho da camada Silver, expondo métodos
    que retornam DataFrames prontos para carga na Gold.
    """

    def __init__(self, con: duckdb.DuckDBPyConnection, silver: str | Path):
        self.con = con
        # Garante o uso de barras corretas independente do S.O. e formata para o DuckDB
        self.silver = Path(silver).as_posix()

    def _query(self, sql: str) -> duckdb.DuckDBPyRelation:
        """
        Executa uma query e retorna uma DuckDBPyRelation lazily.
        O log de erro e a conversão para DataFrame são centralizados.
        """
        try:
            # Mantém como Relation para otimização de plano de execução do DuckDB
            return self.con.sql(sql)
        except Exception as e:
            logger.error("Erro ao instanciar ou executar query SQL: %s", e)
            raise

    # ------------------------------------------------------------------
    # Pergunta 4: Perfil de quem foi para UTI
    # ------------------------------------------------------------------

    def perfil_uti(self) -> duckdb.DuckDBPyRelation:
        """
        Perfil dos pacientes que foram para UTI:
        idade média, sexo e comorbidades por ano.
        """
        return self._query(f"""
            SELECT
                ano,
                sexo,
                COUNT(*)                                                       AS total_uti,
                ROUND(AVG(idade_anos), 1)                                      AS media_idade,
                COUNT(CASE WHEN diabetes       = 'Sim' THEN 1 END)             AS com_diabetes,
                COUNT(CASE WHEN cardiopatia    = 'Sim' THEN 1 END)             AS com_cardiopatia,
                COUNT(CASE WHEN obesidade      = 'Sim' THEN 1 END)             AS com_obesidade,
                COUNT(CASE WHEN doenca_renal   = 'Sim' THEN 1 END)             AS com_doenca_renal,
                COUNT(CASE WHEN pneumopatia    = 'Sim' THEN 1 END)             AS com_pneumopatia,
                COUNT(CASE WHEN imunodepressao = 'Sim' THEN 1 END)             AS com_imunodepressao
            FROM '{self.silver}'
            WHERE uti = 'Sim'
            GROUP BY ano, sexo
            ORDER BY ano, total_uti DESC
        """)

    # ------------------------------------------------------------------
    # Pergunta 5: Tempo médio de internação
    # ------------------------------------------------------------------

    def tempo_medio_internacao(self) -> duckdb.DuckDBPyRelation:
        """
        Tempo médio em dias entre internação e desfecho clínico,
        separado por evolução (Alta vs Óbito) e ano.
        Garante apenas deltas positivos para evitar inconsistência de dados.
        """
        return self._query(f"""
            SELECT
                ano,
                evolucao,
                COUNT(*)                                                       AS total_casos,
                ROUND(AVG(date_diff('day', dt_internacao, dt_evolucao)), 1)    AS media_dias
            FROM '{self.silver}'
            WHERE dt_internacao IS NOT NULL
              AND dt_evolucao   IS NOT NULL
              AND evolucao IN ('Alta', 'Óbito')
              AND dt_evolucao >= dt_internacao -- Defesa contra outlier/erro de digitação no sistema hospitalar
            GROUP BY ano, evolucao
            ORDER BY ano, evolucao
        """)

    # ------------------------------------------------------------------
    # Pergunta 6: Comorbidades mais frequentes em óbitos
    # ------------------------------------------------------------------

    def comorbidades_em_obitos(self) -> duckdb.DuckDBPyRelation:
        """
        Quais comorbidades aparecem mais nos casos que evoluíram para óbito,
        por ano.
        """
        return self._query(f"""
            SELECT
                ano,
                COUNT(CASE WHEN diabetes       = 'Sim' THEN 1 END)             AS obitos_diabetes,
                COUNT(CASE WHEN cardiopatia    = 'Sim' THEN 1 END)             AS obitos_cardiopatia,
                COUNT(CASE WHEN obesidade      = 'Sim' THEN 1 END)             AS obitos_obesidade,
                COUNT(CASE WHEN doenca_renal   = 'Sim' THEN 1 END)             AS obitos_doenca_renal,
                COUNT(CASE WHEN pneumopatia    = 'Sim' THEN 1 END)             AS obitos_pneumopatia,
                COUNT(CASE WHEN imunodepressao = 'Sim' THEN 1 END)             AS obitos_imunodepressao
            FROM '{self.silver}'
            WHERE evolucao = 'Óbito'
            GROUP BY ano
            ORDER BY ano
        """)

    # ------------------------------------------------------------------
    # Atalho para rodar tudo de uma vez
    # ------------------------------------------------------------------

    def todas_as_analises(self) -> dict:
        """
        Executa todas as análises de forma eficiente, convertendo para DataFrame
        apenas no momento final da entrega dos dados.
        """
        # O .df() é chamado aqui de forma centralizada para poupar memória e otimizar I/O
        return {
            "perfil_uti": self.perfil_uti().df(),
            "tempo_internacao": self.tempo_medio_internacao().df(),
            "comorbidades_obitos": self.comorbidades_em_obitos().df(),
        }