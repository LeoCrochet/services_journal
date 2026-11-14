-- Создание роли БД через psql-переменную.
-- Запускать через deploy/setup_db.sh, который передаёт :db_password.
SELECT format('CREATE ROLE services_journal LOGIN PASSWORD %L', :'db_password')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'services_journal')\gexec