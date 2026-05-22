"""
Patrón Observer — Notificaciones de reservaciones
MEC Solutions
"""

from abc import ABC, abstractmethod
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Observer(ABC):

    @abstractmethod
    def actualizar(self, reservacion):
        pass


def _enviar_correo(asunto, texto_plano, html, destinatario):
    """Envía correo con versión HTML y texto plano como fallback."""
    try:
        msg = EmailMultiAlternatives(
            subject=asunto,
            body=texto_plano,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[destinatario],
        )
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)
    except Exception as e:
        logger.error(f'Error al enviar correo: {e}')


class EmailConfirmacionObserver(Observer):

    def actualizar(self, reservacion):
        nombre    = reservacion.cliente.usuario.get_full_name()
        correo    = reservacion.cliente.usuario.email
        parque    = reservacion.parque.nombre
        direccion = reservacion.parque.direccional
        tipo      = reservacion.get_tipo_visita_display()
        inicio    = reservacion.fecha_inicio.strftime('%d/%m/%Y')
        termino   = reservacion.fecha_termino.strftime('%d/%m/%Y')
        personas  = reservacion.num_personas
        pk        = reservacion.pk

        asunto = f'✅ Reservación #{pk} confirmada — Festival Luciérnagas 2026'

        texto = (
            f'Hola {nombre},\n\n'
            f'Tu reservación ha sido confirmada.\n\n'
            f'Parque: {parque}\n'
            f'Tipo: {tipo}\n'
            f'Inicio: {inicio}\n'
            f'Término: {termino}\n'
            f'Personas: {personas}\n\n'
            f'¡Te esperamos!\n— MEC Solutions'
        )

        html = f"""
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0f0c29;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0c29;padding:40px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#1a1744,#2d2660);border-radius:16px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.5);">

        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#f0c040,#f97316);padding:32px;text-align:center;">
            <div style="font-size:48px;margin-bottom:8px;">🌟</div>
            <h1 style="margin:0;color:#1a1a2e;font-size:22px;font-weight:700;letter-spacing:0.05em;">
              FESTIVAL INTERNACIONAL<br>DE LAS LUCIÉRNAGAS 2026
            </h1>
          </td>
        </tr>

        <!-- Badge confirmado -->
        <tr>
          <td style="padding:28px 32px 0;text-align:center;">
            <div style="display:inline-block;background:rgba(16,185,129,0.2);border:1px solid rgba(16,185,129,0.4);border-radius:24px;padding:8px 24px;">
              <span style="color:#6ee7b7;font-size:14px;font-weight:600;letter-spacing:0.08em;">✅ RESERVACIÓN CONFIRMADA</span>
            </div>
            <p style="color:rgba(255,255,255,0.6);font-size:14px;margin:16px 0 0;">
              Hola <strong style="color:#fff;">{nombre}</strong>, tu lugar en el festival está asegurado.
            </p>
          </td>
        </tr>

        <!-- Datos de la reservación -->
        <tr>
          <td style="padding:24px 32px;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.06);border-radius:12px;overflow:hidden;">
              <tr style="border-bottom:1px solid rgba(255,255,255,0.08);">
                <td style="padding:14px 20px;color:rgba(255,255,255,0.5);font-size:12px;text-transform:uppercase;letter-spacing:0.06em;width:40%;">Reservación</td>
                <td style="padding:14px 20px;color:#f0c040;font-size:14px;font-weight:600;">#{pk}</td>
              </tr>
              <tr style="border-bottom:1px solid rgba(255,255,255,0.08);">
                <td style="padding:14px 20px;color:rgba(255,255,255,0.5);font-size:12px;text-transform:uppercase;letter-spacing:0.06em;">Parque</td>
                <td style="padding:14px 20px;color:#fff;font-size:14px;">{parque}</td>
              </tr>
              <tr style="border-bottom:1px solid rgba(255,255,255,0.08);">
                <td style="padding:14px 20px;color:rgba(255,255,255,0.5);font-size:12px;text-transform:uppercase;letter-spacing:0.06em;">Dirección</td>
                <td style="padding:14px 20px;color:rgba(255,255,255,0.75);font-size:13px;">{direccion}</td>
              </tr>
              <tr style="border-bottom:1px solid rgba(255,255,255,0.08);">
                <td style="padding:14px 20px;color:rgba(255,255,255,0.5);font-size:12px;text-transform:uppercase;letter-spacing:0.06em;">Tipo de visita</td>
                <td style="padding:14px 20px;color:#fff;font-size:14px;">{tipo}</td>
              </tr>
              <tr style="border-bottom:1px solid rgba(255,255,255,0.08);">
                <td style="padding:14px 20px;color:rgba(255,255,255,0.5);font-size:12px;text-transform:uppercase;letter-spacing:0.06em;">Fechas</td>
                <td style="padding:14px 20px;color:#fff;font-size:14px;">{inicio} → {termino}</td>
              </tr>
              <tr>
                <td style="padding:14px 20px;color:rgba(255,255,255,0.5);font-size:12px;text-transform:uppercase;letter-spacing:0.06em;">Personas</td>
                <td style="padding:14px 20px;color:#fff;font-size:14px;">{personas}</td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="padding:0 32px 32px;text-align:center;">
            <p style="color:rgba(255,255,255,0.4);font-size:12px;margin:0;">
              © 2026 MEC Solutions — Ingeniería de Software · Facultad de Ciencias · UNAM
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

        _enviar_correo(asunto, texto, html, correo)


class EmailCancelacionObserver(Observer):

    def actualizar(self, reservacion):
        nombre   = reservacion.cliente.usuario.get_full_name()
        correo   = reservacion.cliente.usuario.email
        parque   = reservacion.parque.nombre
        tipo     = reservacion.get_tipo_visita_display()
        inicio   = reservacion.fecha_inicio.strftime('%d/%m/%Y')
        termino  = reservacion.fecha_termino.strftime('%d/%m/%Y')
        personas = reservacion.num_personas
        pk       = reservacion.pk

        asunto = f'❌ Reservación #{pk} cancelada — Festival Luciérnagas 2026'

        texto = (
            f'Hola {nombre},\n\n'
            f'Tu reservación #{pk} en {parque} ha sido cancelada.\n\n'
            f'Si fue un error puedes realizar una nueva reservación.\n\n'
            f'— MEC Solutions'
        )

        html = f"""
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0f0c29;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0c29;padding:40px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#1a1744,#2d2660);border-radius:16px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.5);">

        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#ef4444,#b91c1c);padding:32px;text-align:center;">
            <div style="font-size:48px;margin-bottom:8px;">🌟</div>
            <h1 style="margin:0;color:#fff;font-size:22px;font-weight:700;letter-spacing:0.05em;">
              FESTIVAL INTERNACIONAL<br>DE LAS LUCIÉRNAGAS 2026
            </h1>
          </td>
        </tr>

        <!-- Badge cancelado -->
        <tr>
          <td style="padding:28px 32px 0;text-align:center;">
            <div style="display:inline-block;background:rgba(239,68,68,0.2);border:1px solid rgba(239,68,68,0.4);border-radius:24px;padding:8px 24px;">
              <span style="color:#fca5a5;font-size:14px;font-weight:600;letter-spacing:0.08em;">❌ RESERVACIÓN CANCELADA</span>
            </div>
            <p style="color:rgba(255,255,255,0.6);font-size:14px;margin:16px 0 0;">
              Hola <strong style="color:#fff;">{nombre}</strong>, tu reservación ha sido cancelada.
            </p>
          </td>
        </tr>

        <!-- Datos -->
        <tr>
          <td style="padding:24px 32px;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.06);border-radius:12px;overflow:hidden;">
              <tr style="border-bottom:1px solid rgba(255,255,255,0.08);">
                <td style="padding:14px 20px;color:rgba(255,255,255,0.5);font-size:12px;text-transform:uppercase;letter-spacing:0.06em;width:40%;">Reservación</td>
                <td style="padding:14px 20px;color:#fca5a5;font-size:14px;font-weight:600;">#{pk}</td>
              </tr>
              <tr style="border-bottom:1px solid rgba(255,255,255,0.08);">
                <td style="padding:14px 20px;color:rgba(255,255,255,0.5);font-size:12px;text-transform:uppercase;letter-spacing:0.06em;">Parque</td>
                <td style="padding:14px 20px;color:#fff;font-size:14px;">{parque}</td>
              </tr>
              <tr style="border-bottom:1px solid rgba(255,255,255,0.08);">
                <td style="padding:14px 20px;color:rgba(255,255,255,0.5);font-size:12px;text-transform:uppercase;letter-spacing:0.06em;">Tipo de visita</td>
                <td style="padding:14px 20px;color:#fff;font-size:14px;">{tipo}</td>
              </tr>
              <tr style="border-bottom:1px solid rgba(255,255,255,0.08);">
                <td style="padding:14px 20px;color:rgba(255,255,255,0.5);font-size:12px;text-transform:uppercase;letter-spacing:0.06em;">Fechas</td>
                <td style="padding:14px 20px;color:#fff;font-size:14px;">{inicio} → {termino}</td>
              </tr>
              <tr>
                <td style="padding:14px 20px;color:rgba(255,255,255,0.5);font-size:12px;text-transform:uppercase;letter-spacing:0.06em;">Personas</td>
                <td style="padding:14px 20px;color:#fff;font-size:14px;">{personas}</td>
              </tr>
            </table>
            <p style="color:rgba(255,255,255,0.5);font-size:13px;text-align:center;margin:20px 0 0;">
              ¿Fue un error? Puedes realizar una nueva reservación en el sistema.
            </p>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="padding:0 32px 32px;text-align:center;">
            <p style="color:rgba(255,255,255,0.4);font-size:12px;margin:0;">
              © 2026 MEC Solutions — Ingeniería de Software · Facultad de Ciencias · UNAM
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

        _enviar_correo(asunto, texto, html, correo)


class ReservacionSubject:

    def __init__(self):
        self._observers = []

    def agregar_observer(self, observer: Observer):
        self._observers.append(observer)

    def notificar(self, reservacion):
        for observer in self._observers:
            observer.actualizar(reservacion)
