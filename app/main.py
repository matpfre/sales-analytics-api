from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from . import analytics, crud, schemas
from .database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sales Analytics API",
    version="1.1.0",
    description="API para cadastro e análise de vendas.",
)


@app.get("/", include_in_schema=False)
def dashboard_root():
    return HTMLResponse("""
    <!doctype html>
    <html lang="pt-BR">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Sales Dashboard</title>
      <style>
        * { box-sizing: border-box; }
        body {
          margin: 0;
          font-family: Arial, sans-serif;
          background: #f5f7fb;
          color: #1f2937;
        }
        .container {
          max-width: 1100px;
          margin: 40px auto;
          padding: 24px;
        }
        .topbar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 24px;
        }
        h1 { margin: 0; }
        .cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }
        .card {
          background: white;
          border-radius: 12px;
          padding: 18px;
          box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
        }
        .card-label {
          color: #64748b;
          font-size: 12px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.08em;
        }
        .card-value {
          margin-top: 8px;
          font-size: 28px;
          font-weight: 700;
        }
        .panel {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
          margin-bottom: 24px;
        }
        form {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
          gap: 16px;
          align-items: end;
        }
        label {
          display: flex;
          flex-direction: column;
          font-size: 13px;
          color: #334155;
          gap: 8px;
        }
        input, button {
          padding: 10px 12px;
          border-radius: 8px;
          border: 1px solid #cbd5e1;
          font-size: 14px;
        }
        button {
          background: #2563eb;
          color: white;
          border: none;
          cursor: pointer;
          font-weight: 700;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 12px;
        }
        th, td {
          text-align: left;
          padding: 12px 10px;
          border-bottom: 1px solid #e2e8f0;
        }
        th {
          color: #475569;
          font-size: 12px;
          text-transform: uppercase;
        }
        .muted {
          color: #64748b;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="topbar">
          <h1>Dashboard de Vendas</h1>
          <button onclick="loadData()">Atualizar</button>
        </div>

        <section class="cards" id="cards"></section>

        <section class="panel">
          <h3>Nova venda</h3>
          <form id="sale-form">
            <label>
              Produto
              <input type="text" name="product" placeholder="Notebook" required />
            </label>
            <label>
              Valor
              <input type="number" name="value" min="0.01" step="0.01" placeholder="2500" required />
            </label>
            <label>
              Data
              <input type="date" name="date" required />
            </label>
            <button type="submit">Salvar venda</button>
          </form>
        </section>

        <section class="panel">
          <h3>Vendas recentes</h3>
          <div id="sales-table" class="muted">Carregando...</div>
        </section>
      </div>

      <script>
        async function fetchJson(url, options = {}) {
          const response = await fetch(url, options);
          if (!response.ok) {
            throw new Error('Erro ao consultar a API');
          }
          return response.json();
        }

        function renderCards(data) {
          const cards = document.getElementById('cards');
          const items = [
            { label: 'Faturamento total', value: formatCurrency(data.total_revenue || 0) },
            { label: 'Ticket médio', value: formatCurrency(data.average_ticket || 0) },
            { label: 'Total de vendas', value: data.total_sales || 0 },
            { label: 'Produto líder', value: data.top_product || 'Nenhum' },
          ];

          cards.innerHTML = items.map(item => `
            <div class="card">
              <div class="card-label">${item.label}</div>
              <div class="card-value">${item.value}</div>
            </div>
          `).join('');
        }

        function renderSalesTable(sales) {
          const container = document.getElementById('sales-table');

          if (!sales.length) {
            container.textContent = 'Nenhuma venda cadastrada.';
            return;
          }

          const rows = sales.map(sale => `
            <tr>
              <td>${sale.product}</td>
              <td>${formatCurrency(sale.value)}</td>
              <td>${sale.date}</td>
              <td>
                <button onclick="deleteSale(${sale.id})">Excluir</button>
              </td>
            </tr>
          `).join('');

          container.innerHTML = `
            <table>
              <thead>
                <tr>
                  <th>Produto</th>
                  <th>Valor</th>
                  <th>Data</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>${rows}</tbody>
            </table>
          `;
        }

        async function loadData() {
          try {
            const [sales, analytics] = await Promise.all([
              fetchJson('/sales?limit=20'),
              fetchJson('/analytics')
            ]);
            renderCards(analytics);
            renderSalesTable(sales);
          } catch (error) {
            document.getElementById('sales-table').textContent = 'Não foi possível carregar os dados.';
            console.error(error);
          }
        }

        async function deleteSale(id) {
          try {
            await fetchJson(`/sales/${id}`, { method: 'DELETE' });
            await loadData();
          } catch (error) {
            alert('Erro ao excluir venda');
            console.error(error);
          }
        }

        document.getElementById('sale-form').addEventListener('submit', async function (event) {
          event.preventDefault();
          const formData = new FormData(event.target);
          const payload = {
            product: formData.get('product').toString().trim(),
            value: Number(formData.get('value')),
            date: formData.get('date')
          };

          try {
            await fetchJson('/sales', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(payload)
            });
            event.target.reset();
            await loadData();
          } catch (error) {
            alert('Não foi possível criar a venda.');
            console.error(error);
          }
        });

        function formatCurrency(value) {
          return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
          }).format(value);
        }

        loadData();
      </script>
    </body>
    </html>
    """)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/sales", response_model=schemas.SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_sale(db, sale)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error creating sale: {exc}") from exc


@app.get("/sales", response_model=list[schemas.SaleResponse])
def list_sales(
    db: Session = Depends(get_db),
    product: str | None = Query(default=None, description="Filter by product name"),
    start_date: date | None = Query(default=None, description="Start date for filtering"),
    end_date: date | None = Query(default=None, description="End date for filtering"),
    skip: int = Query(default=0, ge=0, description="Number of rows to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of rows to return"),
):
    return crud.get_sales(
        db,
        product=product,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )


@app.put("/sales/{sale_id}", response_model=schemas.SaleResponse)
def update_sale(
    sale_id: int,
    sale: schemas.SaleCreate,
    db: Session = Depends(get_db),
):
    updated_sale = crud.update_sale(db, sale_id, sale)
    if updated_sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return updated_sale


@app.delete("/sales/{sale_id}")
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_sale(db, sale_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sale not found")
    return {"message": "Sale deleted successfully"}


@app.get("/analytics", response_model=schemas.AnalyticsResponse)
def analytics_data(db: Session = Depends(get_db)):
    return analytics.get_sales_summary(db)