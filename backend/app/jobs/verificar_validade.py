from app.services.events import event_bus


def verificar_validade() -> None:
    from app.models.produto import ProdutoValidade

    produtos = ProdutoValidade.query.all()
    encontrados = 0

    for produto in produtos:
        if produto.esta_em_risco(dias_antecedencia=7):
            event_bus.publish(
                "produto_vencendo",
                {"produto": produto, "dias": produto.dias_para_vencer()},
            )
            encontrados += 1

    print(f"[Job verificar_validade] {encontrados} produto(s) em risco")
