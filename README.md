# 🥊 UFC Data Analytics Pipeline & Scouting Dashboard

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![Power BI](https://img.shields.io/badge/power_bi-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)

## 📌 Sobre o Projeto
Este projeto é um pipeline completo de Extração, Transformação e Carga (ETL) focado em dados de artes marciais mistas (MMA), culminando em um **Dashboard Interativo de Scouting**. O objetivo é construir uma base de dados analítica robusta a partir do histórico de milhares de lutadores do UFC, unindo conhecimento de domínio no esporte com práticas modernas de Engenharia de Dados e visualização.

O sistema coleta estatísticas detalhadas (Striking, Grappling, Cartel), estrutura esses dados em documentos NoSQL para suportar aninhamento complexo, permite a exportação achatada (flattening) e, finalmente, consome esses dados em um painel analítico (Power BI) para tomada de decisão tática e ranqueamento de atletas.


## 🏗️ Arquitetura e Fluxo de Dados

O pipeline foi desenhado separando a ingestão (scraping seguro) da camada de consumo (análise), garantindo resiliência contra falhas de rede e bloqueios.

1. **Extract (Web Scraping):** Varredura do site UFCStats utilizando `requests` e `BeautifulSoup`. Implementação de Sessões Robustas (com User-Agent customizado e `urllib3 Retry`) para contornar timeouts e bloqueios (*Rate Limiting*).
2. **Transform (In-memory):** Limpeza de tags HTML, conversão de tipos de dados e aplicação de regras de negócio (ex: filtragem de lutadores com menos de 8 lutas na organização).
3. **Load (NoSQL):** Inserção contínua (linha a linha) utilizando a técnica de *Upsert* no **MongoDB Atlas**, evitando duplicação de dados e permitindo a atualização recorrente do banco.
4. **Exportação Analítica:** Consumo da collection do MongoDB, utilizando o método `pd.json_normalize` do **Pandas** para achatar os documentos hierárquicos (BSON) em um formato bidimensional (CSV), ideal para análise.
5. **Data Visualization (Power BI):** Importação dos dados estruturados para criação de medidas DAX (KPIs de precisão, volume de golpes e defesas) e construção de uma interface em *Dark Mode* focada na experiência do usuário (UX), com filtros dinâmicos por categoria de peso e base de luta.

## 🗄️ Modelagem de Dados (MongoDB)
A escolha do MongoDB permite agrupar estatísticas relacionadas dentro do mesmo documento, facilitando a extração de inteligência sem a necessidade de múltiplos `JOINs`. Abaixo, um exemplo da estrutura atualizada:

```json
{
  "nome": "Alex Pereira",
  "url_perfil": "[http://ufcstats.com/fighter-details/](http://ufcstats.com/fighter-details/)...",
  "base_de_luta": "Orthodox",
  "altura_m": 1.93,
  "experiencia": {
    "lutas": 12,
    "vitorias_ufc": 10
  },
  "estatisticas_striking": {
    "socos_min": 5.16,
    "socos_precisao_pct": 62.00,
    "defesa_pct": 53.00
  }
}
```

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.8+
- Conta gratuita no [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (ou MongoDB rodando localmente)
- Power BI Desktop (Para abrir o Dashboard)

### Configuração do Ambiente

1. Clone o repositório:
```bash
git clone [https://github.com/andreandres/analise-ufc.git](https://github.com/andreandres/analise-ufc.git)
cd analise-ufc
```

2. Crie um ambiente virtual e instale as dependências:
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto (use o `.env.example` como base) e insira a sua string de conexão do MongoDB Atlas:
```text
MONGO_URI=mongodb+srv://<usuario>:<senha>@cluster0.mongodb.net/?retryWrites=true&w=majority
```

### Executando o Pipeline

**Passo 1: Popular o Banco de Dados (ETL)**
Rode o script de extração. Ele criará a conexão segura e fará o upsert dos lutadores de A a Z:
```bash
python scripts/extract_to_mongo.py
```

**Passo 2: Exportar para Análise**
Após os dados estarem no MongoDB, rode o script de exportação para gerar o arquivo CSV achatado:
```bash
python scripts/export_to_csv.py
```
O arquivo será salvo automaticamente na pasta `raw_data/`.

**Passo 3: Visualizar o Dashboard**
Com os dados extraídos, você pode explorar a interface gráfica:
1. Localize o arquivo `.pbix` na raiz do projeto.
2. Dê um duplo clique para abrir no **Power BI Desktop**.
3. Interaja com os filtros no canto superior direito para analisar o plantel do UFC!
