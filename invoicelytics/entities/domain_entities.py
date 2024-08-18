import datetime as dt
from zoneinfo import ZoneInfo

from sqlalchemy import Column, String, Date, Float, Enum, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class InvoiceStatus(Enum):
    CREATED = "created"
    PROCESSED = "processed"
    VALIDATED = "validated"


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, index=True)
    tenant_name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.now(ZoneInfo("UTC")))
    updated_at = Column(DateTime, nullable=False, default=dt.datetime.now(ZoneInfo("UTC")))


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("tenant_id", "username", name="uq_username_tenant"),
        UniqueConstraint("tenant_id", "email", name="uq_email_tenant"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.now(ZoneInfo("UTC")))
    updated_at = Column(DateTime, nullable=False, default=dt.datetime.now(ZoneInfo("UTC")))
    last_login_at = Column(DateTime, nullable=True)


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    payee_name = Column(String, nullable=True)
    payee_address = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True, unique=True)
    issued_date = Column(Date, nullable=True)
    total_amount = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(Enum("created", "processed", "validated", name="invoice_status_enum"), nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), nullable=True)
    validated_by = Column(UUID(as_uuid=True), nullable=True)
    pdf_file_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.now(ZoneInfo("UTC")), nullable=True)
    updated_at = Column(DateTime, default=dt.datetime.now(ZoneInfo("UTC")), nullable=True)
