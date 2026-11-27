from typing import TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


def save(session: Session, instance: T) -> T:
    session.add(instance)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
    session.refresh(instance)
    return instance


def save_all(session: Session, instances: list[T]) -> None:
    if not instances:
        return
    session.add_all(instances)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise


def delete(session: Session, instance: object) -> None:
    session.delete(instance)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
