# 🏅 Data Lake Olímpico - Análise Completa dos Jogos Olímpicos

## 📋 Visão Geral

Este projeto implementa uma **arquitetura completa de Data Lake** para análise dos Jogos Olímpicos, integrando dados históricos com informações atuais de Paris 2024. O objetivo é demonstrar boas práticas de engenharia de dados e gerar insights valiosos sobre a evolução olímpica.

## 🏗️ Arquitetura do Data Lake

### Camadas Implementadas

```
📁 raw/           # Dados brutos originais + metadados
📁 bronze/        # Dados processados e limpos (Parquet)
📁 gold/          # Análises finais e visualizações
```

### **RAW Layer** - Dados Brutos
- **World Olympedia**: 155.861 biografias de atletas históricos
- **Paris 2024**: 13 datasets oficiais (atletas, medalhas, eventos, etc.)
- Cada arquivo possui metadados JSON descritivos
- Formato original preservado (CSV)

### **BRONZE Layer** - Dados Processados
- Conversão para formato Parquet (otimizado para analytics)
- Limpeza e padronização dos dados
- Integração entre diferentes fontes
- Metadados técnicos para cada dataset

### **GOLD Layer** - Análises e Insights
- 3 análises estratégicas principais
- Visualizações profissionais (PNG)
- Tabelas resumo (CSV)
- Relatórios executivos (JSON)

## 📊 Datasets Principais

### 1. World Olympedia (Histórico)
- **Fonte**: Olympedia.org
- **Período**: 1896 até jogos recentes
- **Conteúdo**: Biografias completas de atletas
- **Campos**: ID, nome, gênero, nascimento, altura, peso, país

### 2. Paris 2024 (Atual)
- **Fonte**: Kaggle - Dados oficiais
- **Conteúdo**: Atletas, medalhas, eventos, equipes
- **Total**: 11.113 atletas, 2.315 medalhas
- **Cobertura**: Todos os esportes e modalidades

## 🎯 Análises Realizadas

### 1. **Evolução da Participação por Gênero**
- Análise temporal da inclusão feminina
- Baseada na década de nascimento dos atletas
- Visualização de tendências históricas

### 2. **Performance por País - Paris 2024**
- Ranking de medalhas por nação
- Distribuição por tipo (ouro, prata, bronze)
- Top 15 países com melhor performance

### 3. **Comparação Histórica vs Atual**
- Correlação entre tradição olímpica e participação atual
- Análise de países emergentes vs estabelecidos
- Scatter plot com linha de tendência

## 📈 Principais Descobertas

### 🥇 Medalhas Paris 2024
- **USA** liderou com ~320 medalhas totais
- **França** (país-sede) ficou em 2º lugar
- Forte correlação entre tradição histórica e performance atual

### 🌍 Participação Global
- 20 países analisados na comparação histórica
- Correlação positiva significativa (r > 0.7)
- Países tradicionais mantêm grandes delegações

### 👥 Inclusão e Diversidade
- Crescimento consistente da participação feminina
- Evolução positiva ao longo das décadas
- Tendência de maior equidade de gênero

## 🚀 Como Executar

### Pré-requisitos
```bash
pip install -r requirements.txt
```

### Pipeline Completo
```bash
# Executar pipeline completo
python complete_pipeline.py

# Análise interativa
jupyter notebook olympics_complete_analysis.ipynb
```

### Estrutura de Execução
1. **RAW**: Metadados criados automaticamente
2. **BRONZE**: Processamento e conversão para Parquet
3. **GOLD**: Geração de análises e visualizações

## 📁 Arquivos Principais

### Scripts de Processamento
- `complete_pipeline.py` - Pipeline principal RAW → BRONZE → GOLD
- `download_paris2024.py` - Download automático dos dados Paris 2024

### Notebooks
- `olympics_complete_analysis.ipynb` - Análise completa e interativa

### Configuração
- `requirements.txt` - Dependências Python
- `metadata_schema.json` - Schema técnico dos metadados

## 🔧 Tecnologias Utilizadas

- **Python**: Linguagem principal
- **Pandas**: Manipulação de dados
- **Parquet**: Formato otimizado para analytics
- **Matplotlib/Seaborn**: Visualizações profissionais
- **Jupyter**: Análise interativa
- **JSON**: Metadados estruturados
- **KaggleHub**: Download automático de datasets

## 📊 Estatísticas do Projeto

- **155.861** atletas históricos processados
- **11.113** atletas de Paris 2024
- **2.315** medalhas analisadas
- **3** análises estratégicas
- **22** visualizações geradas
- **100%** cobertura de metadados

## 🎯 Próximos Passos

- Expandir para análises por modalidade específica
- Incluir dados de performance (tempos, recordes)
- Implementar análises preditivas
- Automatizar pipeline com novos dados
- Dashboard interativo com Streamlit/Dash

## 📝 Contribuição

Este projeto demonstra:
- Arquitetura moderna de Data Lake
- Boas práticas de engenharia de dados
- Análises estatísticas avançadas
- Visualizações profissionais
- Documentação completa

---

**🏆 Projeto desenvolvido como demonstração de competências em Ciência de Dados e Engenharia de Dados**
