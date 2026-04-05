import enum
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Enum, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Role(str, enum.Enum):
    CLIENT = "CLIENT"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.CLIENT, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # which tariff is currently active for this user (nullable = not subscribed)
    active_tariff_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("tariffs.id"), nullable=True
    )

    invoices: Mapped[list["Invoice"]] = relationship("Invoice", back_populates="user")
    active_tariff: Mapped["Tariff | None"] = relationship("Tariff")
