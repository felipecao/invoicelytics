-- 
-- depends: 0008_add_chat_assistant_id_to_tenants  0009_change_unique_constraints_on_users

ALTER TABLE invoices
RENAME COLUMN validated_by TO approved_by;
