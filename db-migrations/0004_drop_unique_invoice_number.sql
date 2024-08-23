-- 
-- depends: 0003_add_open_ai_file_id_to_invoices_table

ALTER TABLE invoices
DROP CONSTRAINT IF EXISTS invoices_invoice_number_key;


