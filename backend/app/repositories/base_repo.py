from typing import Generic, TypeVar

from app.extensions import db

T = TypeVar("T", bound=db.Model)


class BaseRepository(Generic[T]):
    model: type[T]

    def get(self, id: int) -> T | None:
        return db.session.get(self.model, id)

    def get_all(self) -> list[T]:
        return self.model.query.all()

    def filter_by(self, **kwargs) -> list[T]:
        return self.model.query.filter_by(**kwargs).all()

    def save(self, instance: T) -> T:
        db.session.add(instance)
        db.session.commit()
        return instance

    def delete(self, instance: T) -> None:
        db.session.delete(instance)
        db.session.commit()
