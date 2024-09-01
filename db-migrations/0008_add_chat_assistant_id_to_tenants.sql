-- 
-- depends: 0007_refactor_open_ai_columns_on_invoices

ALTER TABLE tenants
ADD COLUMN open_ai_chat_assistant_id CHARACTER VARYING NULL;
