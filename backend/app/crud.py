import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Circuit,
    CircuitCreate,
    CircuitUpdate,
    Item,
    ItemCreate,
    User,
    UserCreate,
    UserUpdate,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def get_circuit(*, session: Session, id: int) -> Circuit | None:
    statement = select(Circuit).where(Circuit.id == id)
    circuit = session.exec(statement).first()
    return circuit


def get_multi_circuits(
    *, session: Session, skip: int = 0, limit: int = 100
) -> list[Circuit]:
    statement = select(Circuit).offset(skip).limit(limit)
    circuits = session.exec(statement).all()
    return list(circuits)


def create_circuit(*, session: Session, circuit_in: CircuitCreate) -> Circuit:
    db_circuit = Circuit.model_validate(circuit_in)
    session.add(db_circuit)
    session.commit()
    session.refresh(db_circuit)
    return db_circuit


def update_circuit(
    *, session: Session, db_circuit: Circuit, circuit_in: CircuitUpdate
) -> Circuit:
    circuit_data = circuit_in.model_dump(exclude_unset=True)
    db_circuit.sqlmodel_update(circuit_data)
    session.add(db_circuit)
    session.commit()
    session.refresh(db_circuit)
    return db_circuit


def remove_circuit(*, session: Session, id: int) -> Circuit | None:
    db_circuit = get_circuit(session=session, id=id)
    if db_circuit:
        session.delete(db_circuit)
        session.commit()
    return db_circuit
