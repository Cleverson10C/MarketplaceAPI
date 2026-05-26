# Marketplace API

API REST para marketplace com:
- autenticação JWT;
- gestão de usuários;
- catálogo de produtos;
- controle de estoque com histórico de movimentações;
- criação de pedidos com baixa automática de estoque.

## Sumário

1. Visão geral
2. Stack e arquitetura
3. Estrutura de pastas
4. Requisitos
5. Configuração do ambiente
6. Como executar
7. Autenticação e autorização
8. Regras de negócio
9. Endpoints
10. Exemplos de uso (curl)
11. Testes
12. Observabilidade (logs)
13. Solução de problemas
14. Próximos passos recomendados

## Visão geral

Este projeto modela um fluxo real de operação de mercado:
- produto nasce com quantidade inicial em estoque;
- toda movimentação de estoque é registrada (`entrada`, `saida`, `ajuste`);
- pedido só é criado se houver estoque suficiente;
- ao concluir pedido, o estoque é baixado automaticamente.

## Stack e arquitetura

- `FastAPI` para API HTTP.
- `SQLAlchemy` para ORM e acesso a banco.
- `PostgreSQL` como banco principal.
- `python-jose` para JWT.
- `passlib` para hash de senha.
- `pytest` para testes.
- `alembic` para migrações de banco.

Arquitetura em camadas:
- `api/routes`: camada HTTP (validação de entrada, status code, resposta).
- `repositorios`: regras de persistência e parte da regra de negócio.
- `models`: entidades SQLAlchemy.
- `schemas`: contratos de entrada/saída (Pydantic).
- `core`: autenticação, token, configurações e dependências.
- `banco`: engine/sessão/base do SQLAlchemy.

## Estrutura de pastas

```text
app/
  api/routes/
    aut_rotas.py
    rotas_produto.py
    rotas_pedido.py
  banco/
    session.py
  core/
    config.py
    dependencias.py
    logging_config.py
    seguranca.py
    token.py
  models/
    usuario.py
    produto.py
    pedido.py
    item_pedido.py
    movimento_estoque.py
  repositorios/
    usuario_repository.py
    repositorio_produto.py
    pedido_repository.py
  schemas/
    usuario.py
    produto.py
    pedido.py
  main.py
tests/
  test_api.py
```

## Requisitos

- Python `3.11+`
- pip

## Configuração do ambiente

1. Criar e ativar ambiente virtual:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Instalar dependências:

```bash
pip install -r requirements.txt
```

3. Configurar variáveis de ambiente:

Copie `.env.example` para `.env` e ajuste conforme necessário.

Variáveis disponíveis:
- `SECRET_KEY`: chave JWT.
- `ALGORITHM`: algoritmo JWT (ex.: `HS256`).
- `ACCESS_TOKEN_EXPIRE_HOURS`: expiração do token em horas.
- `DATABASE_URL`: URL do banco (default: `postgresql+psycopg2://postgres:postgres@localhost:5432/marketplace_api`).
- `LOG_LEVEL`: nível de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`).

## Como executar

```bash
uvicorn app.main:app --reload
```

Acesse:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Autenticação e autorização

### Fluxo JWT

1. Criar conta em `POST /auth/registro`.
2. Fazer login em `POST /auth/login`.
3. Usar token Bearer no header:

```http
Authorization: Bearer <access_token>
```

### Perfis

- `usuario`: perfil padrão.
- `admin`: necessário para listagem/deleção administrativa de usuários.

## Regras de negócio

### Produtos

- Criação de produto exige:
  - `nome` não vazio;
  - `preco > 0`;
  - `quantidade >= 0`;
  - `estoque_minimo >= 0`.
- Quantidade inicial define o estoque inicial.
- Se `quantidade > 0`, é criado um movimento de estoque do tipo `entrada`.

### Estoque

- Tipos de movimento:
  - `entrada`: soma estoque.
  - `saida`: reduz estoque (exige saldo suficiente).
  - `ajuste`: define estoque para valor exato informado.
- Toda operação gera histórico em `movimentos_estoque`.

### Pedidos

- Só usuário autenticado cria pedido.
- Cada item precisa de `produto_id` válido e `quantidade > 0`.
- Se produto não existir: `404`.
- Se estoque for insuficiente: `409`.
- Em sucesso, o estoque é baixado automaticamente.

## Endpoints

### Saúde

- `GET /`

### Autenticação e usuários (`/auth`)

- `POST /auth/registro`
- `POST /auth/login`
- `GET /auth/me`
- `DELETE /auth/me`
- `GET /auth/usuarios` (admin)
- `DELETE /auth/usuarios/{usuario_id}` (admin)

### Produtos (`/products`)

- `POST /products/`
- `GET /products/`
- `GET /products/{produto_id}`
- `PUT /products/{produto_id}`
- `DELETE /products/{produto_id}`
- `POST /products/{produto_id}/estoque`
- `GET /products/{produto_id}/estoque/movimentos`
- `GET /products/estoque/alertas`
- `POST /products/{produto_id}/rastreamentos`
- `GET /products/{produto_id}/rastreamentos`

### Pedidos (`/pedidos`)

- `POST /pedidos/`

## Exemplos de uso (curl)

### 1. Registrar usuário

```bash
curl -X POST "http://127.0.0.1:8000/auth/registro" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"user@teste.com\",\"senha\":\"123456\"}"
```

### 2. Login

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"user@teste.com\",\"senha\":\"123456\"}"
```

Resposta esperada:

```json
{
  "access_token": "JWT_AQUI",
  "token_type": "bearer"
}
```

### 3. Criar produto com estoque inicial

```bash
curl -X POST "http://127.0.0.1:8000/products/" ^
  -H "Authorization: Bearer JWT_AQUI" ^
  -H "Content-Type: application/json" ^
  -d "{\"nome\":\"Arroz 5kg\",\"preco\":29.9,\"quantidade\":40,\"estoque_minimo\":10}"
```

### 4. Movimentar estoque

```bash
curl -X POST "http://127.0.0.1:8000/products/1/estoque" ^
  -H "Authorization: Bearer JWT_AQUI" ^
  -H "Content-Type: application/json" ^
  -d "{\"tipo\":\"saida\",\"quantidade\":3}"
```

### 5. Criar pedido

```bash
curl -X POST "http://127.0.0.1:8000/pedidos/" ^
  -H "Authorization: Bearer JWT_AQUI" ^
  -H "Content-Type: application/json" ^
  -d "{\"itens\":[{\"produto_id\":1,\"quantidade\":2},{\"produto_id\":2,\"quantidade\":1}]}"
```

## Testes

Executar:

```bash
pytest -q
```

Escolha de banco de testes:
- Padrão (isolado): usa `TEST_DATABASE_URL` (fallback `sqlite:///./test_suite.db`).
- Forçar uso do mesmo banco da API (`DATABASE_URL`): defina `TEST_USE_MAIN_DB=true`.

Exemplos (PowerShell):

```powershell
$env:TEST_USE_MAIN_DB="true"; pytest -q
```

```powershell
$env:TEST_DATABASE_URL="sqlite:///./test_suite.db"; pytest -q
```

Cobertura funcional atual dos testes:
- registro e login;
- proteção de rotas sem token;
- CRUD de produtos;
- validação de nome/preço de produto;
- criação de pedido com cálculo de total;
- pedido com produto inexistente;
- movimentação de estoque e baixa automática no pedido.
- alerta de produtos abaixo do estoque mínimo.

## Migrações com Alembic

Estrutura adicionada:
- `alembic.ini`
- `alembic/env.py`
- `alembic/versions/20260523_0001_initial_schema.py`

Comandos úteis:

```bash
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "descricao_da_migracao"
```

Observação:
- Em ambiente novo, prefira `alembic upgrade head` em vez de depender de `create_all`.

## Observabilidade (logs)

Logs implementados:
- middleware HTTP com método, rota, status e latência;
- logs de autenticação (registro/login/situações inválidas).

Configuração via `LOG_LEVEL` no `.env`.

## Solução de problemas

### Erro após alterar modelos

Mudanças de schema não devem ser aplicadas com `create_all` em ambientes reais.

Opções:
- aplicar migração com `alembic upgrade head`;
- criar nova revisão com `alembic revision --autogenerate -m "descricao_da_migracao"`.

### `401 Token inválido`

- Verifique se enviou `Authorization: Bearer <token>`.
- Confirme `SECRET_KEY` e `ALGORITHM` compatíveis com o token gerado.

### `409 Estoque insuficiente`

- Faça entrada/ajuste de estoque antes de criar pedido.

## Próximos passos recomendados

1. Refinar permissões para operações de estoque (ex.: restrito a admin/operador).
2. Evoluir testes para cenários de concorrência de estoque.

Projeto desenvolvido por:
Cleverson/10C 
