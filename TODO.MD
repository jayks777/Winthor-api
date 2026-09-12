# a fazer

## [x] Rotas e dependências para sustentar um portal do cliente

- Deve fazer a autenticação de um cliente pelo numdoc + senha cadastrado no nbanco da uol
- Nesse portal, o cliente deverá observar faturas vencidas, pagas e a vencer APENAS DELE MESMO
- Ele também poderá observar os pedidos que ele fez, preferencialmente com nome e imagem dos itens comprados
- Também pode conseguir observar os dados de seu vendedor responsável
- Deve ser seguro
  - Login protegido contra tentativas repetidas e token de cliente separado.
  - Todas as consultas do portal usam o `CODCLI` do token, nunca um código
    informado pela requisição.

## [ ] (menos urgente) Rotas para cadastro de funcionários, vendedores e clientes

obs: não temos permissão de edição nos bancos do WinThor, apenas visualização
