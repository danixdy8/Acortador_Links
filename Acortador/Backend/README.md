# Backend API - Acortador de Enlaces con FastAPI y DynamoDB

API REST modular y de alto rendimiento desarrollada con **FastAPI**, **Boto3** y **Uvicorn**, diseñada para ejecutarse en **Amazon EC2** y almacenar la información de los enlaces en **Amazon DynamoDB**, sirviendo peticiones a la interfaz web desplegada en **Amazon S3**.

---

## 📋 Características Principales

- **Generación dinámica de identificadores UUID**: Cada enlace corto recibe un identificador único generado mediante `uuid.uuid4()`.
- **Persistencia en Amazon DynamoDB**: Almacena `short_code`, `original_url` y fecha/hora UTC `created_at`.
- **Redirección HTTP 307 real**: Endpoint `GET /{short_code}` que redirige automáticamente al navegador a la URL original.
- **Consulta de metadatos**: Endpoint `GET /urls/{short_code}` para inspeccionar detalles del enlace en formato JSON.
- **Soporte CORS integrado**: Permite peticiones directas desde el bucket de Amazon S3 donde se aloja el frontend.
- **Seguridad mediante IAM Role**: El backend no almacena claves de acceso en el código; Boto3 adquiere credenciales temporales automáticamente desde el rol asociado a la instancia EC2.
- **Health Check**: Endpoint `GET /health` para monitorear el estado de la API y la conectividad con la tabla de DynamoDB.
- **Servicio Systemd listo para EC2**: Archivo de configuración para mantener la API ejecutándose en segundo plano continuamente.

---

## 🏛 Estructura del Proyecto

```text
Acortador/Backend/
├── app/
│   ├── __init__.py          # Inicialización del paquete
│   ├── config.py            # Configuración y variables de entorno (Pydantic BaseSettings)
│   ├── database.py          # Cliente Boto3 y conexión a DynamoDB
│   ├── models.py            # Esquemas de datos (Pydantic models)
│   ├── services.py          # Lógica de negocio (generación UUID, DynamoDB CRUD)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py        # Endpoint GET /health
│   │   ├── shorten.py       # Endpoints POST /shorten y GET /urls/{short_code}
│   │   └── redirect.py      # Endpoint GET /{short_code} (Redirección HTTP 307)
│   └── main.py              # Instancia FastAPI, CORS y registro de routers
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Fixtures y mock en memoria para pruebas
│   └── test_api.py          # Suite de pruebas unitarias y de integración
├── systemd/
│   └── acortador.service    # Configuración de systemd para despliegue en EC2
├── .env.example             # Plantilla de variables de entorno
├── requirements.txt         # Dependencias de producción y pruebas
└── README.md                # Documentación técnica
```

---

## 🚀 Endpoints de la API

### 1. Crear enlace corto
- **Método**: `POST`
- **Ruta**: `/shorten`
- **Código de Estado**: `201 Created`
- **Cuerpo de la solicitud (JSON)**:
  ```json
  {
    "original_url": "https://www.example.com/articulos/arquitectura-cloud"
  }
  ```
- **Respuesta (JSON)**:
  ```json
  {
    "short_code": "550e8400-e29b-41d4-a716-446655440000",
    "original_url": "https://www.example.com/articulos/arquitectura-cloud",
    "short_url": "http://<ip-publica-ec2>:8000/550e8400-e29b-41d4-a716-446655440000"
  }
  ```

---

### 2. Redireccionar al destino original
- **Método**: `GET`
- **Ruta**: `/{short_code}`
- **Código de Estado**: `307 Temporary Redirect` (o `404 Not Found` si el UUID no existe)
- **Cabecera de respuesta**: `Location: <original_url>`
- **Comportamiento**: Redirección HTTP real en el navegador al destino original.

---

### 3. Consultar información de un enlace
- **Método**: `GET`
- **Ruta**: `/urls/{short_code}`
- **Código de Estado**: `200 OK` (o `404 Not Found`)
- **Respuesta (JSON)**:
  ```json
  {
    "short_code": "550e8400-e29b-41d4-a716-446655440000",
    "original_url": "https://www.example.com/articulos/arquitectura-cloud",
    "created_at": "2026-10-29T23:59:00.123456+00:00",
    "short_url": "http://<ip-publica-ec2>:8000/550e8400-e29b-41d4-a716-446655440000"
  }
  ```

---

### 4. Health Check
- **Método**: `GET`
- **Ruta**: `/health`
- **Respuesta (JSON)**:
  ```json
  {
    "status": "healthy",
    "app": "Acortador de Enlaces API",
    "version": "1.0.0",
    "dynamodb_table": "shortened-urls",
    "dynamodb_status": "connected (status: ACTIVE)"
  }
  ```

---

### 5. Documentación Interactiva (Swagger / OpenAPI)
- **Swagger UI**: `http://<ip-publica-ec2>:8000/docs`
- **ReDoc**: `http://<ip-publica-ec2>:8000/redoc`

---

## ⚙️ Variables de Entorno

Cree un archivo `.env` basado en `.env.example`:

| Variable | Descripción | Valor por Defecto |
| :--- | :--- | :--- |
| `AWS_REGION` | Región de AWS donde está la tabla DynamoDB | `us-east-1` |
| `DYNAMODB_TABLE_NAME` | Nombre de la tabla DynamoDB | `shortened-urls` |
| `BASE_URL` | URL base pública para generar `short_url` (ej. `http://54.x.x.x:8000`) | Detectada automáticamente de la petición |
| `ALLOWED_ORIGINS` | Orígenes permitidos en CORS (ej. URL del bucket S3 o `*`) | `*` |
| `DEBUG` | Activar logs de depuración | `false` |

---

## 🛠 Instalación y Ejecución Local

1. **Crear y activar el entorno virtual**:
   ```bash
   # En Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # En Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la suite de pruebas automatizadas**:
   ```bash
   pytest -v
   ```

4. **Iniciar el servidor de desarrollo**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

---

## ☁️ Guía de Despliegue en AWS

### Paso 1: Crear la tabla en Amazon DynamoDB
1. Ingrese a la consola de AWS -> **DynamoDB** -> **Crear tabla**.
2. **Nombre de la tabla**: `shortened-urls`
3. **Clave de partición (Partition key)**: `short_code` (Tipo: `String`)
4. **Capacidad**: Configuración predeterminada o *On-Demand (Bajo demanda)*.

### Paso 2: Crear el Rol IAM para la Instancia EC2
1. Ingrese a **IAM** -> **Roles** -> **Crear rol**.
2. Seleccione **Servicio de AWS** -> Caso de uso: **EC2**.
3. Asigne una política en línea (Inline Policy) con permisos mínimos:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "dynamodb:GetItem",
           "dynamodb:PutItem",
           "dynamodb:DescribeTable"
         ],
         "Resource": "arn:aws:dynamodb:*:*:table/shortened-urls"
       }
     ]
   }
   ```
4. Asigne el nombre al rol (ej: `EC2-DynamoDB-Shortener-Role`) y créelo.

### Paso 3: Lanzar la Instancia Amazon EC2
1. Lance una instancia EC2 (Ubuntu 24.04 LTS o Amazon Linux 2023, tipo `t2.micro` o `t3.micro`).
2. En la sección **IAM Instance Profile**, adjunte el rol creado en el Paso 2 (`EC2-DynamoDB-Shortener-Role`).
3. En el **Security Group**:
   - Inbound Rule 1: **SSH (22)** desde su IP.
   - Inbound Rule 2: **Custom TCP (8000)** desde `0.0.0.0/0` (o restringido a CloudFront/S3 si aplica).

### Paso 4: Configurar la Instancia EC2 y Ejecutar con Systemd
Conéctese por SSH a la instancia EC2 y ejecute:

```bash
# 1. Actualizar paquetes del sistema
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git

# 2. Clonar el repositorio y cambiarse a la rama api
git clone https://github.com/<tu-usuario>/Acortador_Links.git
cd Acortador_Links
git checkout api

# 3. Preparar el entorno virtual
cd Acortador/Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
nano .env
# Configure su IP pública de EC2: BASE_URL=http://<IP-PUBLICA-EC2>:8000

# 5. Instalar y habilitar el servicio con systemd
sudo cp systemd/acortador.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable acortador
sudo systemctl start acortador

# 6. Comprobar el estado del servicio
sudo systemctl status acortador
```
