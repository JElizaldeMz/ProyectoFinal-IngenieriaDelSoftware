# Sistema de Reservación y Mapeo
## Festival Internacional de las Luciérnagas 2026
### MEC Solutions

---

## Pasos para levantar el proyecto (siguiendo el tutorial Django)

### 1. Activar el entorno de Conda

```bash
conda activate nombreEntorno
```

### 2. Navegar a la carpeta del proyecto

```bash
cd /ruta/donde/clonaste/el/proyecto
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

El archivo `.env` ya está incluido con valores de desarrollo.
Para producción, cambia los valores de `SECRET_KEY`, `EMAIL_HOST_USER` y `EMAIL_HOST_PASSWORD`.

### 5. Aplicar las migraciones (crear la base de datos)

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear un superusuario (administrador del sistema)

```bash
python manage.py createsuperuser
```
Ingresa: correo electrónico, nombre, apellido y contraseña.

### 7. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

El sistema estará disponible en: http://127.0.0.1:8000/

---

## Estructura del proyecto

```
luciernagas_project/
├── manage.py
├── requirements.txt
├── .env                        ← variables de entorno (NO subir a GitHub)
├── .gitignore
├── luciernagas/                ← paquete de configuración central
│   ├── __init__.py
│   ├── settings.py             ← configuración (Patrón Singleton)
│   ├── urls.py                 ← rutas raíz
│   └── wsgi.py
├── apps/
│   ├── usuarios/               ← modelos: Usuario, Cliente, Administrador
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── migrations/
│   ├── parques/                ← modelo: Parque + vistas CRUD admin
│   │   ├── models.py
│   │   ├── views.py            ← Patrón Template Method (CBV)
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── migrations/
│   └── reservaciones/          ← modelo: Reservacion + TipoVisita
│       ├── models.py           ← Patrón Observer (señal post_save)
│       ├── validaciones.py     ← Patrón Strategy (3 clases de validación)
│       ├── views.py
│       ├── forms.py
│       ├── urls.py
│       └── migrations/
├── templates/
│   ├── base.html               ← template base del sistema
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
│   ├── reservaciones/
│   │   ├── nueva_reservacion.html
│   │   ├── confirmacion.html
│   │   ├── mis_reservaciones.html
│   │   ├── confirmar_cancelacion.html
│   │   └── admin/
│   │       └── todas_reservaciones.html
│   └── usuarios/
│       └── dashboard.html
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
| **Observer** | `apps/reservaciones/models.py` | `post_save` → envío de correo |
| **Template Method** | `apps/parques/views.py` | CBV para CRUD del administrador |
| **Singleton** | `luciernagas/settings.py` | Configuración global del sistema |

---

## Reglas de negocio implementadas

- **RNF01** — Solo fechas de junio a agosto 2026 (`ValidacionFestival`)
- **RNF02** — Sin días martes (`ValidacionSinMartes`)
- **RNF03** — Todos los parques tienen camping; cabañas es opcional
- **RNF04** — Contraseñas con hashing seguro (PBKDF2)
- **RNF06** — Control de capacidad máxima por parque (`ValidacionDisponibilidad`)
