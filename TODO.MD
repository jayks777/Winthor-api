# a fazer

- [x] Remover Limit dos endpoints de forma segura para produção (URGENTE)
  - `limit`/`offset` removidos dos endpoints de listagem (`/departments`,
    `/clients`, `/prestacoes`, `/user`) e dos repositórios.
  - Agora retornam **todos** os registros; teto de segurança server-side via
    `API_MAX_RESULTS` (padrão 50000; 0 = sem limite) no `.env`.
- [x] Investigar lentidão na API
  - Relatório detalhado em `PERFORMANCE.md`.
  - Corrigido: `/product/random` (order by dbms_random.value) e busca de
    duplicata em `/prestacoes` (to_char que impedia índice).
  - Pendência: índices no banco (ver `PERFORMANCE.md`).
- [ ] Criar/confirmar índices no banco: PCPREST(DTVENC), PCPREST(DTBAIXA),
      PCPREST(CODCLI), PCPREST(CODFILIAL), PCCLIENT(CLIENTE). 