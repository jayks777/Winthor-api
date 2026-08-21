# Investigação de lentidão na API

Relatório da análise de performance (TODO: "Investigar lentidão na API").

## Causas-raiz encontradas no código

### 1. `GET /product/random` – ordenação aleatória do catálogo inteiro
- **Antes:** `query.order_by(func.dbms_random.value()).first()`.
  O Oracle precisa ordenar (sort) **todo** o resultado do join (produtos × seção ×
  departamento × estoque) para então devolver a primeira linha.
- **Depois (corrigido):** contagem leve + `OFFSET` aleatório + `FETCH FIRST 1`.
  Vira duas consultas baratas em vez de um sort gigante.

### 2. Búsqueda em `/prestacoes` (não-sargável)
- **Antes:** `func.to_char(Prestacoes.DUPLIC).like('%...')` e
  `func.upper(Clientes.CLIENTE).like(...)`. Funções em colunas impedem o uso de
  índice → full scan no `PCPREST` (e no join com `PCCLIENT`).
- **Depois:** termo numérico → igualdade exata em `DUPLIC` (usar índice da PK);
  termo não-numérico → só busca parcial em nome do cliente.

### 3. Búsqueda `LIKE %term%` (wildcard inicial)
- `ilike("%...%")` em `PCCLIENT.CLIENTE`, `PCPRODUT.DESCRICAO` etc. não usam
  índices B-tree normais. Evitar para datasets grandes ou usar:
  - Oracle Text (`CONTAINS`) ou
  - buscador dedicado (cache/banco de busca) para o catálogo.

### 4. Falta de índices no banco (ação do DBA/ERP)
Os modelos representam tabelas do WinThor (gerenciadas pelo ERP). Recomendo
confirmar com o DBA a existência de índices para:
  - `PCPREST (DTVENC)` — range nos endpoints `/prestacoes`, `/vencidas`, `/a-vencer`
  - `PCPREST (DTBAIXA)` — filtro "em aberto"
  - `PCPREST (CODCLI)` — join com `PCCLIENT`
  - `PCPREST (CODFILIAL)`
  - `PCCLIENT (CLIENTE)` — busca por nome (ainda que `%x%` não use)
  - `PCSECAU (CODEPTO)` — categorias por departamento
  - `PCEST (CODPROD, CODFILIAL)` — já é a PK do ERP; usado no join do catálogo

### 5. `/catalog` recalcula `total` em toda chamada
`query.count()` é executado a cada requisição, mesmo filtrado. Para um catálogo
grande o custo é real. Possível melhoria (fora do escopo desta revisão):
  - cache do total por N minutos;
  - paginação por `keyset` (WHERE) em vez de `OFFSET` para páginas profundas.

### 6. Pool de conexões
- `create_engine(pool_size=20, max_overflow=40, pool_pre_ping=True)` tanto no
  Oracle (Winthor) quanto no MySQL (UOL).
- Com múltiplos `--workers`, cada worker abre seus próprios pools. Mantenha o
  serviço com 1 worker ou ajuste os tamanhos para o próprio budget da instância.
- `pool_pre_ping` adiciona um round-trip por checkout — aceito como troca.
- Verifique se a latência de rede até o banco não está com gateway/rede.

## Mudanças aplicadas nesta revisão
1. **limitação `limit`/`offset` removida** dos endpoints `/departments`,
   `/clients`, `/prestacoes`, `/user` e dos repositórios; retornam agora
   **todos** os registros, com teto de segurança server-side configurável
   (`API_MAX_RESULTS`, padrão 50000; `0` = sem limite).
2. **`/product/random`** otimizado (amostragem aleatória sem sort completo).
3. **Busca `/prestacoes`** por duplicata usa igualdade exata (PK).

## Como medir após o deploy
- `EXPLAIN PLAN` nas queries do catálogo e de prestações para confirmar índice.
- `curl` (ou Postman) com medição de tempo antes/depois nas rotas listadas.
- `pue es_monitoring` dos conexões (2 pools × pool_size) e da latência DB.

## Próximos passos (fora do código)
- Criar/confirmar índices acima no banco de produção (com o DBA).
- Avaliar cache HTTP/CDN para `/catalog` (imutável por períodos).