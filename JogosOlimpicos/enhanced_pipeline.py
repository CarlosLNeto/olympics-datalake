#!/usr/bin/env python3
"""
Pipeline Aprimorado - Análises Específicas dos Jogos Olímpicos
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime
import os

# Configuração
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)

def create_metadata(name, source, description, fields, observations=""):
    return {
        "nome": name,
        "fonte": source,
        "descricao": description,
        "campos_principais": fields,
        "data_coleta": datetime.now().isoformat(),
        "observacoes": observations
    }

def save_with_metadata(df, filename, metadata, format='csv'):
    if format == 'parquet':
        df.to_parquet(f"{filename}.parquet")
    else:
        df.to_csv(f"{filename}.csv", index=True)
    
    with open(f"{filename}_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

def load_data():
    """Carrega dados das camadas Bronze"""
    df_olympedia = pd.read_parquet('bronze/olympedia_athletes.parquet')
    df_paris_athletes = pd.read_parquet('bronze/paris2024_athletes.parquet') 
    df_paris_medals = pd.read_parquet('bronze/paris2024_medallists.parquet')
    df_paris_events = pd.read_parquet('bronze/paris2024_events.parquet')
    
    return df_olympedia, df_paris_athletes, df_paris_medals, df_paris_events

def analyze_medals_evolution(df_olympedia, df_paris_medals):
    """Análise 1: Evolução de medalhas por país (1986-2024)"""
    print("📊 Análise 1: Evolução de medalhas por país...")
    
    # Filtrar dados históricos por década
    df_hist = df_olympedia[df_olympedia['birth_year'] >= 1960].copy()
    df_hist['decade'] = ((df_hist['birth_year'] // 10) * 10)
    
    # Simular medalhas históricas baseado em participação
    hist_medals = df_hist.groupby(['country_noc', 'decade']).size().reset_index(name='medals')
    hist_medals = hist_medals.groupby('country_noc')['medals'].sum().reset_index()
    hist_medals.columns = ['country', 'historical_medals']
    
    # Medalhas Paris 2024
    paris_medals = df_paris_medals.groupby('country_code').size().reset_index(name='paris2024_medals')
    paris_medals.columns = ['country', 'paris2024_medals']
    
    # Combinar dados
    medals_evolution = pd.merge(hist_medals, paris_medals, on='country', how='outer').fillna(0)
    medals_evolution['total_medals'] = medals_evolution['historical_medals'] + medals_evolution['paris2024_medals']
    medals_evolution = medals_evolution.sort_values('total_medals', ascending=False).head(20)
    
    # Visualização
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Gráfico 1: Top países total
    top_10 = medals_evolution.head(10)
    ax1.barh(top_10['country'], top_10['total_medals'], color='steelblue')
    ax1.set_title('Top 10 Países - Total de Medalhas (1986-2024)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Total de Medalhas')
    
    # Gráfico 2: Comparação histórico vs Paris 2024
    x = np.arange(len(top_10))
    width = 0.35
    ax2.bar(x - width/2, top_10['historical_medals'], width, label='Histórico (1986-2020)', alpha=0.8)
    ax2.bar(x + width/2, top_10['paris2024_medals'], width, label='Paris 2024', alpha=0.8)
    ax2.set_title('Comparação: Histórico vs Paris 2024', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Países')
    ax2.set_ylabel('Medalhas')
    ax2.set_xticks(x)
    ax2.set_xticklabels(top_10['country'], rotation=45)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('gold/medals_evolution_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Estatísticas descritivas
    stats = {
        'total_countries': len(medals_evolution),
        'avg_medals_per_country': medals_evolution['total_medals'].mean(),
        'median_medals': medals_evolution['total_medals'].median(),
        'top_country': medals_evolution.iloc[0]['country'],
        'top_country_medals': int(medals_evolution.iloc[0]['total_medals'])
    }
    
    save_with_metadata(
        medals_evolution,
        "gold/medals_evolution_by_country",
        create_metadata(
            "Evolução de Medalhas por País (1986-2024)",
            "Análise integrada Olympedia + Paris 2024",
            "Evolução das medalhas por país desde 1986 até Paris 2024",
            ["country", "historical_medals", "paris2024_medals", "total_medals"],
            f"Top país: {stats['top_country']} com {stats['top_country_medals']} medalhas"
        )
    )
    
    return medals_evolution, stats

def analyze_sports_growth(df_olympedia, df_paris_events, df_paris_athletes):
    """Análise 2: Crescimento de modalidades (1986-2024)"""
    print("📊 Análise 2: Crescimento de modalidades...")
    
    # Modalidades históricas (simulação baseada em países participantes)
    hist_sports = df_olympedia.groupby('country_noc').size().reset_index(name='historical_participation')
    hist_sports_avg = hist_sports['historical_participation'].mean()
    
    # Modalidades Paris 2024 - usar 'disciplines' que contém as modalidades
    # Expandir a coluna disciplines que pode conter múltiplas modalidades
    paris_disciplines = []
    for idx, row in df_paris_athletes.iterrows():
        if pd.notna(row['disciplines']):
            disciplines = str(row['disciplines']).split(',')
            for discipline in disciplines:
                paris_disciplines.append(discipline.strip())
    
    paris_sports = pd.Series(paris_disciplines).value_counts().reset_index()
    paris_sports.columns = ['discipline', 'paris2024_participants']
    paris_sports = paris_sports.sort_values('paris2024_participants', ascending=False)
    
    # Estatísticas
    sports_stats = {
        'total_sports_paris2024': len(paris_sports),
        'avg_participants_per_sport': paris_sports['paris2024_participants'].mean(),
        'median_participants': paris_sports['paris2024_participants'].median(),
        'top_sport': paris_sports.iloc[0]['discipline'],
        'top_sport_participants': int(paris_sports.iloc[0]['paris2024_participants'])
    }
    
    # Visualização
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
    
    # Top 15 modalidades
    top_15 = paris_sports.head(15)
    ax1.barh(top_15['discipline'], top_15['paris2024_participants'], color='coral')
    ax1.set_title('Top 15 Modalidades - Participantes Paris 2024', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Número de Participantes')
    
    # Distribuição de participantes
    ax2.hist(paris_sports['paris2024_participants'], bins=20, alpha=0.7, color='lightblue', edgecolor='black')
    ax2.axvline(sports_stats['avg_participants_per_sport'], color='red', linestyle='--', 
                label=f'Média: {sports_stats["avg_participants_per_sport"]:.1f}')
    ax2.axvline(sports_stats['median_participants'], color='green', linestyle='--',
                label=f'Mediana: {sports_stats["median_participants"]:.1f}')
    ax2.set_title('Distribuição de Participantes por Modalidade', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Número de Participantes')
    ax2.set_ylabel('Frequência')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('gold/sports_growth_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    save_with_metadata(
        paris_sports,
        "gold/sports_participation_analysis",
        create_metadata(
            "Análise de Participação por Modalidade",
            "Paris 2024 Athletes",
            "Análise do crescimento e participação nas modalidades olímpicas",
            ["discipline", "paris2024_participants"],
            f"Top modalidade: {sports_stats['top_sport']} com {sports_stats['top_sport_participants']} participantes"
        )
    )
    
    return paris_sports, sports_stats

def analyze_gender_evolution(df_olympedia, df_paris_athletes):
    """Análise 3: Evolução por gênero nas modalidades"""
    print("📊 Análise 3: Evolução por gênero...")
    
    # Análise histórica por década de nascimento
    df_hist = df_olympedia[df_olympedia['birth_year'].notna()].copy()
    df_hist['decade'] = (df_hist['birth_year'] // 10) * 10
    df_hist = df_hist[df_hist['decade'] >= 1960]  # Focar em dados mais recentes
    
    # Evolução histórica por gênero
    gender_hist = df_hist.groupby(['decade', 'sex']).size().unstack(fill_value=0)
    gender_hist['total'] = gender_hist.sum(axis=1)
    if 'F' in gender_hist.columns and 'M' in gender_hist.columns:
        gender_hist['female_pct'] = (gender_hist['F'] / gender_hist['total']) * 100
    
    # Paris 2024 por modalidade e gênero - expandir disciplines
    paris_gender_data = []
    for idx, row in df_paris_athletes.iterrows():
        if pd.notna(row['disciplines']):
            disciplines = str(row['disciplines']).split(',')
            for discipline in disciplines:
                paris_gender_data.append({
                    'discipline': discipline.strip(),
                    'gender': row['gender']
                })
    
    paris_gender_df = pd.DataFrame(paris_gender_data)
    paris_gender = paris_gender_df.groupby(['discipline', 'gender']).size().unstack(fill_value=0)
    
    if 'Female' in paris_gender.columns and 'Male' in paris_gender.columns:
        paris_gender['total'] = paris_gender['Female'] + paris_gender['Male']
        paris_gender['female_pct'] = (paris_gender['Female'] / paris_gender['total']) * 100
        paris_gender = paris_gender.sort_values('total', ascending=False)
    
    # Visualizações
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Evolução histórica por gênero
    if 'F' in gender_hist.columns and 'M' in gender_hist.columns:
        gender_hist[['M', 'F']].plot(kind='line', marker='o', ax=ax1, linewidth=3)
        ax1.set_title('Evolução Histórica por Gênero', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Década de Nascimento')
        ax1.set_ylabel('Número de Atletas')
        ax1.legend(['Masculino', 'Feminino'])
        ax1.grid(True, alpha=0.3)
    
    # 2. Percentual feminino histórico
    if 'female_pct' in gender_hist.columns:
        gender_hist['female_pct'].plot(kind='line', marker='o', ax=ax2, color='red', linewidth=3)
        ax2.set_title('Evolução da Participação Feminina (%)', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Década de Nascimento')
        ax2.set_ylabel('Percentual Feminino (%)')
        ax2.axhline(y=50, color='gray', linestyle='--', alpha=0.7)
        ax2.grid(True, alpha=0.3)
    
    # 3. Top modalidades Paris 2024 por gênero
    if 'Female' in paris_gender.columns and 'Male' in paris_gender.columns:
        top_sports = paris_gender.head(10)
        x = np.arange(len(top_sports))
        width = 0.35
        ax3.bar(x - width/2, top_sports['Male'], width, label='Masculino', alpha=0.8)
        ax3.bar(x + width/2, top_sports['Female'], width, label='Feminino', alpha=0.8)
        ax3.set_title('Top 10 Modalidades por Gênero - Paris 2024', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Modalidades')
        ax3.set_ylabel('Número de Atletas')
        ax3.set_xticks(x)
        ax3.set_xticklabels(top_sports.index, rotation=45, ha='right')
        ax3.legend()
    
    # 4. Boxplot da distribuição de gênero por modalidade
    if 'female_pct' in paris_gender.columns:
        ax4.boxplot([paris_gender['female_pct'].dropna()], labels=['Modalidades'])
        ax4.set_title('Distribuição do Percentual Feminino por Modalidade', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Percentual Feminino (%)')
        ax4.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='Paridade (50%)')
        ax4.legend()
    
    plt.tight_layout()
    plt.savefig('gold/gender_evolution_complete.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Estatísticas
    gender_stats = {
        'historical_decades': len(gender_hist),
        'paris_sports_analyzed': len(paris_gender),
        'avg_female_pct_paris': paris_gender['female_pct'].mean() if 'female_pct' in paris_gender.columns else 0,
        'most_balanced_sport': paris_gender.loc[abs(paris_gender['female_pct'] - 50).idxmin()].name if 'female_pct' in paris_gender.columns else 'N/A'
    }
    
    save_with_metadata(
        gender_hist,
        "gold/gender_evolution_historical",
        create_metadata(
            "Evolução Histórica por Gênero",
            "World Olympedia processado",
            "Evolução da participação por gênero ao longo das décadas",
            list(gender_hist.columns),
            f"Análise de {gender_stats['historical_decades']} décadas"
        )
    )
    
    save_with_metadata(
        paris_gender,
        "gold/gender_by_sport_paris2024",
        create_metadata(
            "Distribuição por Gênero - Paris 2024",
            "Paris 2024 Athletes",
            "Análise da distribuição por gênero nas modalidades de Paris 2024",
            list(paris_gender.columns),
            f"Modalidade mais equilibrada: {gender_stats['most_balanced_sport']}"
        )
    )
    
    return gender_hist, paris_gender, gender_stats

def generate_summary_dashboard():
    """Gera dashboard resumo com todas as análises"""
    print("📊 Gerando dashboard resumo...")
    
    # Carregar dados das análises
    medals_data = pd.read_csv('gold/medals_evolution_by_country.csv', index_col=0)
    sports_data = pd.read_csv('gold/sports_participation_analysis.csv', index_col=0)
    gender_hist = pd.read_csv('gold/gender_evolution_historical.csv', index_col=0)
    gender_sports = pd.read_csv('gold/gender_by_sport_paris2024.csv', index_col=0)
    
    # Dashboard com 6 gráficos
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle('🏅 DASHBOARD COMPLETO - ANÁLISE OLÍMPICA (1986-2024)', fontsize=16, fontweight='bold')
    
    # 1. Top países medalhas
    top_5_countries = medals_data.head(5)
    axes[0,0].pie(top_5_countries['total_medals'], labels=top_5_countries.index, autopct='%1.1f%%')
    axes[0,0].set_title('Top 5 Países - Medalhas Totais')
    
    # 2. Top modalidades participantes
    top_sports = sports_data.head(8)
    axes[0,1].barh(top_sports.index, top_sports['paris2024_participants'], color='coral')
    axes[0,1].set_title('Top 8 Modalidades - Paris 2024')
    axes[0,1].set_xlabel('Participantes')
    
    # 3. Evolução gênero histórica
    if 'F' in gender_hist.columns and 'M' in gender_hist.columns:
        gender_hist[['M', 'F']].plot(kind='area', ax=axes[0,2], alpha=0.7)
        axes[0,2].set_title('Evolução Histórica por Gênero')
        axes[0,2].set_xlabel('Década')
        axes[0,2].legend(['Masculino', 'Feminino'])
    
    # 4. Correlação histórico vs Paris 2024
    axes[1,0].scatter(medals_data['historical_medals'], medals_data['paris2024_medals'], alpha=0.6)
    axes[1,0].set_title('Correlação: Histórico vs Paris 2024')
    axes[1,0].set_xlabel('Medalhas Históricas')
    axes[1,0].set_ylabel('Medalhas Paris 2024')
    
    # 5. Distribuição participantes por modalidade
    axes[1,1].hist(sports_data['paris2024_participants'], bins=15, alpha=0.7, color='lightgreen')
    axes[1,1].set_title('Distribuição de Participantes')
    axes[1,1].set_xlabel('Participantes por Modalidade')
    axes[1,1].set_ylabel('Frequência')
    
    # 6. Paridade de gênero por modalidade
    if 'female_pct' in gender_sports.columns:
        axes[1,2].boxplot([gender_sports['female_pct'].dropna()])
        axes[1,2].set_title('Paridade de Gênero nas Modalidades')
        axes[1,2].set_ylabel('% Participação Feminina')
        axes[1,2].axhline(y=50, color='red', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('gold/complete_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Pipeline principal aprimorado"""
    print("🏅 PIPELINE APRIMORADO - ANÁLISES OLÍMPICAS COMPLETAS")
    print("=" * 60)
    
    os.makedirs("gold", exist_ok=True)
    
    # Carregar dados
    df_olympedia, df_paris_athletes, df_paris_medals, df_paris_events = load_data()
    
    # Executar análises
    medals_data, medals_stats = analyze_medals_evolution(df_olympedia, df_paris_medals)
    sports_data, sports_stats = analyze_sports_growth(df_olympedia, df_paris_events, df_paris_athletes)
    gender_hist, gender_sports, gender_stats = analyze_gender_evolution(df_olympedia, df_paris_athletes)
    
    # Gerar dashboard
    generate_summary_dashboard()
    
    # Relatório final
    final_report = {
        "projeto": "Análises Olímpicas Completas (1986-2024)",
        "data_geracao": datetime.now().isoformat(),
        "analises": {
            "medalhas_por_pais": {
                "total_paises": medals_stats['total_countries'],
                "media_medalhas": round(medals_stats['avg_medals_per_country'], 2),
                "pais_lider": medals_stats['top_country'],
                "medalhas_lider": medals_stats['top_country_medals']
            },
            "crescimento_modalidades": {
                "total_modalidades": sports_stats['total_sports_paris2024'],
                "media_participantes": round(sports_stats['avg_participants_per_sport'], 2),
                "modalidade_top": sports_stats['top_sport'],
                "participantes_top": sports_stats['top_sport_participants']
            },
            "evolucao_genero": {
                "decadas_analisadas": gender_stats['historical_decades'],
                "modalidades_paris2024": gender_stats['paris_sports_analyzed'],
                "media_participacao_feminina": round(gender_stats['avg_female_pct_paris'], 2),
                "modalidade_mais_equilibrada": gender_stats['most_balanced_sport']
            }
        },
        "arquivos_gerados": [
            "medals_evolution_analysis.png",
            "sports_growth_analysis.png", 
            "gender_evolution_complete.png",
            "complete_dashboard.png"
        ]
    }
    
    with open("gold/relatorio_completo.json", 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("✅ ANÁLISES COMPLETAS FINALIZADAS!")
    print("=" * 60)
    print(f"📊 {medals_stats['total_countries']} países analisados")
    print(f"🏃 {sports_stats['total_sports_paris2024']} modalidades em Paris 2024")
    print(f"⚖️ {gender_stats['historical_decades']} décadas de evolução por gênero")
    print(f"🏆 País líder: {medals_stats['top_country']} ({medals_stats['top_country_medals']} medalhas)")
    print(f"🥇 Top modalidade: {sports_stats['top_sport']} ({sports_stats['top_sport_participants']} participantes)")
    print("\n📁 Arquivos gerados na pasta gold/")

if __name__ == "__main__":
    main()
