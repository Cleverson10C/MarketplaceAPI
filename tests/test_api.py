def criar_usuario_e_login(client, email="user@example.com", senha="123456"):
    registro = client.post("/auth/registro", json={"email": email, "senha": senha})
    assert registro.status_code == 200

    login = client.post("/auth/login", json={"email": email, "senha": senha})
    assert login.status_code == 200

    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_registro_e_login(client):
    response = client.post("/auth/registro", json={"email": "novo@example.com", "senha": "123456"})
    assert response.status_code == 200
    assert response.json()["mensagem"] == "Usuário criado com sucesso"

    login = client.post("/auth/login", json={"email": "novo@example.com", "senha": "123456"})
    assert login.status_code == 200
    body = login.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_rotas_protegidas_sem_token(client):
    response = client.post("/products/", json={"nome": "Teclado", "preco": 100, "quantidade": 10})
    assert response.status_code == 403


def test_crud_produtos(client):
    headers = criar_usuario_e_login(client)

    criado = client.post("/products/", json={"nome": "Mouse", "preco": 50, "quantidade": 5}, headers=headers)
    assert criado.status_code == 200
    produto = criado.json()
    assert produto["nome"] == "Mouse"
    assert produto["estoque"] == 5
    assert produto["estoque_minimo"] == 0
    produto_id = produto["id"]

    lista = client.get("/products/")
    assert lista.status_code == 200
    assert len(lista.json()) == 1

    atualizado = client.put(
        f"/products/{produto_id}",
        json={"nome": "Mouse Pro", "preco": 80},
        headers=headers,
    )
    assert atualizado.status_code == 200
    assert atualizado.json()["nome"] == "Mouse Pro"

    deletado = client.delete(f"/products/{produto_id}", headers=headers)
    assert deletado.status_code == 204


def test_validacao_produto_nome_e_preco(client):
    headers = criar_usuario_e_login(client, email="validacao@example.com")

    nome_vazio = client.post(
        "/products/",
        json={"nome": "", "preco": 10, "quantidade": 1},
        headers=headers,
    )
    assert nome_vazio.status_code == 422

    preco_zero = client.post(
        "/products/",
        json={"nome": "Produto X", "preco": 0, "quantidade": 1},
        headers=headers,
    )
    assert preco_zero.status_code == 422


def test_criar_pedido_calcula_total(client):
    headers = criar_usuario_e_login(client, email="pedido@example.com")

    p1 = client.post("/products/", json={"nome": "Item A", "preco": 10, "quantidade": 2}, headers=headers).json()
    p2 = client.post("/products/", json={"nome": "Item B", "preco": 25, "quantidade": 1}, headers=headers).json()

    pedido = client.post(
        "/pedidos/",
        json={
            "itens": [
                {"produto_id": p1["id"], "quantidade": 2},
                {"produto_id": p2["id"], "quantidade": 1},
            ]
        },
        headers=headers,
    )

    assert pedido.status_code == 200
    assert pedido.json()["total"] == 45


def test_pedido_com_produto_invalido(client):
    headers = criar_usuario_e_login(client, email="invalido@example.com")

    pedido = client.post(
        "/pedidos/",
        json={"itens": [{"produto_id": 9999, "quantidade": 1}]},
        headers=headers,
    )

    assert pedido.status_code == 404
    assert "não encontrado" in pedido.json()["detail"]


def test_movimentacoes_estoque_e_baixa_no_pedido(client):
    headers = criar_usuario_e_login(client, email="estoque@example.com")
    produto = client.post("/products/", json={"nome": "Arroz", "preco": 30, "quantidade": 0}, headers=headers).json()
    produto_id = produto["id"]

    entrada = client.post(
        f"/products/{produto_id}/estoque",
        json={"tipo": "entrada", "quantidade": 10},
        headers=headers,
    )
    assert entrada.status_code == 200
    assert entrada.json()["estoque_depois"] == 10

    saida = client.post(
        f"/products/{produto_id}/estoque",
        json={"tipo": "saida", "quantidade": 3},
        headers=headers,
    )
    assert saida.status_code == 200
    assert saida.json()["estoque_depois"] == 7

    ajuste = client.post(
        f"/products/{produto_id}/estoque",
        json={"tipo": "ajuste", "quantidade": 20},
        headers=headers,
    )
    assert ajuste.status_code == 200
    assert ajuste.json()["estoque_depois"] == 20

    pedido = client.post(
        "/pedidos/",
        json={"itens": [{"produto_id": produto_id, "quantidade": 5}]},
        headers=headers,
    )
    assert pedido.status_code == 200

    produto_atual = client.get(f"/products/{produto_id}")
    assert produto_atual.status_code == 200
    assert produto_atual.json()["estoque"] == 15

    sem_estoque = client.post(
        "/pedidos/",
        json={"itens": [{"produto_id": produto_id, "quantidade": 100}]},
        headers=headers,
    )
    assert sem_estoque.status_code == 409
    assert "Estoque insuficiente" in sem_estoque.json()["detail"]


def test_alerta_estoque_minimo(client):
    headers = criar_usuario_e_login(client, email="alerta@example.com")
    p1 = client.post(
        "/products/",
        json={"nome": "Feijao", "preco": 8, "quantidade": 2, "estoque_minimo": 5},
        headers=headers,
    )
    assert p1.status_code == 200

    p2 = client.post(
        "/products/",
        json={"nome": "Macarrao", "preco": 6, "quantidade": 10, "estoque_minimo": 3},
        headers=headers,
    )
    assert p2.status_code == 200

    alertas = client.get("/products/estoque/alertas", headers=headers)
    assert alertas.status_code == 200
    itens = alertas.json()
    assert len(itens) == 1
    assert itens[0]["nome"] == "Feijao"


def test_rastreamento_produto(client):
    headers = criar_usuario_e_login(client, email="rastreamento@example.com")
    produto = client.post(
        "/products/",
        json={"nome": "Notebook", "preco": 3500, "quantidade": 3},
        headers=headers,
    ).json()
    produto_id = produto["id"]

    registro_1 = client.post(
        f"/products/{produto_id}/rastreamentos",
        json={
            "status": "Em separacao",
            "localizacao": "Centro de distribuicao SP",
            "observacao": "Conferencia de qualidade iniciada",
        },
        headers=headers,
    )
    assert registro_1.status_code == 200
    assert registro_1.json()["status"] == "Em separacao"

    registro_2 = client.post(
        f"/products/{produto_id}/rastreamentos",
        json={
            "status": "Em transporte",
            "localizacao": "Rodovia BR-116",
        },
        headers=headers,
    )
    assert registro_2.status_code == 200

    lista = client.get(f"/products/{produto_id}/rastreamentos", headers=headers)
    assert lista.status_code == 200
    itens = lista.json()
    assert len(itens) == 2
    assert itens[0]["status"] == "Em transporte"
    assert itens[1]["status"] == "Em separacao"


def test_rastreamento_produto_inexistente(client):
    headers = criar_usuario_e_login(client, email="rastreamento404@example.com")
    response = client.post(
        "/products/9999/rastreamentos",
        json={
            "status": "Em separacao",
            "localizacao": "CD",
        },
        headers=headers,
    )
    assert response.status_code == 404


def test_pedido_gera_rastreamento_automatico(client):
    headers = criar_usuario_e_login(client, email="pedido-rastreio@example.com")
    produto = client.post(
        "/products/",
        json={"nome": "Cadeira", "preco": 199.9, "quantidade": 10},
        headers=headers,
    ).json()

    pedido = client.post(
        "/pedidos/",
        json={"itens": [{"produto_id": produto["id"], "quantidade": 2}]},
        headers=headers,
    )
    assert pedido.status_code == 200

    rastreamentos = client.get(f"/products/{produto['id']}/rastreamentos", headers=headers)
    assert rastreamentos.status_code == 200
    itens = rastreamentos.json()
    assert len(itens) >= 1
    assert itens[0]["status"] == "pedido_criado"
