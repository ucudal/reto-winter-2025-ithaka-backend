# reto-winter-2025-ithaka-backend

##  Opciones de Ejecución

Puedes ejecutar esta aplicación de **dos formas**:

### 1.  **Docker (Recomendado para producción)**
```bash
# Opción A: Usar imagen del registry
docker pull crretoxmas2024.azurecr.io/ithaka-backend:latest
docker run -p 8000:8000 crretoxmas2024.azurecr.io/ithaka-backend:latest

# Opción B: Construir localmente
docker build -t ithaka-backend .
docker run -p 8000:8000 ithaka-backend

# Opción C: Docker Compose (desarrollo)
docker-compose up
```

### 2.  **Desarrollo Local (Python)**

## Requisitos

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (gestor de paquetes compatible con pip)

## Instalación

### 1. Crear entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar `uv`
Si no lo tenés instalado, escribí en la terminal:

```bash
pip install uv
```

### 3. Instalar dependencias
```bash
uv pip install -r requirements.txt
```

### 4. Ejecución
Para ejecutarlo ir a la raíz del proyecto y ejecutar:

```bash
uvicorn app.main:app --reload
```

### Documentación
Podes revisar la doc en http://127.0.0.1:8000/docs

# Instrucciones para usar la base de datos y el ORM

## 1. Instalar dependencias

Asegúrate de tener las dependencias necesarias:

```
pip install -r requirements.txt
```

## 2. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido (ajusta los valores según tu entorno):

```
DATABASE_URL=postgresql+asyncpg://<USUARIO>:<PASSWORD>@<HOST>:<PUERTO>/<NOMBRE_DB>
```

## 3. Crear la base de datos y usuario en PostgreSQL

Solo ejecuta este bloque si el usuario y la base de datos NO existen:

```
CREATE USER <USUARIO> WITH PASSWORD '<PASSWORD>';
CREATE DATABASE <NOMBRE_DB> OWNER <USUARIO>;
GRANT ALL PRIVILEGES ON DATABASE <NOMBRE_DB> TO <USUARIO>;
```

> **Nota:**
> Si el usuario o la base de datos ya existen, puedes omitir estos comandos y solo asegurarte de que el usuario tiene permisos sobre la base de datos.

## 4. Crear las tablas en la base de datos

Ejecuta el siguiente comando desde la raíz del proyecto:

```
python -m app.db.config.create_tables
```

Esto creará las tablas `conversations`, `messages` y `postulations`.

## 5. Correr la API

Inicia el servidor de desarrollo:

```
uvicorn app.main:app --reload
```

# Cómo usar ruff

- Analizar el código:
  ```bash
  ruff check .

  ```

## CI/CD y Docker

### Pipeline Automático
- **Trigger:** Push a ramas `DevOps` o `main`
- **Registry:** `crretoxmas2024.azurecr.io/ithaka-backend`
- **Tags:** Automático por rama y commit SHA

### Usar imagen de producción
```bash
# Pull de la imagen del registry
docker pull crretoxmas2024.azurecr.io/ithaka-backend:latest

# Ejecutar contenedor
docker run -p 8000:8000 -e DATABASE_URL=sqlite+aiosqlite:///./app.db crretoxmas2024.azurecr.io/ithaka-backend:latest
```

### Variables de entorno para Docker
```env
DATABASE_URL=sqlite+aiosqlite:///./app.db  # Para desarrollo con SQLite
# O para PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database
```

---

# Funcionamiento de notificación por WhatsApp
- Ingresar a https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn?frameUrl=%2Fconsole%2Fsms%2Fwhatsapp%2Flearn%3Fx-target-region%3Dus1
- Enviar mensaje al número de WhatsApp +14155238886 con el mensaje `join may-steady`
- Obtener las credenciales y token de Twilio
- Agregar un archivo .env con las credenciales de Twilio
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

# Funcionamiento de notificación por correo
- Agregar un archivo .env con las variables de entorno de Gmail
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=ithakapostula@gmail.com
EMAIL_PASS= clave en tarjeta de Trello
```

# CI/CD Pipeline Test - Wed Jul 30 11:49:28 -03 2025
