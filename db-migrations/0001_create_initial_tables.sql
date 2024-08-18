-- Create the tenants table
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    tenant_name CHARACTER VARYING NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create the users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username CHARACTER VARYING NOT NULL,
    email CHARACTER VARYING NOT NULL,
    password_hash CHARACTER VARYING NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    CONSTRAINT unique_username_per_tenant UNIQUE (tenant_id, username),
    CONSTRAINT unique_email_per_tenant UNIQUE (tenant_id, email)
);

-- Create the invoices table
CREATE TABLE invoices (
    id UUID PRIMARY KEY,
    payee_name CHARACTER VARYING,
    payee_address CHARACTER VARYING,
    invoice_number CHARACTER VARYING UNIQUE,
    issued_date DATE,
    total_amount NUMERIC,
    tax_amount NUMERIC,
    due_date DATE,
    status CHARACTER VARYING,
    pdf_file_path CHARACTER VARYING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
    validated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE
);
