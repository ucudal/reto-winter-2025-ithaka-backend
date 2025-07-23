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