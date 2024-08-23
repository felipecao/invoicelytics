-- 
-- depends: 0004_drop_unique_invoice_number

ALTER TABLE invoices
RENAME COLUMN issued_date TO issue_date;


