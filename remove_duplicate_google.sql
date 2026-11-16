-- =============================================================================
-- Remove the duplicate "Google" company, keeping only "Google India".
-- =============================================================================
-- Any job postings currently under "Google" are moved to "Google India"
-- first, so nothing is silently lost — then the "Google" row itself is
-- deleted. Safe to run even if one of the two companies doesn't exist
-- (it just does nothing in that case).
--
-- HOW TO RUN
--   mysql -u <your_db_user> -p <your_db_name> < remove_duplicate_google.sql
-- (or paste into MySQL Workbench / phpMyAdmin / TablePlus and run as a script)
-- =============================================================================

SET @google_plain_id = (SELECT id FROM companies WHERE name = 'Google' LIMIT 1);
SET @google_india_id = (SELECT id FROM companies WHERE name = 'Google India' LIMIT 1);

-- Move any jobs posted under "Google" over to "Google India"
UPDATE jobs
SET company_id = @google_india_id
WHERE company_id = @google_plain_id
  AND @google_plain_id IS NOT NULL
  AND @google_india_id IS NOT NULL;

-- Remove the now-empty "Google" company row
DELETE FROM companies
WHERE id = @google_plain_id
  AND @google_plain_id IS NOT NULL;

-- Confirm the result
SELECT id, name FROM companies ORDER BY name;
