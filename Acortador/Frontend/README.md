# Frontend Web - Acortador de Enlaces para Amazon S3

Interfaz web moderna, ligera y responsiva desarrollada en **HTML5**, **CSS3** y **JavaScript (Vanilla)**, diseñada para ser alojada como sitio web estático en **Amazon S3** y consumir la API REST desarrollada en **FastAPI** ejecutándose sobre **Amazon EC2**.

---

## 📋 Características

- **Sin frameworks adicionales**: Desarrollada exclusivamente con tecnologías web estándar (HTML/CSS/JS) para máxima portabilidad, velocidad y ligereza.
- **Formulario interactivo**: Permite ingresar la URL original con validación inmediata en el cliente.
- **Consumo asíncrono con `fetch()`**: Envía la solicitud `POST /shorten` al backend en EC2.
- **Portapapeles universal**: Botón de copia directa con compatibilidad tanto para entornos HTTPS como HTTP (requerido por el endpoint estático de S3).
- **Apertura y prueba inmediata**: Enlace directo para abrir el enlace corto y verificar la redirección HTTP 307 hacia la página de destino.
- **Configuración dinámica de API**: Permite configurar la IP pública de EC2 en `config.js` o cambiarla en caliente directamente desde la interfaz.
- **Manejo de errores claro**: Notifica al usuario en caso de URL inválida, fallos de red o problemas de conexión/CORS con el backend.

---

## 📂 Archivos del Frontend

```text
Acortador/Frontend/
├── index.html       # Estructura semántica, alertas y tarjetas de resultado
├── styles.css       # Estilos visuales modernos, responsivos y accesibles
├── config.js        # Configuración de la URL del Backend FastAPI en EC2
├── app.js           # Lógica JavaScript (fetch, validación, copiado, eventos)
└── README.md        # Esta guía de despliegue en Amazon S3
```

---

## 🚀 Guía de Despliegue en Amazon S3

Siga estos pasos para alojar la interfaz en un bucket de Amazon S3:

### 1. Crear el Bucket en Amazon S3
1. Inicie sesión en la consola de AWS y acceda a **Amazon S3**.
2. Haga clic en **Crear bucket** (Create bucket).
3. Asigne un nombre único a nivel global (ejemplo: `acortador-enlaces-frontend-tu-nombre`).
4. Seleccione la misma región donde tiene su instancia EC2 (por ejemplo, `us-east-1`).
5. En la sección **Bloqueo de acceso público (Block Public Access)**:
   - **Desmarque** la casilla *"Bloquear todo el acceso público"* (Block all public access).
   - Marque la casilla de reconocimiento de advertencia.
6. Deje las demás opciones por defecto y haga clic en **Crear bucket**.

---

### 2. Habilitar Alojamiento de Sitios Web Estáticos
1. Ingrese al bucket recién creado y diríjase a la pestaña **Propiedades** (Properties).
2. Desplácese hasta el final hasta la sección **Alojamiento de sitios web estáticos** (Static website hosting).
3. Haga clic en **Editar**:
   - Seleccione **Habilitar** (Enable).
   - Tipo de alojamiento: **Alojar un sitio web estático**.
   - **Documento de índice**: escriba exactamente `index.html`.
4. Haga clic en **Guardar cambios**.
5. Al final de la página se generará el **Punto de enlace del sitio web del bucket** (Bucket website endpoint), con un formato similar a:
   ```text
   http://acortador-enlaces-frontend-tu-nombre.s3-website-us-east-1.amazonaws.com
   ```

---

### 3. Configurar la Política de Acceso Público del Bucket
1. En el bucket, diríjase a la pestaña **Permisos** (Permissions).
2. En la sección **Política de bucket** (Bucket policy), haga clic en **Editar**.
3. Pegue la siguiente política, sustituyendo `<NOMBRE-DE-TU-BUCKET>` por el nombre de su bucket:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::<NOMBRE-DE-TU-BUCKET>/*"
        }
    ]
}
```
4. Haga clic en **Guardar cambios**.

---

### 4. Configurar la URL de la API y Subir Archivos
1. Abra el archivo `config.js` y reemplace `DEFAULT_API_URL` con la IP pública y puerto de su instancia EC2:
   ```javascript
   const CONFIG = {
       DEFAULT_API_URL: "http://<IP-PUBLICA-EC2>:8000",
       // ...
   };
   ```
2. En la consola de S3, vaya a la pestaña **Objetos** (Objects) del bucket y haga clic en **Cargar** (Upload).
3. Suba los siguientes 4 archivos:
   - `index.html`
   - `styles.css`
   - `config.js`
   - `app.js`
4. Haga clic en **Cargar**.

---

### 5. Configurar CORS en el Backend (EC2)
Asegúrese de que el backend en EC2 permita peticiones desde el endpoint de S3:
- En el archivo `.env` del backend en EC2, defina:
  ```env
  ALLOWED_ORIGINS=http://acortador-enlaces-frontend-tu-nombre.s3-website-us-east-1.amazonaws.com
  ```
  *(o `ALLOWED_ORIGINS=*` para permitir cualquier origen durante las pruebas).*

---

### 6. Probar la Aplicación
1. Abra el enlace generado por S3 en su navegador.
2. Ingrese una URL de prueba (por ejemplo: `https://aws.amazon.com/dynamodb/`).
3. Presione **Acortar enlace**.
4. Copie el enlace corto generado y ábralo en una nueva pestaña para comprobar que se realice la redirección HTTP automática a la página de destino.
