#!/usr/bin/env python3
"""
Pipeline Completo do Data Lake - Jogos Olímpicos
Arquitetura: RAW → BRONZE → GOLD
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração de estilo
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def create_metadata(name, source, description, fields, observations=""):
    """Cria metadados padronizados"""
    return {
        "nome": name,
        "fonte": source,
        "descricao": description,
        "campos_principais": fields,
        "data_coleta": datetime.now().isoformat(),
        "observacoes": observations
    }

def save_with_metadata(df, filename, metadata, format='parquet'):
    """Salva arquivo com metadados"""
    if format == 'parquet':
        df.to_parquet(f"{filename}.parquet")
    else:
        df.to_csv(f"{filename}.csv", index=False)
    
    with open(f"{filename}_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

def process_raw_layer():
    """Processa camada RAW - cria metadados para dados brutos"""
    print("=== PROCESSANDO CAMADA RAW ===")
    
    # Metadados para world_olympedia
    olympedia_meta = create_metadata(
        "World Olympedia - Biografias de Atletas",
        "Olympedia.org",
        "Dataset histórico com biografias completas de atletas olímpicos",
        ["athlete_id", "name", "sex", "birth_date", "birth_year", "height", "weight", "country", "country_noc"],
        "Dados históricos de 1896 até jogos recentes"
    )
    
    with open("raw/world_olympedia_olympics_athlete_bio_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(olympedia_meta, f, indent=2, ensure_ascii=False)
    
    # Metadados para Paris 2024 - principais arquivos
    paris_files = {
        'athletes': "Atletas participantes de Paris 2024",
        'medallists': "Medalhistas de Paris 2024", 
        'medals': "Medalhas conquistadas em Paris 2024",
        'events': "Eventos esportivos de Paris 2024",
        'teams': "Equipes participantes de Paris 2024"
    }
    
    for file, desc in paris_files.items():
        meta = create_metadata(
            f"Paris 2024 - {file.title()}",
            "Kaggle - Paris 2024 Olympic Summer Games",
            desc,
            ["Varia por arquivo"],
            "Dados oficiais dos Jogos Olímpicos de Paris 2024"
        )
        
        with open(f"raw/paris2024_{file}_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
    
    print("✓ Metadados RAW criados")

def process_bronze_layer():
    """Processa camada BRONZE - converte para Parquet e integra dados"""
    print("\n=== PROCESSANDO CAMADA BRONZE ===")
    
    os.makedirs("bronze", exist_ok=True)
    
    # 1. Carregar e processar World Olympedia
    print("Processando World Olympedia...")
    df_olympedia = pd.read_csv("raw/world_olympedia_olympics_athlete_bio.csv")
    
    # Limpeza básica
    df_olympedia['birth_year'] = pd.to_numeric(df_olympedia['birth_year'], errors='coerce')
    df_olympedia['height'] = pd.to_numeric(df_olympedia['height'], errors='coerce') 
    df_olympedia['weight'] = pd.to_numeric(df_olympedia['weight'], errors='coerce')
    
    save_with_metadata(
        df_olympedia, 
        "bronze/olympedia_athletes",
        create_metadata(
            "Atletas Olímpicos Históricos (Bronze)",
            "World Olympedia processado",
            "Dataset limpo de biografias de atletas olímpicos",
            ["athlete_id", "name", "sex", "birth_year", "height", "weight", "country"],
            f"Processado em Parquet. Total: {len(df_olympedia)} atletas"
        )
    )
    
    # 2. Carregar e processar Paris 2024
    print("Processando Paris 2024...")
    
    # Athletes
    df_paris_athletes = pd.read_csv("raw/paris2024_athletes.csv")
    save_with_metadata(
        df_paris_athletes,
        "bronze/paris2024_athletes", 
        create_metadata(
            "Atletas Paris 2024 (Bronze)",
            "Kaggle Paris 2024 processado",
            "Atletas participantes dos Jogos de Paris 2024",
            list(df_paris_athletes.columns),
            f"Total: {len(df_paris_athletes)} atletas"
        )
    )
    
    # Medallists
    df_medallists = pd.read_csv("raw/paris2024_medallists.csv")
    save_with_metadata(
        df_medallists,
        "bronze/paris2024_medallists",
        create_metadata(
            "Medalhistas Paris 2024 (Bronze)", 
            "Kaggle Paris 2024 processado",
            "Medalhistas dos Jogos de Paris 2024",
            list(df_medallists.columns),
            f"Total: {len(df_medallists)} medalhas"
        )
    )
    
    # Events
    df_events = pd.read_csv("raw/paris2024_events.csv")
    save_with_metadata(
        df_events,
        "bronze/paris2024_events",
        create_metadata(
            "Eventos Paris 2024 (Bronze)",
            "Kaggle Paris 2024 processado", 
            "Eventos esportivos dos Jogos de Paris 2024",
            list(df_events.columns),
            f"Total: {len(df_events)} eventos"
        )
    )
    
    # 3. Integração de dados
    print("Integrando dados...")
    
    # Análise de países por participação histórica vs Paris 2024
    countries_historical = df_olympedia['country_noc'].value_counts().head(20)
    countries_paris = df_paris_athletes['country_code'].value_counts().head(20)
    
    integration_df = pd.DataFrame({
        'country': countries_historical.index,
        'historical_athletes': countries_historical.values
    })
    
    # Merge com Paris 2024
    paris_counts = df_paris_athletes['country_code'].value_counts().to_dict()
    integration_df['paris2024_athletes'] = integration_df['country'].map(paris_counts).fillna(0)
    
    save_with_metadata(
        integration_df,
        "bronze/countries_comparison",
        create_metadata(
            "Comparação Países - Histórico vs Paris 2024",
            "Integração World Olympedia + Paris 2024",
            "Comparação da participação de países entre dados históricos e Paris 2024",
            ["country", "historical_athletes", "paris2024_athletes"],
            "Top 20 países por participação histórica"
        )
    )
    
    print(f"✓ Bronze processado: {len(df_olympedia)} atletas históricos, {len(df_paris_athletes)} atletas Paris 2024")
    return df_olympedia, df_paris_athletes, df_medallists, df_events, integration_df

def process_gold_layer(df_olympedia, df_paris_athletes, df_medallists, df_events, integration_df):
    """Processa camada GOLD - análises e visualizações"""
    print("\n=== PROCESSANDO CAMADA GOLD ===")
    
    os.makedirs("gold", exist_ok=True)
    
    # Análise 1: Evolução da participação por gênero ao longo do tempo
    print("Análise 1: Evolução por gênero...")
    
    # Filtrar dados com anos válidos
    df_gender = df_olympedia[df_olympedia['birth_year'].notna()].copy()
    df_gender['decade'] = (df_gender['birth_year'] // 10) * 10
    
    gender_evolution = df_gender.groupby(['decade', 'sex']).size().unstack(fill_value=0)
    gender_evolution['total'] = gender_evolution.sum(axis=1)
    if 'F' in gender_evolution.columns:
        gender_evolution['female_pct'] = (gender_evolution['F'] / gender_evolution['total']) * 100
    
    # Gráfico
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    if 'M' in gender_evolution.columns and 'F' in gender_evolution.columns:
        gender_evolution[['M', 'F']].plot(kind='line', marker='o', ax=ax1)
        ax1.set_title('Evolução da Participação por Gênero')
        ax1.set_xlabel('Década de Nascimento')
        ax1.set_ylabel('Número de Atletas')
        ax1.legend(['Masculino', 'Feminino'])
        
        gender_evolution['female_pct'].plot(kind='line', marker='o', ax=ax2, color='red')
        ax2.set_title('Percentual de Participação Feminina')
        ax2.set_xlabel('Década de Nascimento')
        ax2.set_ylabel('Percentual (%)')
    
    plt.tight_layout()
    plt.savefig('gold/gender_evolution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    save_with_metadata(
        gender_evolution,
        "gold/gender_evolution",
        create_metadata(
            "Evolução da Participação por Gênero",
            "Análise World Olympedia",
            "Evolução da participação masculina e feminina por década de nascimento",
            ["M", "F", "total", "female_pct"],
            "Baseado em década de nascimento dos atletas"
        ),
        format='csv'
    )
    
    # Análise 2: Top países por medalhas em Paris 2024
    print("Análise 2: Medalhas Paris 2024...")
    
    medals_by_country = df_medallists.groupby(['country_code', 'medal_type']).size().unstack(fill_value=0)
    medals_by_country['total'] = medals_by_country.sum(axis=1)
    top_countries = medals_by_country.sort_values('total', ascending=False).head(15)
    
    # Gráfico
    plt.figure(figsize=(12, 8))
    medal_cols = [col for col in ['Gold Medal', 'Silver Medal', 'Bronze Medal'] if col in top_countries.columns]
    if medal_cols:
        top_countries[medal_cols].plot(kind='barh', stacked=True, 
                                       color=['gold', 'silver', '#CD7F32'])
        plt.title('Top 15 Países - Medalhas Paris 2024')
        plt.xlabel('Número de Medalhas')
        plt.ylabel('País')
        plt.legend(title='Tipo de Medalha', labels=['Ouro', 'Prata', 'Bronze'])
    plt.tight_layout()
    plt.savefig('gold/paris2024_medals.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    save_with_metadata(
        top_countries,
        "gold/paris2024_medals",
        create_metadata(
            "Medalhas por País - Paris 2024",
            "Análise Paris 2024 Medallists",
            "Distribuição de medalhas por país nos Jogos de Paris 2024",
            ["Gold Medal", "Silver Medal", "Bronze Medal", "total"],
            f"Top 15 países. Total de medalhas: {top_countries['total'].sum()}"
        ),
        format='csv'
    )
    
    # Análise 3: Comparação histórica vs Paris 2024
    print("Análise 3: Comparação histórica...")
    
    plt.figure(figsize=(12, 8))
    plt.scatter(integration_df['historical_athletes'], integration_df['paris2024_athletes'], 
                alpha=0.7, s=100)
    
    # Adicionar linha de tendência
    z = np.polyfit(integration_df['historical_athletes'], integration_df['paris2024_athletes'], 1)
    p = np.poly1d(z)
    plt.plot(integration_df['historical_athletes'], p(integration_df['historical_athletes']), 
             "r--", alpha=0.8)
    
    plt.xlabel('Atletas Históricos (Total)')
    plt.ylabel('Atletas Paris 2024')
    plt.title('Correlação: Participação Histórica vs Paris 2024')
    
    # Anotar países principais
    for i, row in integration_df.head(5).iterrows():
        plt.annotate(row['country'], (row['historical_athletes'], row['paris2024_athletes']),
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('gold/historical_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    save_with_metadata(
        integration_df,
        "gold/historical_comparison", 
        create_metadata(
            "Comparação Histórica vs Paris 2024",
            "Integração de datasets",
            "Análise comparativa da participação de países entre dados históricos e Paris 2024",
            ["country", "historical_athletes", "paris2024_athletes"],
            "Correlação entre participação histórica e atual"
        ),
        format='csv'
    )
    
    # Relatório final
    report = {
        "projeto": "Data Lake - Jogos Olímpicos",
        "data_geracao": datetime.now().isoformat(),
        "datasets_processados": {
            "raw": ["world_olympedia_olympics_athlete_bio.csv", "paris2024_*.csv"],
            "bronze": ["olympedia_athletes.parquet", "paris2024_*.parquet", "countries_comparison.parquet"],
            "gold": ["gender_evolution.csv", "paris2024_medals.csv", "historical_comparison.csv"]
        },
        "analises_realizadas": [
            {
                "nome": "Evolução por Gênero",
                "arquivo": "gender_evolution.csv",
                "grafico": "gender_evolution.png",
                "insights": "Crescimento da participação feminina ao longo das décadas"
            },
            {
                "nome": "Medalhas Paris 2024", 
                "arquivo": "paris2024_medals.csv",
                "grafico": "paris2024_medals.png",
                "insights": f"Top país: {top_countries.index[0]} com {top_countries.iloc[0]['total']} medalhas"
            },
            {
                "nome": "Comparação Histórica",
                "arquivo": "historical_comparison.csv", 
                "grafico": "historical_comparison.png",
                "insights": "Correlação positiva entre participação histórica e atual"
            }
        ],
        "estatisticas": {
            "total_atletas_historicos": len(df_olympedia),
            "total_atletas_paris2024": len(df_paris_athletes),
            "total_medalhas_paris2024": len(df_medallists),
            "paises_analisados": len(integration_df)
        }
    }
    
    with open("gold/relatorio_final.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("✓ Análises Gold concluídas")
    return report

def main():
    """Pipeline principal"""
    print("🏅 PIPELINE COMPLETO - DATA LAKE OLÍMPICO")
    print("=" * 50)
    
    # Processar camadas
    process_raw_layer()
    df_olympedia, df_paris_athletes, df_medallists, df_events, integration_df = process_bronze_layer()
    report = process_gold_layer(df_olympedia, df_paris_athletes, df_medallists, df_events, integration_df)
    
    print("\n" + "=" * 50)
    print("✅ PIPELINE CONCLUÍDO COM SUCESSO!")
    print("=" * 50)
    print(f"📊 Processados: {report['estatisticas']['total_atletas_historicos']:,} atletas históricos")
    print(f"🥇 Paris 2024: {report['estatisticas']['total_atletas_paris2024']:,} atletas, {report['estatisticas']['total_medalhas_paris2024']:,} medalhas")
    print(f"🌍 Países analisados: {report['estatisticas']['paises_analisados']}")
    print("\n📁 Estrutura criada:")
    print("   raw/ - Dados brutos + metadados")
    print("   bronze/ - Dados processados (Parquet)")
    print("   gold/ - Análises + visualizações")

if __name__ == "__main__":
    main()
