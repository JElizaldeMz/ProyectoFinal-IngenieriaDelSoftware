# Sistema de Reservación y Mapeo
## Festival Internacional de las Luciérnagas 2026
### MEC Solutions

---

## Requisitos previos

- Python 3.12
- Conda (recomendado) o virtualenv
- Git

---

## Pasos para levantar el proyecto

### 1. Activar el entorno de Conda

```bash
conda activate nombreEntorno
```

### 2. Navegar a la carpeta del proyecto

```bash
cd luciernagas_project
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Copia el archivo de ejemplo y llénalo con tus propios valores:

```bash
cp .env.example .env
```

Abre el archivo `.env` y configura las siguientes variables:

```env
SECRET_KEY=tu_clave_secreta_aqui

DEBUG=True

DATABASE_URL=sqlite:///db.sqlite3

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contrasena_de_aplicacion
```

> **Notas importantes:**
> - En desarrollo puedes dejar `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` — los correos se imprimirán en la terminal en lugar de enviarse realmente.
> - Para producción cambia `EMAIL_BACKEND` a `django.core.mail.backends.smtp.EmailBackend` y configura un correo real con contraseña de aplicación de Gmail (no tu contraseña normal).
> - Nunca subas el archivo `.env` a GitHub. Ya está incluido en `.gitignore`.
> - La `SECRET_KEY` puede generarse con:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

### 5. Aplicar las migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear un superusuario (administrador del sistema)

```bash
python manage.py createsuperuser
```

El sistema pedirá: correo electrónico, nombre, apellido y contraseña.
Este usuario tendrá acceso al panel de administrador del sistema.

### 7. Cargar los datos de prueba (recomendado)

```bash
python manage.py seed_data
```

Esto crea automáticamente los 2 administradores, 9 parques de Oaxaca, 10 clientes y 20 reservaciones de prueba listos para usar. Ver sección **Base de datos de prueba** para las credenciales.

### 8. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

El sistema estará disponible en: http://127.0.0.1:8000/

---

## Acceso al sistema

Con el servidor corriendo en http://127.0.0.1:8000/, estas son las URLs y el flujo de cada tipo de usuario:

### Administrador

| Acción | URL |
|---|---|
| Iniciar sesión como admin | http://127.0.0.1:8000/usuarios/login/ |
| Panel Django Admin (gestión avanzada) | http://127.0.0.1:8000/admin/ |
| Lista de parques (CRUD) | http://127.0.0.1:8000/parques/admin/ |
| Crear nuevo parque | http://127.0.0.1:8000/parques/admin/crear/ |
| Ver todas las reservaciones | http://127.0.0.1:8000/reservaciones/admin/todas/ |

**Flujo del administrador:**
1. Entrar a http://127.0.0.1:8000/usuarios/login/ con una cuenta `is_staff=True`
2. Desde ahí puede gestionar parques, configurar disponibilidad y consultar reservaciones
3. Para el panel técnico de Django: http://127.0.0.1:8000/admin/

> **Credenciales de prueba (tras ejecutar `seed_data`):**
> - `admin@luciernagas.mx` / `admin1234`
> - `jeduardo@luciernagas.mx` / `mec2026`

---

### Usuario cliente

| Acción | URL |
|---|---|
| Página principal | http://127.0.0.1:8000/ |
| Registrarse (cuenta nueva) | http://127.0.0.1:8000/usuarios/registro/ |
| Iniciar sesión | http://127.0.0.1:8000/usuarios/login/ |
| Ver mapa de parques | http://127.0.0.1:8000/parques/mapa/ |
| Mis reservaciones | http://127.0.0.1:8000/reservaciones/mis-reservaciones/ |

**Flujo del cliente:**
1. Entrar a http://127.0.0.1:8000/ — página principal con los parques destacados
2. Registrarse en http://127.0.0.1:8000/usuarios/registro/ o iniciar sesión si ya tiene cuenta
3. Explorar el mapa interactivo y hacer clic en un parque para ver su detalle
4. Desde el detalle del parque, hacer clic en "Reservar" para abrir el formulario
5. Seleccionar fechas (junio–agosto 2026, sin martes), número de personas y tipo de visita
6. Al confirmar, el sistema registra la reservación y envía el correo de confirmación a la terminal (en modo desarrollo)
7. Consultar y cancelar reservaciones en "Mis reservaciones"

> **Credenciales de prueba (tras ejecutar `seed_data`):**
> - `vtorres@gmail.com` / `Festival2026!`
> - `aguzman@gmail.com` / `Oaxaca2026!`
> - (ver sección **Base de datos de prueba** para la lista completa)

---

### Visitante sin sesión

Un visitante que no ha iniciado sesión puede:
- Ver la página principal con los parques destacados
- Explorar el mapa interactivo y ver la información de cada parque
- No puede realizar reservaciones — el sistema redirige al login si lo intenta

---

## Base de datos de prueba

El proyecto incluye datos de ejemplo realistas para demostrar el sistema funcionando.
Se cargan **2 administradores, 9 parques en Oaxaca, 10 usuarios clientes y 20 reservaciones**.

### Cargar todos los datos de prueba

```bash
python manage.py seed_data
```

### Limpiar la base de datos y volver a cargar desde cero

```bash
python manage.py seed_data --reset
```

### Cuentas de prueba disponibles tras el seed

#### Administradores

| Correo | Contraseña | Acceso |
|---|---|---|
| `admin@luciernagas.mx` | `admin1234` | Panel administrador completo |
| `jeduardo@luciernagas.mx` | `mec2026` | Panel administrador completo |

#### Clientes

| Nombre | Correo | Contraseña |
|---|---|---|
| Valentina Torres Mendoza | `vtorres@gmail.com` | `Festival2026!` |
| Rodrigo Espinoza Rios | `rodrigo.esp@hotmail.com` | `Luciernagas26` |
| Mariana Fuentes Castillo | `mfuentes@outlook.com` | `Camping2026#` |
| Alejandro Guzman Lopez | `aguzman@gmail.com` | `Oaxaca2026!` |
| Sofia Herrera Vazquez | `sofi.herrera@gmail.com` | `Sierra2026*` |
| Emilio Ramirez Ortega | `eramirez@live.com` | `Festival26!` |
| Daniela Morales Quispe | `dmorales@gmail.com` | `Oaxaca2026#` |
| Fernando Salinas Cruz | `fsalinas@yahoo.com` | `Luciernaga26!` |
| Camila Reyes Dominguez | `creyes@gmail.com` | `Camping26*` |
| Luis Pacheco Ibarra | `lpacheco@hotmail.com` | `Festival26#` |

#### Parques cargados (9 parques en el estado de Oaxaca)

| Parque | Región | Cabañas | Cap. Camping | Cap. Cabañas |
|---|---|---|---|---|
| Bosque Comunal Cuajimoloyas | Sierra Norte | Sí | 30 | 8 |
| Reserva Natural Lachatao | Sierra Norte | No | 40 | — |
| Parque Ecoturístico Etla | Valles Centrales | Sí | 25 | 5 |
| Sendero Nocturno Yagul | Valles Centrales | No | 20 | — |
| Bosque de Niebla San José del Pacífico | Sierra Sur | Sí | 20 | 10 |
| Reserva Comunal Miahuatlán | Sierra Sur | No | 35 | — |
| Parque Natural Mixteca Alta — Huajuapan | Mixteca | Sí | 30 | 6 |
| Cañada Verde — Teotitlán del Camino | Cañada | No | 45 | — |
| Reserva Ecoturística Tuxtepec | Papaloapan | Sí | 25 | 7 |

---

## Ejecutar las pruebas

El proyecto cuenta con 42 pruebas distribuidas en 3 niveles:

```bash
python manage.py test apps.reservaciones.tests
```

Para ver el detalle de cada prueba:

```bash
python manage.py test apps.reservaciones.tests --verbosity=2
```

Resultado esperado: `Ran 42 tests in ~14s OK`

---

## Estructura del proyecto

```
luciernagas_project/
├── manage.py
├── requirements.txt
├── .env                        ← variables de entorno (NO subir a GitHub)
├── .env.example                ← plantilla de variables de entorno
├── .gitignore
├── luciernagas/                ← paquete de configuración central
│   ├── settings.py             ← configuración (Patrón Singleton)
│   ├── urls.py                 ← rutas raíz
│   └── wsgi.py
├── apps/
│   ├── usuarios/               ← modelos: Usuario, Cliente, Administrador
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── urls.py
│   ├── parques/                ← modelo: Parque + vistas CRUD admin
│   │   ├── models.py
│   │   ├── views.py            ← Patrón Template Method (CBV)
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── fixtures/
│   │   │   └── parques_prueba.json   ← fixture con 4 parques de prueba rápida
│   │   └── management/
│   │       └── commands/
│   │           └── seed_data.py      ← comando para cargar datos realistas
│   └── reservaciones/          ← modelo: Reservacion + TipoVisita
│       ├── models.py           ← Patrón Observer (señal post_save)
│       ├── validaciones.py     ← Patrón Strategy (3 clases de validación)
│       ├── views.py
│       ├── forms.py
│       ├── urls.py
│       └── tests/
│           ├── test_validaciones.py  ← 17 pruebas de unidad (Strategy)
│           ├── test_models.py        ← 9 pruebas de unidad (modelos)
│           ├── test_integracion.py   ← 13 pruebas de integración (HTTP)
│           └── test_sistema.py       ← 3 pruebas de sistema (end-to-end)
├── templates/
│   ├── base.html               ← template base del sistema (herencia global)
│   ├── registration/
│   │   ├── login.html
│   │   └── registro.html
│   ├── parques/
│   │   ├── landing.html
│   │   ├── mapa.html           ← integra Leaflet.js
│   │   ├── detalle.html
│   │   └── admin/
│   │       ├── form_parque.html
│   │       ├── lista_parques.html
│   │       └── confirmar_eliminacion.html
│   └── reservaciones/
│       ├── nueva_reservacion.html
│       ├── confirmacion.html
│       ├── mis_reservaciones.html
│       ├── confirmar_cancelacion.html
│       └── admin/
│           └── todas_reservaciones.html
└── static/
    ├── css/
    ├── js/
    └── img/
```

---

## Patrones de diseño implementados

| Patrón | Archivo | Descripción |
|---|---|---|
| **Strategy** | `apps/reservaciones/validaciones.py` | 3 clases de validación independientes |
| **Observer** | `apps/reservaciones/models.py` | `post_save` → envío de correo automático |
| **Template Method** | `apps/parques/views.py` | CBV para CRUD del administrador |
| **Singleton** | `luciernagas/settings.py` | Configuración global del sistema |

---

## Reglas de negocio implementadas

| ID | Regla | Clase responsable |
|---|---|---|
| RNF01 | Solo fechas de junio a agosto 2026 | `ValidacionFestival` |
| RNF02 | Sin días martes (mantenimiento de parques) | `ValidacionSinMartes` |
| RNF03 | Todos los parques tienen camping; cabañas es opcional | Modelo `Parque` |
| RNF04 | Contraseñas con hashing seguro (PBKDF2-SHA256) | Django auth |
| RNF06 | Control de capacidad máxima por parque | `ValidacionDisponibilidad` |
