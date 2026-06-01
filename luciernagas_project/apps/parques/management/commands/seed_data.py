"""
Comando para cargar datos de ejemplo realistas.
Estado de Oaxaca — Festival Internacional de las Luciérnagas 2026.

Uso:
    python manage.py seed_data           # carga todo
    python manage.py seed_data --reset   # limpia BD y vuelve a cargar
"""

from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction


SUPERUSUARIOS = [
    {
        "nombre": "Admin",
        "apellido": "MEC Solutions",
        "email": "admin@luciernagas.mx",
        "password": "admin1234",
    },
    {
        "nombre": "Jesus Eduardo",
        "apellido": "Elizalde Maza",
        "email": "jeduardo@luciernagas.mx",
        "password": "mec2026",
    },
]

# 9 parques repartidos por las distintas regiones del estado de Oaxaca
PARQUES = [
    # ── Sierra Norte ──────────────────────────────────────────────────────────
    {
        "nombre": "Bosque Comunal Cuajimoloyas",
        "direccional": "Cuajimoloyas, San Miguel Amatlán, Ixtlán de Juárez, Oaxaca",
        "servicios": "Guías especializados en avistamiento de luciérnagas, zona de fogata, baños ecológicos, estacionamiento, tienda de artesanías locales",
        "horario": "19:00 – 23:30",
        "latitud": 17.2167,
        "longitud": -96.4333,
        "tiene_cabanas": True,
        "cap_camping": 30,
        "cap_cabanas": 8,
    },
    {
        "nombre": "Reserva Natural Lachatao",
        "direccional": "Santa Catarina Lachatao, Ixtlán de Juárez, Oaxaca",
        "servicios": "Observación de luciérnagas en bosque de pino-encino, sendero ecológico 3 km, área de descanso, estacionamiento gratuito",
        "horario": "19:00 – 22:30",
        "latitud": 17.3100,
        "longitud": -96.3850,
        "tiene_cabanas": False,
        "cap_camping": 40,
        "cap_cabanas": 0,
    },
    # ── Valles Centrales ──────────────────────────────────────────────────────
    {
        "nombre": "Parque Ecoturístico Etla",
        "direccional": "San Pedro y San Pablo Etla, Valles Centrales, Oaxaca",
        "servicios": "Zona boscosa con luciérnagas, palapa comunitaria, sanitarios, área de fogata, acceso a mercado artesanal los fines de semana",
        "horario": "18:30 – 22:30",
        "latitud": 17.2050,
        "longitud": -96.8100,
        "tiene_cabanas": True,
        "cap_camping": 25,
        "cap_cabanas": 5,
    },
    {
        "nombre": "Sendero Nocturno Yagul",
        "direccional": "Unión Zapata, Tlacolula de Matamoros, Valles Centrales, Oaxaca",
        "servicios": "Sendero 2 km al borde de zona arqueológica, guía nocturno, venta de mezcal artesanal y tlayudas, sanitarios",
        "horario": "19:30 – 23:00",
        "latitud": 16.9550,
        "longitud": -96.4600,
        "tiene_cabanas": False,
        "cap_camping": 20,
        "cap_cabanas": 0,
    },
    # ── Sierra Sur ────────────────────────────────────────────────────────────
    {
        "nombre": "Bosque de Niebla San José del Pacífico",
        "direccional": "San José del Pacífico, Yautepec, Sierra Sur, Oaxaca",
        "servicios": "Avistamiento en bosque de niebla a 2 700 msnm, cabañas con chimenea, baños calientes, restaurante comunitario, área de meditación",
        "horario": "19:00 – 23:00",
        "latitud": 16.1450,
        "longitud": -96.6500,
        "tiene_cabanas": True,
        "cap_camping": 20,
        "cap_cabanas": 10,
    },
    {
        "nombre": "Reserva Comunal Miahuatlán",
        "direccional": "San Marcos Tlapazola, Miahuatlán de Porfirio Díaz, Sierra Sur, Oaxaca",
        "servicios": "Tour guiado en cafetal iluminado de luciérnagas, zona de camping, baños ecológicos, venta de café de altura y chocolate artesanal",
        "horario": "19:00 – 22:00",
        "latitud": 16.3300,
        "longitud": -96.5950,
        "tiene_cabanas": False,
        "cap_camping": 35,
        "cap_cabanas": 0,
    },
    # ── Mixteca ───────────────────────────────────────────────────────────────
    {
        "nombre": "Parque Natural Mixteca Alta — Huajuapan",
        "direccional": "San Marcos Arteaga, Huajuapan de León, Mixteca, Oaxaca",
        "servicios": "Caminata nocturna entre milpas y bosque de encino, guías bilingües (español/mixteco), zona de camping, sanitarios, venta de tejidos",
        "horario": "20:00 – 23:30",
        "latitud": 17.7800,
        "longitud": -97.7750,
        "tiene_cabanas": True,
        "cap_camping": 30,
        "cap_cabanas": 6,
    },
    # ── Cañada ────────────────────────────────────────────────────────────────
    {
        "nombre": "Cañada Verde — Teotitlán del Camino",
        "direccional": "Teotitlán del Camino, Cañada, Oaxaca",
        "servicios": "Avistamiento en barranca boscosa, sendero iluminado 1.5 km, área de camping junto al río, sanitarios, venta de pan de yema local",
        "horario": "19:30 – 23:00",
        "latitud": 18.1300,
        "longitud": -97.0650,
        "tiene_cabanas": False,
        "cap_camping": 45,
        "cap_cabanas": 0,
    },
    # ── Papaloapan ────────────────────────────────────────────────────────────
    {
        "nombre": "Reserva Ecoturística Tuxtepec",
        "direccional": "San José Chiltepec, Tuxtepec, Papaloapan, Oaxaca",
        "servicios": "Avistamiento en selva tropical baja, recorrido en lancha por el río Papaloapan, cabañas palafíticas, guías locales, restaurante con mariscos",
        "horario": "18:00 – 22:30",
        "latitud": 18.0900,
        "longitud": -96.1200,
        "tiene_cabanas": True,
        "cap_camping": 25,
        "cap_cabanas": 7,
    },
]

USUARIOS = [
    {"nombre": "Valentina",  "apellido": "Torres Mendoza",    "email": "vtorres@gmail.com",        "password": "Festival2026!"},
    {"nombre": "Rodrigo",    "apellido": "Espinoza Rios",     "email": "rodrigo.esp@hotmail.com",  "password": "Luciernagas26"},
    {"nombre": "Mariana",    "apellido": "Fuentes Castillo",  "email": "mfuentes@outlook.com",     "password": "Camping2026#"},
    {"nombre": "Alejandro",  "apellido": "Guzman Lopez",      "email": "aguzman@gmail.com",        "password": "Oaxaca2026!"},
    {"nombre": "Sofia",      "apellido": "Herrera Vazquez",   "email": "sofi.herrera@gmail.com",   "password": "Sierra2026*"},
    {"nombre": "Emilio",     "apellido": "Ramirez Ortega",    "email": "eramirez@live.com",        "password": "Festival26!"},
    {"nombre": "Daniela",    "apellido": "Morales Quispe",    "email": "dmorales@gmail.com",       "password": "Oaxaca2026#"},
    {"nombre": "Fernando",   "apellido": "Salinas Cruz",      "email": "fsalinas@yahoo.com",       "password": "Luciernaga26!"},
    {"nombre": "Camila",     "apellido": "Reyes Dominguez",   "email": "creyes@gmail.com",         "password": "Camping26*"},
    {"nombre": "Luis",       "apellido": "Pacheco Ibarra",    "email": "lpacheco@hotmail.com",     "password": "Festival26#"},
]

# (idx_usuario, idx_parque, fecha_inicio, fecha_termino, personas, tipo, estado)
# Sin martes, dentro de jun–ago 2026
RESERVACIONES = [
    # Valentina (0)
    (0, 0, date(2026, 6, 4),  date(2026, 6, 6),  2, "cabana",  "activa"),
    (0, 3, date(2026, 7, 9),  date(2026, 7, 11), 1, "camping", "activa"),
    # Rodrigo (1)
    (1, 4, date(2026, 6, 11), date(2026, 6, 13), 4, "cabana",  "activa"),
    (1, 6, date(2026, 8, 6),  date(2026, 8, 8),  2, "cabana",  "cancelada"),
    # Mariana (2)
    (2, 1, date(2026, 6, 18), date(2026, 6, 20), 3, "camping", "activa"),
    (2, 8, date(2026, 7, 23), date(2026, 7, 25), 2, "cabana",  "activa"),
    # Alejandro (3)
    (3, 2, date(2026, 7, 2),  date(2026, 7, 4),  5, "cabana",  "activa"),
    (3, 5, date(2026, 8, 13), date(2026, 8, 15), 2, "camping", "activa"),
    # Sofia (4)
    (4, 6, date(2026, 6, 25), date(2026, 6, 27), 2, "cabana",  "activa"),
    (4, 0, date(2026, 7, 16), date(2026, 7, 18), 3, "camping", "cancelada"),
    # Emilio (5)
    (5, 4, date(2026, 8, 20), date(2026, 8, 22), 4, "cabana",  "activa"),
    (5, 7, date(2026, 6, 4),  date(2026, 6, 6),  1, "camping", "activa"),
    # Daniela (6)
    (6, 3, date(2026, 6, 11), date(2026, 6, 13), 2, "camping", "activa"),
    (6, 8, date(2026, 8, 6),  date(2026, 8, 8),  3, "cabana",  "activa"),
    # Fernando (7)
    (7, 1, date(2026, 7, 9),  date(2026, 7, 11), 4, "camping", "activa"),
    (7, 5, date(2026, 6, 25), date(2026, 6, 27), 2, "camping", "cancelada"),
    # Camila (8)
    (8, 2, date(2026, 8, 13), date(2026, 8, 15), 2, "cabana",  "activa"),
    (8, 6, date(2026, 7, 2),  date(2026, 7, 4),  3, "cabana",  "activa"),
    # Luis (9)
    (9, 0, date(2026, 6, 18), date(2026, 6, 20), 5, "camping", "activa"),
    (9, 7, date(2026, 8, 20), date(2026, 8, 22), 2, "camping", "activa"),
]


class Command(BaseCommand):
    help = "Carga datos de ejemplo — Festival de las Luciernagas 2026, Oaxaca"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Elimina todos los datos existentes antes de cargar",
        )

    def handle(self, *args, **options):
        from apps.parques.models import Parque
        from apps.reservaciones.models import Reservacion
        from apps.usuarios.models import Usuario, Cliente

        if options["reset"]:
            self.stdout.write("Limpiando datos existentes...")
            Reservacion.objects.all().delete()
            Cliente.objects.all().delete()
            Usuario.objects.filter(is_superuser=False).delete()
            Parque.objects.all().delete()
            self.stdout.write(self.style.WARNING("  Datos eliminados.\n"))

        with transaction.atomic():

            # ── Superusuarios ─────────────────────────────────────────────────
            self.stdout.write("Cargando superusuarios (acceso a /admin)...")
            for datos in SUPERUSUARIOS:
                if Usuario.objects.filter(email=datos["email"]).exists():
                    self.stdout.write(f"  – {datos['email']} (ya existe)")
                else:
                    Usuario.objects.create_superuser(
                        email=datos["email"],
                        nombre=datos["nombre"],
                        apellido=datos["apellido"],
                        password=datos["password"],
                    )
                    self.stdout.write(
                        f"  {self.style.SUCCESS('✔')} {datos['email']} "
                        f"| contraseña: {datos['password']}"
                    )

            # ── Parques ───────────────────────────────────────────────────────
            self.stdout.write("\nCargando parques...")
            parques_creados = []
            for datos in PARQUES:
                parque, creado = Parque.objects.get_or_create(
                    nombre=datos["nombre"],
                    defaults=datos,
                )
                parques_creados.append(parque)
                marca  = self.style.SUCCESS("✔") if creado else "–"
                estado = "creado" if creado else "ya existia"
                self.stdout.write(f"  {marca} {parque.nombre} ({estado})")

            # ── Usuarios / Clientes ───────────────────────────────────────────
            self.stdout.write("\nCargando usuarios clientes...")
            usuarios_creados = []
            for datos in USUARIOS:
                if Usuario.objects.filter(email=datos["email"]).exists():
                    usuario = Usuario.objects.get(email=datos["email"])
                    self.stdout.write(f"  – {usuario.get_full_name()} (ya existe)")
                else:
                    usuario = Usuario.objects.create_user(
                        email=datos["email"],
                        nombre=datos["nombre"],
                        apellido=datos["apellido"],
                        password=datos["password"],
                    )
                    self.stdout.write(
                        f"  {self.style.SUCCESS('✔')} {usuario.get_full_name()} "
                        f"| {datos['email']} | contraseña: {datos['password']}"
                    )
                Cliente.objects.get_or_create(usuario=usuario)
                usuarios_creados.append(usuario)

            # ── Reservaciones ─────────────────────────────────────────────────
            self.stdout.write("\nCargando reservaciones...")
            for idx_u, idx_p, fi, ft, personas, tipo, estado in RESERVACIONES:
                usuario = usuarios_creados[idx_u]
                parque  = parques_creados[idx_p]
                cliente = usuario.cliente

                if Reservacion.objects.filter(
                    cliente=cliente, parque=parque,
                    fecha_inicio=fi, fecha_termino=ft,
                ).exists():
                    self.stdout.write(f"  – {usuario.nombre} en {parque.nombre} (ya existe)")
                    continue

                Reservacion.objects.create(
                    cliente=cliente,
                    parque=parque,
                    fecha_inicio=fi,
                    fecha_termino=ft,
                    num_personas=personas,
                    tipo_visita=tipo,
                    estado=estado,
                )
                self.stdout.write(
                    f"  {self.style.SUCCESS('✔')} {usuario.nombre} -> {parque.nombre} "
                    f"({fi} - {ft}, {tipo}, {estado})"
                )

            # ── Recalcular contadores ─────────────────────────────────────────
            self.stdout.write("\nActualizando disponibilidad de parques...")
            for parque in parques_creados:
                parque.ocupados_camping = Reservacion.objects.filter(
                    parque=parque, tipo_visita="camping", estado="activa"
                ).count()
                parque.ocupados_cabanas = Reservacion.objects.filter(
                    parque=parque, tipo_visita="cabana", estado="activa"
                ).count()
                parque.save()
                self.stdout.write(
                    f"  {parque.nombre}: "
                    f"camping {parque.ocupados_camping}/{parque.cap_camping}  "
                    f"cabanas {parque.ocupados_cabanas}/{parque.cap_cabanas}"
                )

        self.stdout.write(self.style.SUCCESS(
            f"\nListo: {len(SUPERUSUARIOS)} superusuarios, "
            f"{len(parques_creados)} parques, "
            f"{len(usuarios_creados)} clientes, "
            f"{len(RESERVACIONES)} reservaciones."
        ))
