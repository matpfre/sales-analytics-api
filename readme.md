# Sales Analytics API

API de análise de vendas desenvolvida com FastAPI, SQLAlchemy e Pandas.

## Funcionalidades
- Cadastro de vendas
- Listagem de vendas
- Análise de dados:
  - Faturamento total
  - Ticket médio
  - Produto mais vendido
  - Vendas por dia

## Tecnologias
- Python
- FastAPI
- SQLAlchemy
- Pandas
- SQLite

##  Endpoints

- POST /sales
- GET /sales
- GET /analytics

##  Como rodar

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload

