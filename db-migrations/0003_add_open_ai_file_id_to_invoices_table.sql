-- 
-- depends: 0001_create_initial_tables  0002_populate_tenants_table

ALTER TABLE invoices
ADD COLUMN open_ai_file_id CHARACTER VARYING NULL;


