# Acortador de Enlaces Cloud (AWS S3 + DynamoDB + EC2)

Aplicación web integral para acortar enlaces construida sobre servicios de Amazon Web Services (AWS):

- **Amazon EC2**: Aloja y ejecuta la API REST desarrollada con **FastAPI** y **Uvicorn**, protegida con un **IAM Role** para acceso a DynamoDB.
- **Amazon DynamoDB**: Base de datos NoSQL donde se persisten las URLs originales, sus identificadores generados dinámicamente con UUID (`short_code`) y la fecha de creación (`created_at`).
- **Amazon S3**: Alojamiento estático del Frontend desarrollado con HTML, CSS y JavaScript moderno.

---

## 🌿 Estructura de Ramas

- **`api`**: Contiene la implementación del Backend en FastAPI, pruebas automatizadas, configuración de DynamoDB, variables de entorno y servicio systemd para EC2.
- **`main`**: Rama principal del repositorio.

---

## 📂 Estructura del Repositorio

```text
Acortador_Links/
├── .gitignore
├── README.md
└── Acortador/
    ├── Backend/
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── config.py         # Configuración y variables de entorno
    │   │   ├── database.py       # Conexión Boto3 a DynamoDB e IAM Role
    │   │   ├── models.py         # Esquemas Pydantic
    │   │   ├── services.py       # Lógica de UUID y operaciones DynamoDB
    │   │   └── routers/          # Endpoints (/shorten, /{short_code}, /urls, /health)
    │   ├── tests/                # Pruebas automatizadas con pytest
    │   ├── systemd/              # Servicio systemd para Linux/EC2
    │   ├── .env.example
    │   ├── requirements.txt
    │   └── README.md
    └── Frontend/                 # Archivos estáticos para Amazon S3 (HTML/CSS/JS)
```

Para instrucciones detalladas sobre la instalación, configuración y ejecución del Backend, consulte [Acortador/Backend/README.md](Acortador/Backend/README.md).
