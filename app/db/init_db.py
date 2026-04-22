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
    tariff_start = Tariff(
        name="Старт",
        monthly_fee=1990.00,
        description="20 Мбит/с, 50 ГБ в месяц",
        is_active=True,
    )
    tariff_comfort = Tariff(
        name="Комфорт",
        monthly_fee=2990.00,
        description="50 Мбит/с, 100 ГБ в месяц",
        is_active=True,
    )
    db.add_all([tariff_start, tariff_comfort])
    db.flush()

    # Раньше здесь пароль был забит прямо в коде ("Password1!"). 
    # Это плохая практика, поэтому вынес в переменные окружения.
    # Если переменная не задана, используем заглушку для локальной разработки.
    import os
    admin_pass = os.getenv("ADMIN_INITIAL_PASSWORD", "ComplexPass123!")
    admin = User(
        username="daniyar",
        email="daniyar@kazakhtelecom.kz",
        phone_number="+77051234567",
        password_hash=hash_password(admin_pass),
        role=Role.ADMIN,
        is_active=True,
    )
    client = User(
        username="azamat",
        email="azamat@mail.kz",
        phone_number="+77059876543",
        password_hash=hash_password("Password1!"),
        role=Role.CLIENT,
        is_active=True,
        active_tariff_id=tariff_start.id,
    )
    db.add_all([admin, client])
    db.flush()

    invoice = Invoice(
        user_id=client.id,
        tariff_id=tariff_start.id,
        billing_period="2025-03",
        amount=1990.00,
        currency="KZT",
        status=InvoiceStatus.PENDING,
    )
    db.add(invoice)
    db.commit()
