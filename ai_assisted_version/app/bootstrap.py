from sqlalchemy.orm import Session

from app.database import Base, engine
from app.models import Customer, Invoice, InvoiceStatus, Plan, Role
from app.security import hash_password
from app.config import settings


def create_schema() -> None:
    Base.metadata.create_all(bind=engine)


def seed_data(db: Session) -> None:
    if db.query(Customer).count() > 0:
        return

    plans = [
        Plan(title="AI Start", monthly_price=2100, traffic_limit_gb=60, description="25 Mbit/s for basic usage"),
        Plan(title="AI Family", monthly_price=3400, traffic_limit_gb=140, description="60 Mbit/s for home clients"),
        Plan(title="AI Pro", monthly_price=5200, traffic_limit_gb=300, description="120 Mbit/s and priority support"),
        Plan(title="AI Office", monthly_price=9100, traffic_limit_gb=700, description="350 Mbit/s and static IP"),
        Plan(title="AI Archive", monthly_price=1500, traffic_limit_gb=40, description="Legacy plan", is_public=False),
    ]
    db.add_all(plans)
    db.flush()

    admin = Customer(
        username="ai_admin",
        email="ai_admin@telecom.kz",
        phone="+77051112233",
        password_hash=hash_password(settings.admin_password),
        role=Role.ADMIN,
        active_plan_id=None,
    )
    demo = Customer(
        username="ai_client",
        email="ai_client@example.com",
        phone="+77054445566",
        password_hash=hash_password(settings.demo_password),
        role=Role.CLIENT,
        active_plan_id=plans[0].id,
    )
    db.add_all([admin, demo])
    db.flush()

    clients = [demo]
    client_hash = hash_password(settings.demo_password)
    for number in range(1, 101):
        plan = plans[number % 4]
        clients.append(
            Customer(
                username=f"ai_user_{number:03d}",
                email=f"ai_user_{number:03d}@example.com",
                phone=f"+7706{number:07d}",
                password_hash=client_hash,
                role=Role.CLIENT,
                active_plan_id=plan.id,
            )
        )
    db.add_all(clients[1:])
    db.flush()

    statuses = [InvoiceStatus.PAID, InvoiceStatus.PENDING, InvoiceStatus.CANCELLED]
    invoices: list[Invoice] = []
    for index, customer in enumerate(clients):
        plan = next(item for item in plans if item.id == customer.active_plan_id)
        for month_offset in range(2):
            invoices.append(
                Invoice(
                    customer_id=customer.id,
                    plan_id=plan.id,
                    billing_month=f"2026-{(index + month_offset) % 12 + 1:02d}",
                    amount=float(plan.monthly_price),
                    currency="KZT",
                    status=statuses[index % len(statuses)],
                )
            )
    db.add_all(invoices)
    db.commit()
