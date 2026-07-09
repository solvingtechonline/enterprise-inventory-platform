-- Script de preparación de PostgreSQL (única base de datos del sistema).
-- Ejecutar una sola vez, conectado como superusuario (ej. `psql -U postgres`).
--
-- Django administra las tablas de Empresa/Productos/Usuarios.
-- SQLAlchemy (FastAPI) administra exclusivamente la tabla Inventario y
-- la tabla de embeddings del agente de IA (producto_embedding).
-- Todas viven en la MISMA base de datos.

CREATE USER lite_thinking_user WITH PASSWORD 'lite_thinking_password';

CREATE DATABASE lite_thinking_db OWNER lite_thinking_user;

GRANT ALL PRIVILEGES ON DATABASE lite_thinking_db TO lite_thinking_user;

-- La extensión pgvector debe habilitarse DENTRO de lite_thinking_db (no en la
-- base de datos por defecto), y requiere el paquete `postgresql-<version>-pgvector`
-- (o equivalente) ya instalado a nivel de sistema operativo antes de este paso.
-- Es la única extensión nueva que introduce el agente de IA; no agrega
-- infraestructura adicional.
\c lite_thinking_db

CREATE EXTENSION IF NOT EXISTS vector;
