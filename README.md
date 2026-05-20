# LunchFlow

Solucion web para la gestion de almuerzos corporativos. LunchFlow centraliza la entrega de beneficios de alimentacion para empleados mediante registro de consumos con codigo QR, control de pagos y saldos, administracion por roles y visualizacion de metricas para apoyar la operacion y la toma de decisiones.

## Acceso rapido

- Aplicacion desplegada: `https://web-production-de81d.up.railway.app/`

## Contexto del proyecto

LunchFlow fue desarrollado como una entrega academica final orientada a resolver la gestion de almuerzos corporativos para una empresa cliente. El proyecto busca digitalizar tareas que normalmente se manejan de forma manual, como la validacion de consumos, el seguimiento de pagos y la consulta del estado de cuenta por parte de empleados, administradores y personal del restaurante.

En esta etapa, el proyecto se presenta como una solucion funcional, desplegada y lista para evaluacion, demostracion y continuidad operativa.

## Funcionalidades principales

- Registro de consumos mediante codigos QR para agilizar la validacion de almuerzos.
- Gestion de pagos, saldos y estado de cuenta para el seguimiento financiero del beneficio.
- Paneles diferenciados por rol para empleados, administradores y restaurante.
- Herramientas administrativas para gestion de personal, inventario y reportes.
- Analitica basica y estimacion de demanda para apoyar decisiones operativas.
- Integracion de vistas operativas para consultar historial de consumos y movimientos del sistema.

## Arquitectura y stack

- Backend en Django.
- Base de datos PostgreSQL.
- Despliegue y hosting en Railway.
- Contenedorizacion con Docker y orquestacion con Docker Compose.
- Archivos estaticos servidos con WhiteNoise.

## Acceso a la aplicacion

La version principal del sistema se encuentra disponible en Railway:

`https://web-production-de81d.up.railway.app`

Puntos de acceso relevantes:

- Aplicacion web: `https://web-production-de81d.up.railway.app/`
- Panel administrativo: `https://web-production-de81d.up.railway.app/admin/`

## Como ejecutar la solucion localmente

### Requisitos previos

Antes de ejecutar el proyecto localmente, asegurese de tener instalado:

- Docker Desktop o Docker Engine con Docker Compose
- Python 3.10 o superior

Puede verificarlo con:

```bash
docker --version
docker compose version
python --version
```

### Levantar el entorno con Docker

Desde la raiz del proyecto ejecute:

```bash
docker compose up --build
```

Este comando construye la imagen de la aplicacion, levanta el contenedor web y el servicio de PostgreSQL, y expone la aplicacion en el puerto `8000`.

### Migraciones

Si necesita aplicar migraciones manualmente:

```bash
docker compose exec web python manage.py migrate
```

### Crear un superusuario

Para acceder al panel administrativo local:

```bash
docker compose exec web python manage.py createsuperuser
```

### Rutas locales

- Aplicacion local: `http://localhost:8000`
- Administracion Django: `http://localhost:8000/admin`
- Adminer: `http://localhost:8080`

### Operacion basica

- Ver logs del contenedor web:

```bash
docker compose logs -f web
```

- Detener los servicios:

```bash
docker compose down
```

La base de datos local corre en un contenedor PostgreSQL separado y el entorno fue preparado para ejecutarse principalmente mediante Docker Compose.

## Estado actual y continuidad

La fase academica del proyecto se considera finalizada y el sistema cuenta con una version desplegada y funcional. Aun asi, la base del proyecto permite continuar con mantenimiento correctivo, ajustes operativos y nuevas mejoras si la empresa cliente decide extender su uso o evolucion.

## Equipo y cliente

Este repositorio corresponde a una entrega academica de `Proyecto2_EAFIT` orientada al desarrollo de LunchFlow para la empresa UDP SA.

Integrantes del desarrollo:

- Juan Simon Ospina
- Sebastian Duran
- Juan Nicolas Vasquez
- Juan Jose Gomez
- Valeria Aguilar

Cliente beneficiario:

- Empresa UDP SA.
