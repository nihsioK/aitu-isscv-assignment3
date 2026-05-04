import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes.billing import require_internal_api_key
from app.core.config import settings
from app.db.base import Base
from app.main import app
from app.models.invoice import Invoice
from app.models.tariff import Tariff
from app.models.user import Role, User
from app.schemas.invoice import GenerateInvoiceRequest
from app.services import billing_service


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        tariff = Tariff(
            name="Start",
            monthly_fee=1990.00,
            description="Test tariff",
            is_active=True,
        )
        db.add(tariff)
        db.flush()

        client = User(
            username="client",
            email="client@example.com",
            phone_number="+77050000001",
            password_hash="hash",
            role=Role.CLIENT,
            is_active=True,
            active_tariff_id=tariff.id,
        )
        other_client = User(
            username="other",
            email="other@example.com",
            phone_number="+77050000002",
            password_hash="hash",
            role=Role.CLIENT,
            is_active=True,
            active_tariff_id=tariff.id,
        )
        db.add_all([client, other_client])
        db.commit()
        db.refresh(client)
        db.refresh(other_client)
        db.refresh(tariff)

        yield db, client, other_client, tariff
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_request_size_middleware_rejects_oversized_body(monkeypatch):
    monkeypatch.setattr(settings, "max_request_size_bytes", 10)
    client = TestClient(app)

    response = client.post(
        "/auth/register",
        content=b"x" * 50,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 413
    assert response.json() == {"detail": "Request body too large"}


def test_generate_invoice_request_rejects_client_controlled_fields():
    with pytest.raises(ValidationError):
        GenerateInvoiceRequest(
            user_id=1,
            tariff_id=1,
            billing_period="2026-04",
            amount=1,
            currency="USD",
        )


def test_generate_invoice_calculates_amount_from_active_tariff(db_session):
    db, client, _other_client, tariff = db_session

    invoice = billing_service.generate_invoice(
        db,
        GenerateInvoiceRequest(user_id=client.id, billing_period="2026-04"),
    )

    assert invoice.user_id == client.id
    assert invoice.tariff_id == tariff.id
    assert float(invoice.amount) == 1990.00
    assert invoice.currency == "KZT"


def test_generate_invoice_rejects_duplicate_period(db_session):
    db, client, _other_client, _tariff = db_session
    request = GenerateInvoiceRequest(user_id=client.id, billing_period="2026-04")

    billing_service.generate_invoice(db, request)

    with pytest.raises(HTTPException) as exc_info:
        billing_service.generate_invoice(db, request)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Invoice already exists for this period"


def test_internal_billing_api_requires_shared_key(monkeypatch):
    monkeypatch.setattr(settings, "internal_api_key", "secret-key")

    with pytest.raises(HTTPException) as exc_info:
        require_internal_api_key()

    assert exc_info.value.status_code == 403
    assert require_internal_api_key("secret-key") is None


def test_client_cannot_distinguish_foreign_invoice_from_missing_invoice(db_session):
    db, client, other_client, tariff = db_session
    foreign_invoice = Invoice(
        user_id=other_client.id,
        tariff_id=tariff.id,
        billing_period="2026-04",
        amount=1990.00,
        currency="KZT",
    )
    db.add(foreign_invoice)
    db.commit()
    db.refresh(foreign_invoice)

    with pytest.raises(HTTPException) as exc_info:
        billing_service.get_invoice(db, foreign_invoice.id, client.id, is_admin=False)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Invoice not found"
    assert billing_service.get_invoice(db, foreign_invoice.id, client.id, is_admin=True).id == foreign_invoice.id
