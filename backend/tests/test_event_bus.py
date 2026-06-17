"""Testes do padrão Observer (EventBus).

Usa instâncias novas de EventBus para isolamento — não mexe no singleton global.
"""
from app.services.events import EventBus


class FakeSubscriber:
    def __init__(self):
        self.recebidos = []

    def notify(self, event_name, payload):
        self.recebidos.append((event_name, payload))


def test_publish_notifica_todos_os_subscribers():
    bus = EventBus()
    s1, s2 = FakeSubscriber(), FakeSubscriber()
    bus.subscribe("produto_vencendo", s1)
    bus.subscribe("produto_vencendo", s2)

    bus.publish("produto_vencendo", {"dias": 3})

    assert s1.recebidos == [("produto_vencendo", {"dias": 3})]
    assert s2.recebidos == [("produto_vencendo", {"dias": 3})]


def test_subscriber_que_falha_nao_interrompe_os_outros():
    bus = EventBus()

    class Quebra:
        def notify(self, event_name, payload):
            raise RuntimeError("boom")

    bom = FakeSubscriber()
    bus.subscribe("evento", Quebra())
    bus.subscribe("evento", bom)

    bus.publish("evento", {})  # não deve propagar a exceção

    assert len(bom.recebidos) == 1


def test_evento_sem_subscriber_e_unsubscribe():
    bus = EventBus()
    s = FakeSubscriber()
    bus.subscribe("e", s)
    bus.unsubscribe("e", s)

    bus.publish("e", {})  # ninguém registrado — silencioso
    assert s.recebidos == []


def test_subscriber_so_recebe_seu_evento():
    bus = EventBus()
    s = FakeSubscriber()
    bus.subscribe("produto_vencendo", s)

    bus.publish("garantia_vencendo", {"x": 1})

    assert s.recebidos == []
