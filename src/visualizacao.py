# src/visualizacao.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from config import GOLD

def grafico_obitos_por_estado():
    # Carrega o parquet da Gold
    df = pd.read_parquet(os.path.join(GOLD, "obitos_por_estado.parquet"))

    # Pega top 10 estados com maior taxa em 2023 para focar o gráfico
    top_estados = (
        df[df['ano'] == '2023']
        .nlargest(10, 'taxa_obito_pct')['uf']
        .tolist()
    )
    df_filtrado = df[df['uf'].isin(top_estados)].copy()

    # Configuração visual
    sns.set_theme(style="whitegrid", palette="muted")
    fig, ax = plt.subplots(figsize=(14, 7))

    sns.barplot(
        data=df_filtrado,
        x='uf',
        y='taxa_obito_pct',
        hue='ano',
        ax=ax,
        palette={'2023': '#E05C5C', '2024': '#5C9BE0'}
    )

    # Linha da média nacional
    media_2023 = df[df['ano'] == '2023']['taxa_obito_pct'].mean()
    media_2024 = df[df['ano'] == '2024']['taxa_obito_pct'].mean()
    ax.axhline(media_2023, color='#E05C5C', linestyle='--', linewidth=1.2, alpha=0.7, label=f'Média 2023: {media_2023:.1f}%')
    ax.axhline(media_2024, color='#5C9BE0', linestyle='--', linewidth=1.2, alpha=0.7, label=f'Média 2024: {media_2024:.1f}%')

    # Anotação do Tocantins
    ax.annotate(
        '⚠️ TO: taxa quase\no dobro da média',
        xy=(0, df_filtrado[(df_filtrado['uf'] == 'TO') & (df_filtrado['ano'] == '2023')]['taxa_obito_pct'].values[0]),
        xytext=(1.5, 17),
        fontsize=9,
        color='#E05C5C',
        arrowprops=dict(arrowstyle='->', color='#E05C5C')
    )

    # Formatação
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=1))
    ax.set_title('Taxa de Óbito por SRAG — Top 10 Estados (2023 vs 2024)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Estado', fontsize=11)
    ax.set_ylabel('Taxa de Óbito (%)', fontsize=11)
    ax.legend(title='Ano', fontsize=10)

    plt.tight_layout()

    # Salva na raiz do projeto
    output = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "grafico_obitos.png")
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"✅ Gráfico salvo em: {output}")
    plt.show()

if __name__ == "__main__":
    grafico_obitos_por_estado()