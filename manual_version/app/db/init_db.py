from app.db.session import SessionLocal
from app.models.user import User, Role
from app.models.tariff import Tariff
from app.models.invoice import Invoice, InvoiceStatus
from app.core.config import settings
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
    tariffs = [
        Tariff(name="Старт", monthly_fee=1990.00, description="20 Мбит/с, 50 ГБ в месяц", is_active=True),
        Tariff(name="Комфорт", monthly_fee=2990.00, description="50 Мбит/с, 100 ГБ в месяц", is_active=True),
        Tariff(name="Профи", monthly_fee=4990.00, description="100 Мбит/с, 250 ГБ в месяц", is_active=True),
        Tariff(name="Бизнес", monthly_fee=8990.00, description="300 Мбит/с, статический IP", is_active=True),
        Tariff(name="Архив", monthly_fee=1490.00, description="старый тариф, недоступен для подключения", is_active=False),
    ]
    db.add_all(tariffs)
    db.flush()

    admin = User(
        username="daniyar",
        email="daniyar@kazakhtelecom.kz",
        phone_number="+77051234567",
        password_hash=hash_password(settings.admin_initial_password),
        role=Role.ADMIN,
        is_active=True,
    )
    client = User(
        username="azamat",
        email="azamat@mail.kz",
        phone_number="+77059876543",
        password_hash=hash_password(settings.demo_client_password),
        role=Role.CLIENT,
        is_active=True,
        active_tariff_id=tariffs[0].id,
    )
    db.add_all([admin, client])
    db.flush()

    clients: list[User] = [client]
    password_hash = hash_password(settings.demo_client_password)
    for index in range(1, 101):
        tariff = tariffs[index % 4]
        clients.append(
            User(
                username=f"client{index:03d}",
                email=f"client{index:03d}@example.com",
                phone_number=f"+7705{index:07d}",
                password_hash=password_hash,
                role=Role.CLIENT,
                is_active=True,
                active_tariff_id=tariff.id,
            )
        )
    db.add_all(clients[1:])
    db.flush()

    invoices: list[Invoice] = []
    periods = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06"]
    statuses = [InvoiceStatus.PAID, InvoiceStatus.PENDING, InvoiceStatus.CANCELLED]
    for index, seeded_client in enumerate(clients):
        tariff = next(item for item in tariffs if item.id == seeded_client.active_tariff_id)
        for period in periods[:2]:
            invoices.append(
                Invoice(
                    user_id=seeded_client.id,
                    tariff_id=tariff.id,
                    billing_period=periods[(index + periods.index(period)) % len(periods)],
                    amount=float(tariff.monthly_fee),
                    currency="KZT",
                    status=statuses[index % len(statuses)],
                )
            )
    db.add_all(invoices)
    db.commit()
