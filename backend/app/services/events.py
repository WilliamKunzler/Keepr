from collections import defaultdict
from typing import Any, Callable, Protocol


class Subscriber(Protocol):
    """Contrato que todo subscriber deve cumprir."""

    def notify(self, event_name: str, payload: dict[str, Any]) -> None:
        ...


class EventBus:
    """Bus central de eventos."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Subscriber]] = defaultdict(list)

    def subscribe(self, event_name: str, subscriber: Subscriber) -> None:
        self._subscribers[event_name].append(subscriber)

    def unsubscribe(self, event_name: str, subscriber: Subscriber) -> None:
        if subscriber in self._subscribers[event_name]:
            self._subscribers[event_name].remove(subscriber)

    def publish(self, event_name: str, payload: dict[str, Any]) -> None:
        for subscriber in self._subscribers[event_name]:
            try:
                subscriber.notify(event_name, payload)
            except Exception as exc:  # noqa: BLE001
                # Um subscriber falhar não pode parar os outros.
                print(f"[EventBus] subscriber falhou em {event_name}: {exc}")

    def clear(self) -> None:
        self._subscribers.clear()


# Instância singleton — usada pela aplicação inteira
event_bus = EventBus()
