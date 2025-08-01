# reto-winter-2025-ithaka-backend

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

