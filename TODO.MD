## Pedidos ao backend

### 1. Busca textual em `/prestacoes/`

**Motivação:** atualmente o endpoint `GET /prestacoes/` não aceita parâmetro de busca textual. O frontend filtra apenas os registros da página atual (client-side), então o usuário não encontra prestações que estejam em outras páginas.

**Alteração solicitada:** adicionar parâmetro `search` opcional ao endpoint existente:

```
GET /prestacoes/?search=NOME_OU_DUPLICATA&dias_passados=30&dias_futuros=30&limit=50&offset=0
```

| Parâmetro | Tipo   | Obrigatório | Descrição |
|-----------|--------|-------------|-----------|
| `search`  | string | Não         | Busca por nome do cliente (`CLIENTE`) ou número da duplicata (`DUPLIC`). A busca deve ser case-insensitive e aceitar correspondência parcial (LIKE `%termo%`). |

**Comportamento esperado:** retorna o mesmo schema `PrestacaoResponse[]` atual, porém filtrando no banco de dados antes de paginar. O parâmetro deve ser combinável com `codcli`, `codfilial`, `dias_passados` e `dias_futuros`.

---

### 2. Endpoint agregado de previsão de recebimentos por dia

**Motivação:** o gráfico de barras "Previsão de Recebimentos" precisa do total a receber agrupado por data de vencimento. Hoje o frontend pagina todas as páginas de `/prestacoes/a-vencer` e soma os valores no JavaScript — ineficiente para períodos longos ou com muitas prestações.

**Novo endpoint sugerido:**

```
GET /prestacoes/a-vencer/por-dia?dias=30&codfilial=1
```

| Parâmetro   | Tipo    | Padrão | Descrição                             |
|-------------|---------|--------|---------------------------------------|
| `dias`      | integer | 30     | Número de dias futuros (máx. 365)     |
| `codfilial` | integer | null   | Filtrar por filial (opcional)         |

**Schema de resposta sugerido:**

```json
[
  { "DTVENC": "2026-08-19", "total": 4850.00, "quantidade": 3 },
  { "DTVENC": "2026-08-20", "total": 12300.50, "quantidade": 7 },
  { "DTVENC": "2026-08-21", "total": 0.00, "quantidade": 0 }
]
```

Retorna um item para **cada dia** do intervalo (inclusive dias sem vencimentos, com `total: 0`), já ordenado por `DTVENC` ASC. Equivale a `SELECT DTVENC, SUM(VALOR), COUNT(*) FROM ... GROUP BY DTVENC` no banco, muito mais eficiente do que paginar registros individuais.
