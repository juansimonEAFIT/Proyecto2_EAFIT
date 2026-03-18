-- 1) Crear/asegurar el rol de la app (en DO porque aquí sí se permite IF)
DO
$$
BEGIN
   IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'p2usr') THEN
      -- Puedes usar CREATE USER también; CREATE ROLE + LOGIN es equivalente
      CREATE ROLE p2usr LOGIN PASSWORD 'proyecto_2_psw';
   ELSE
      -- Si ya existe, asegurar login y actualizar contraseña
      ALTER ROLE p2usr WITH LOGIN PASSWORD 'proyecto_2_psw';
   END IF;
END
$$;

-- 2) Crear la base si no existe (OJO: NO dentro de DO; CREATE DATABASE no admite transacción)
-- Este patrón usa psql y \gexec para ejecutar la sentencia devuelta por SELECT.
-- Los scripts en /docker-entrypoint-initdb.d/ se ejecutan con psql, así que funciona.
SELECT 'CREATE DATABASE lunchflow OWNER p2usr'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'lunchflow')\gexec

-- 3) Ajustar privilegios en la base (conéctate primero a esa base)
\connect lunchflow

-- Asegurar propietario del esquema público para que la app pueda crear objetos
ALTER SCHEMA public OWNER TO p2usr;

-- (Opcional) Conceder privilegios por defecto para objetos futuros creados por el superusuario
-- Esto afecta solo objetos creados por el rol que ejecuta estas sentencias.
-- ALTER DEFAULT PRIVILEGES GRANT ALL ON TABLES TO p2usr;
-- ALTER DEFAULT PRIVILEGES GRANT ALL ON SEQUENCES TO p2usr;
-- ALTER DEFAULT PRIVILEGES GRANT ALL ON FUNCTIONS TO p2usr;