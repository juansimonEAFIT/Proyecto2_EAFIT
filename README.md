# Proyecto2_EAFIT
Aplicación web para la gestión integral de almuerzos corporativos, que automatiza el registro de consumo mediante códigos QR, el control de pagos y saldos, y la visualización de métricas administrativas, apoyando la toma de decisiones a través de analítica básica y estimación de demanda.

---

## Requerimientos previos

Para ejecutar correctamente el proyecto, asegúrate de tener instalado:

### 1. Docker Desktop o Docker Engine + Docker Compose
Verifica la instalación con:

```bash
docker --version
docker compose version
```

### 2. Python 3.10+ (opcional, solo si deseas usar venv fuera de Docker)
```bash
python --version
```

---

## (Opcional) Crear entorno virtual

Si deseas ejecutar scripts o herramientas fuera de Docker, puedes crear un entorno virtual:

```bash
python -m venv .venv
```

Activación:

**Windows (PowerShell):**
```bash
.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

Instalar dependencias manualmente (opcional):

```bash
pip install -r requirements.txt
```

---

## Ejecutar la aplicación con Docker

### 1. Construir y levantar los contenedores

En el directorio raíz del proyecto:

```bash
docker compose up --build
```

Esto:
- Construye la imagen de la aplicación  
- Instala dependencias  
- Levanta el servidor web y la base de datos  
- Inicia el backend en puerto 8000  

---

### 2. Aplicar migraciones (si tu entrypoint no lo hace automáticamente)

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

> Nota: si tu servicio no se llama `web` en docker-compose.yml, ajusta el nombre en los comandos.

---

### 3. Crear un superusuario

```bash
docker compose exec web python manage.py createsuperuser
```

O si necesitas hacerlo sin interacción:

```bash
docker compose exec web python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser("admin", "admin@example.com", "admin123")
exit()
```

---

## Acceso a la aplicación

### Aplicación principal:
```
http://localhost:8000
```

### Administrador de Django:
```
http://localhost:8000/admin
```

Inicia sesión con el superusuario que creaste.

---

## Comandos útiles

### Entrar al shell interactivo de Django
```bash
docker compose exec web python manage.py shell
```

### Ver logs del contenedor
```bash
docker compose logs -f web
```

### Reiniciar contenedores
```bash
docker compose down
docker compose up --build
```

---

## Resetear completamente la base de datos (solo desarrollo)

Si las migraciones fallan o la base de datos está inconsistente:

```bash
docker compose down -v
docker compose up --build
```

Esto borra los volúmenes y la base de datos, luego la reconstruye desde cero.

---

## Notas para desarrollo

- Ejecuta siempre comandos de Django desde el contenedor usando:  
  `docker compose exec web ...`
- Si eliminas apps o cambias modelos de forma importante, borra migraciones y resetea la base con `docker compose down -v`.
- Los roles se manejan desde `User.role`.
- Los perfiles se crean automáticamente mediante signals.

---

## Errores comunes (solo desarrollo)

 - Un posible error que puede recivir en el momento de ejecucion es uno relacionado al archivo entrypoint.sh del programa y se veria de esta forma:
```bash
env: ‘bash\r’: No such file or directory
env: use -[v]S to pass options in shebang lines
```
En el caso que esto suceda no se preocupe, todo lo que tiene que hacer es lo siguiente:

1. En la linea de comandos escribir el siguiente comando:
```bash
git config core.autocrlf false
```
esto configurara a git para que no vuelva a pasar este problema en esta maquina

2. En tu editor de texto simplemente selecciona el archivo entrypoint.sh y busca como se cambia el tipo de espaciado en tu editor de preferencia. Para vscode, PyCharm y AntiGravity esto esta en la esquina derecha abajo al lado de una opcion UTF-8, simplemente dar click a CRLF(o el que aparezca) y cambiar a LF
  
 
