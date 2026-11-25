from typing import TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


def save(session: Session, instance: T) -> T:
    session.add(instance)
    session.commit()
    session.refresh(instance)
    return instance


def save_all(session: Session, instances: list[T]) -> None:
    if instances:
        session.add_all(instances)
        session.commit()


def delete(session: Session, instance: object) -> None:
    session.delete(instance)
    session.commit()
