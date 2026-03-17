# 🥊 UFC Data Analytics Pipeline

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)

## 📌 Sobre o Projeto
Este projeto é um pipeline completo de Extração, Transformação e Carga (ETL) focado em dados de artes marciais mistas (MMA). O objetivo é construir uma base de dados analítica robusta a partir do histórico de milhares de lutadores do UFC, unindo conhecimento de domínio no esporte com práticas modernas de Engenharia de Dados.

O sistema coleta estatísticas detalhadas (Striking, Grappling, Cartel), estrutura esses dados em documentos NoSQL para suportar aninhamento complexo, e permite a exportação achatada (flattening) para análises em ferramentas de Data Science ou Business Intelligence.

## 🏗️ Arquitetura e Fluxo de Dados

O pipeline foi desenhado separando a ingestão (scraping seguro) da camada de consumo (análise), garantindo resiliência contra falhas de rede e bloqueios.

1. **Extract (Web Scraping):** Varredura do site UFCStats utilizando `requests` e `BeautifulSoup`. Implementação de Sessões Robustas (com User-Agent customizado e `urllib3 Retry`) para contornar timeouts e bloqueios (*Rate Limiting*).
2. **Transform (In-memory):** Limpeza de tags HTML, conversão de tipos de dados e aplicação de regras de negócio (ex: filtragem de lutadores com menos de 8 lutas na organização).
3. **Load (NoSQL):** Inserção contínua (linha a linha) utilizando a técnica de *Upsert* no **MongoDB Atlas**, evitando duplicação de dados e permitindo a atualização recorrente do banco.
4. **Exportação Analítica:** Consumo da collection do MongoDB, utilizando o método `pd.json_normalize` do **Pandas** para achatar os documentos hierárquicos (BSON) em um formato bidimensional (CSV), ideal para análise.

## 🗄️ Modelagem de Dados (MongoDB)
A escolha do MongoDB permite agrupar estatísticas relacionadas dentro do mesmo documento, facilitando a extração de inteligência sem a necessidade de múltiplos `JOINs`.

```json
{
  "nome": "Alex Pereira",
  "url_perfil": "[http://ufcstats.com/fighter-details/](http://ufcstats.com/fighter-details/)...",
  "cartel_geral": "10-2-0",
  "experiencia_ufc": {
    "lutas": 8,
    "vitorias": 7,
    "derrotas": 1
  },
  "estatisticas": {
    "slpm": 5.0,
    "td_avg": 0.0,
    "sub_avg": 0.0
  }
}
```

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.8+
- Conta gratuita no [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (ou MongoDB rodando localmente)

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
