from app.db.session import SessionLocal
from app.models.user import User, Role
from app.models.tariff import Tariff
from app.models.invoice import Invoice, InvoiceStatus
from app.core.security import hash_password


def seed_db() -> None:
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return
        _seed(db)
    finally:
        db.close()


def _seed(db) -> None:
    tariff_basic = Tariff(
        name="Basic",
        monthly_fee=2990.00,
        description="100 min calls, 5 GB internet",
        is_active=True,
    )
    tariff_pro = Tariff(
        name="Pro",
        monthly_fee=5990.00,
        description="Unlimited calls, 30 GB internet",
        is_active=True,
    )
    db.add_all([tariff_basic, tariff_pro])
    db.flush()

    admin = User(
        username="admin",
        email="admin@telecom.kz",
        phone_number="+77001234567",
        password_hash=hash_password("Admin1234!"),
        role=Role.ADMIN,
        is_active=True,
    )
    client = User(
        username="john_doe",
        email="john@example.com",
        phone_number="+77009876543",
        password_hash=hash_password("Client1234!"),
        role=Role.CLIENT,
        is_active=True,
        active_tariff_id=tariff_basic.id,
    )
    db.add_all([admin, client])
    db.flush()

    invoice = Invoice(
        user_id=client.id,
        tariff_id=tariff_basic.id,
        billing_period="2025-03",
        amount=2990.00,
        currency="KZT",
        status=InvoiceStatus.PENDING,
    )
    db.add(invoice)
    db.commit()
