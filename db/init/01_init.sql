-- Script de inicialización para la base de datos de Ithaka Chatbot
-- Este script se ejecuta automáticamente cuando se crea el contenedor de PostgreSQL

-- Crear extensiones útiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Crear índices para mejorar las búsquedas de texto
-- (Estos se crearán después de que SQLAlchemy cree las tablas)

-- Comentarios sobre la estructura de la base de datos
COMMENT ON DATABASE ithaka_chatbot IS 'Base de datos para el chatbot de postulaciones de Ithaka - UCU';

-- Configuraciones adicionales para mejor rendimiento
-- Ajustar según recursos disponibles en producción
-- ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
-- ALTER SYSTEM SET pg_stat_statements.track = 'all';

-- Crear función para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'Base de datos de Ithaka Chatbot inicializada correctamente';
END $$; 