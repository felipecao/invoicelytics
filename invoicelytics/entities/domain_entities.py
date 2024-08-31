import datetime as dt
from zoneinfo import ZoneInfo

from sqlalchemy import Column, String, Date, Float, Enum, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class InvoiceStatus(Enum):
    CREATED = "created"
    PROCESSED = "processed"
    APPROVED = "approved"
    REJECTED = "rejected"


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, index=True)
    tenant_name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.now(ZoneInfo("UTC")))
    updated_at = Column(DateTime, nullable=False, default=dt.datetime.now(ZoneInfo("UTC")))
    open_ai_vector_store_id = Column(String, nullable=True)


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
    issue_date = Column(Date, nullable=True)
    total_amount = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(Enum("created", "processed", "approved", "rejected", name="invoice_status_enum"), nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), nullable=True)
    validated_by = Column(UUID(as_uuid=True), nullable=True)
    pdf_file_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.now(ZoneInfo("UTC")), nullable=True)
    updated_at = Column(DateTime, default=dt.datetime.now(ZoneInfo("UTC")), nullable=True)
    open_ai_pdf_file_id = Column(String, nullable=True)
    open_ai_json_file_id = Column(String, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "payee_name": self.payee_name,
            "payee_address": self.payee_address,
            "invoice_number": self.invoice_number,
            "issue_date": self.issue_date.isoformat() if self.issue_date else None,
            "total_amount": self.total_amount,
            "tax_amount": self.tax_amount,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status,
            "uploaded_by": str(self.uploaded_by) if self.uploaded_by else None,
            "validated_by": str(self.validated_by) if self.validated_by else None,
            "pdf_file_path": self.pdf_file_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
