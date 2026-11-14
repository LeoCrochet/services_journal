DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'services_journal') THEN
      CREATE USER services_journal WITH PASSWORD 'SjDb_2026_pw_Tr777';
   END IF;
END
$$;