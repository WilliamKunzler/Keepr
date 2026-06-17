from app.services.events import event_bus


def verificar_garantia() -> None:
    from app.models.produto import ProdutoGarantia

    produtos = ProdutoGarantia.query.all()
    encontrados = 0

    for produto in produtos:
        if produto.esta_em_risco(dias_antecedencia=30):
            dias = produto.garantia.dias_restantes() if produto.garantia else None
            event_bus.publish(
                "garantia_vencendo",
                {"produto": produto, "dias": dias},
            )
            encontrados += 1

    print(f"[Job verificar_garantia] {encontrados} produto(s) em risco")
