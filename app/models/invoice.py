import enum
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Enum, Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.tariff import Tariff
from app.models.user import User


class InvoiceStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    tariff_id: Mapped[int] = mapped_column(Integer, ForeignKey("tariffs.id"), nullable=False)
    billing_period: Mapped[str] = mapped_column(String(7), nullable=False)  # "YYYY-MM"
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="KZT", nullable=False)
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus), default=InvoiceStatus.PENDING, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="invoices")
    tariff: Mapped["Tariff"] = relationship("Tariff")
