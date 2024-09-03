-- Drop the existing tenant-specific unique constraints
ALTER TABLE users DROP CONSTRAINT IF EXISTS uq_username_tenant;
ALTER TABLE users DROP CONSTRAINT IF EXISTS uq_email_tenant;

-- Add new global unique constraints
ALTER TABLE users ADD CONSTRAINT uq_username UNIQUE (username);
ALTER TABLE users ADD CONSTRAINT uq_email UNIQUE (email);