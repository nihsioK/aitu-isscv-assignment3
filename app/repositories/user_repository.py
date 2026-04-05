from sqlalchemy.orm import Session
from app.models.user import User, Role


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create(
    db: Session,
    username: str,
    email: str,
    phone_number: str,
    password_hash: str,
    role: Role = Role.CLIENT,
) -> User:
    user = User(
        username=username,
        email=email,
        phone_number=phone_number,
        password_hash=password_hash,
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_active_tariff(db: Session, user: User, tariff_id: int) -> User:
    user.active_tariff_id = tariff_id
    db.commit()
    db.refresh(user)
    return user
