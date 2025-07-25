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