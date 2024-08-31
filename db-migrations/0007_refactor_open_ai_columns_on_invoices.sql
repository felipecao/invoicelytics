-- 
-- depends: 0006_add_vector_store_id_to_tenants

ALTER TABLE invoices
RENAME COLUMN open_ai_file_id TO open_ai_pdf_file_id;

ALTER TABLE invoices
ADD COLUMN open_ai_json_file_id CHARACTER VARYING NULL;
