# Proyecto2_EAFIT
Aplicación web para la gestión integral de almuerzos corporativos, que automatiza el registro de consumo mediante códigos QR, el control de pagos y saldos, y la visualización de métricas administrativas, apoyando la toma de decisiones a través de analítica básica y estimación de demanda.

## Requisitos Previos

Antes de ejecutar el proyecto, asegúrate de tener instalado:
- **Python 3.10+**
- **Docker** y **Docker Compose** (Para levantar la base de datos PostgreSQL)
- **Git**

## Pasos para ejecutar el proyecto

Sigue estas instrucciones para levantar el proyecto localmente para revisión:

### 1. Iniciar la Base de Datos con Docker

El proyecto utiliza PostgreSQL, el cual está configurado vía Docker. En la raíz del proyecto (donde se encuentra el archivo `docker-compose.yml`), ejecuta el siguiente comando para levantar la base de datos en segundo plano:

```bash
docker-compose up -d
```
*(Opcional: puedes acceder a Adminer en `http://localhost:8080` para visualizar la base de datos)*

### 2. Crear y activar un entorno virtual

Se recomienda usar un entorno virtual para aislar las dependencias del proyecto.

En **Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

En **macOS / Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

Con el entorno virtual activado, instala las dependencias necesarias de Python:
```bash
pip install -r requirements.txt
```

### 4. Ejecutar las migraciones

Aplica las migraciones para estructurar la base de datos de la aplicación:
```bash
python manage.py migrate
```

### 5. Crear un superusuario (Opcional)

Si necesitas acceder al panel de administración de Django, puedes crear un superusuario:
```bash
python manage.py createsuperuser
```
Te pedirá un nombre de usuario, correo electrónico y contraseña.

### 6. Levantar el servidor de desarrollo

Finalmente, inicia el servidor de desarrollo de Django:
```bash
python manage.py runserver
```

### 7. Acceder a la aplicación

Abre tu navegador web e ingresa a la siguiente dirección:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

*Para el panel de administración, ingresa a `http://127.0.0.1:8000/admin/`.*
