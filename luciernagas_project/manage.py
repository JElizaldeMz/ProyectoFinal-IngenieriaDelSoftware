#!/usr/bin/env python
"""
Utilidad de línea de comandos de Django para tareas administrativas.
Sistema de Reservación y Mapeo — Festival Internacional de las Luciérnagas 2026
"""
import os
import sys


def main():
    """Punto de entrada principal."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luciernagas.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Activaste tu entorno de conda?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
