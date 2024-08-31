-- 
-- depends: 0005_rename_issue_date

ALTER TABLE tenants
ADD COLUMN open_ai_vector_store_id CHARACTER VARYING NULL;
