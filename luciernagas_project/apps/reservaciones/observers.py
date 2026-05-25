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
    try:
        msg = EmailMultiAlternatives(
            subject=asunto, body=texto_plano,
            from_email=settings.DEFAULT_FROM_EMAIL, to=[destinatario],
        )
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)
    except Exception as e:
        logger.error(f'Error al enviar correo: {e}')


def _html_base(contenido_inner, color_header='#3d2c1a'):
    """Genera el esqueleto HTML del correo con hojas SVG decorativas."""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#c8bc96;font-family:Arial,sans-serif;">

<!-- Fondo con textura de hojas SVG -->
<table width="100%" cellpadding="0" cellspacing="0"
       style="background:linear-gradient(160deg,#cfc49a 0%,#c0b48a 60%,#b8a87e 100%);
              padding:48px 0;min-height:100vh;">
<tr><td align="center" style="padding:0 16px;">

  <!-- Decoración superior: hojas SVG -->
  <table width="600" cellpadding="0" cellspacing="0" style="max-width:100%;">
  <tr><td style="text-align:center;padding-bottom:8px;">
    <svg width="600" height="60" viewBox="0 0 600 60" xmlns="http://www.w3.org/2000/svg" style="display:block;max-width:100%;">
      <!-- hojas izq -->
      <g fill="#8a9e7a" opacity="0.55">
        <ellipse cx="40" cy="30" rx="38" ry="14" transform="rotate(-25 40 30)"/>
        <ellipse cx="15" cy="45" rx="28" ry="11" transform="rotate(-45 15 45)"/>
        <ellipse cx="70" cy="15" rx="32" ry="12" transform="rotate(-10 70 15)"/>
      </g>
      <!-- hojas der -->
      <g fill="#8a9e7a" opacity="0.55">
        <ellipse cx="560" cy="28" rx="36" ry="13" transform="rotate(22 560 28)"/>
        <ellipse cx="585" cy="48" rx="25" ry="10" transform="rotate(40 585 48)"/>
        <ellipse cx="530" cy="12" rx="30" ry="11" transform="rotate(8 530 12)"/>
      </g>
      <!-- mariposa izq -->
      <g fill="#e3a36e" opacity="0.5" transform="translate(110,20)">
        <ellipse cx="-8" cy="-4" rx="10" ry="6" transform="rotate(-20 -8 -4)"/>
        <ellipse cx="8"  cy="-4" rx="10" ry="6" transform="rotate(20 8 -4)"/>
        <ellipse cx="-5" cy="5"  rx="7"  ry="4" transform="rotate(-30 -5 5)"/>
        <ellipse cx="5"  cy="5"  rx="7"  ry="4" transform="rotate(30 5 5)"/>
      </g>
      <!-- mariposa der -->
      <g fill="#c47d45" opacity="0.45" transform="translate(490,18)">
        <ellipse cx="-8" cy="-4" rx="9" ry="5" transform="rotate(-15 -8 -4)"/>
        <ellipse cx="8"  cy="-4" rx="9" ry="5" transform="rotate(15 8 -4)"/>
        <ellipse cx="-5" cy="4"  rx="6" ry="3.5" transform="rotate(-25 -5 4)"/>
        <ellipse cx="5"  cy="4"  rx="6" ry="3.5" transform="rotate(25 5 4)"/>
      </g>
      <!-- luciérnagas punteadas -->
      <circle cx="150" cy="25" r="3" fill="#f0c040" opacity="0.8"/>
      <circle cx="160" cy="15" r="2" fill="#ffd060" opacity="0.6"/>
      <circle cx="200" cy="40" r="2.5" fill="#f0c040" opacity="0.7"/>
      <circle cx="400" cy="20" r="3" fill="#f0c040" opacity="0.8"/>
      <circle cx="420" cy="38" r="2" fill="#ffd060" opacity="0.6"/>
      <circle cx="350" cy="12" r="2.5" fill="#f0c040" opacity="0.75"/>
      <!-- glows -->
      <circle cx="150" cy="25" r="7" fill="rgba(240,192,64,0.2)"/>
      <circle cx="400" cy="20" r="7" fill="rgba(240,192,64,0.2)"/>
    </svg>
  </td></tr>
  </table>

  <!-- Tarjeta principal -->
  <table width="600" cellpadding="0" cellspacing="0"
         style="background:#faf7f3;border:1px solid rgba(87,61,33,0.12);
                border-radius:4px;overflow:hidden;
                box-shadow:0 20px 60px rgba(0,0,0,0.18);max-width:100%;">

    {contenido_inner}

    <!-- Footer -->
    <tr>
      <td style="background:#f0e8d8;border-top:1px solid rgba(87,61,33,0.12);
                 padding:18px 40px;text-align:center;">
        <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="text-align:center;">
            <!-- luciérnagas footer -->
            <svg width="120" height="20" viewBox="0 0 120 20" xmlns="http://www.w3.org/2000/svg" style="display:inline-block;margin-bottom:8px;">
              <circle cx="20" cy="10" r="3" fill="#f0c040" opacity="0.7"/>
              <circle cx="20" cy="10" r="7" fill="rgba(240,192,64,0.15)"/>
              <circle cx="60" cy="8"  r="2.5" fill="#f0c040" opacity="0.8"/>
              <circle cx="60" cy="8"  r="6" fill="rgba(240,192,64,0.15)"/>
              <circle cx="100" cy="12" r="3" fill="#f0c040" opacity="0.65"/>
              <circle cx="100" cy="12" r="7" fill="rgba(240,192,64,0.15)"/>
            </svg>
          </td>
        </tr>
        <tr>
          <td style="font-size:11px;color:#a89070;letter-spacing:0.08em;text-align:center;font-family:Arial,sans-serif;">
            © 2026 MEC Solutions &nbsp;·&nbsp; Ingeniería de Software &nbsp;·&nbsp; Facultad de Ciencias · UNAM
          </td>
        </tr>
        </table>
      </td>
    </tr>

  </table>

  <!-- Decoración inferior -->
  <table width="600" cellpadding="0" cellspacing="0" style="max-width:100%;">
  <tr><td style="text-align:center;padding-top:8px;">
    <svg width="600" height="40" viewBox="0 0 600 40" xmlns="http://www.w3.org/2000/svg" style="display:block;max-width:100%;">
      <g fill="#8a9e7a" opacity="0.4">
        <ellipse cx="80"  cy="20" rx="35" ry="12" transform="rotate(20 80 20)"/>
        <ellipse cx="520" cy="18" rx="30" ry="11" transform="rotate(-18 520 18)"/>
        <ellipse cx="300" cy="30" rx="45" ry="10" transform="rotate(5 300 30)"/>
      </g>
      <circle cx="180" cy="15" r="2.5" fill="#f0c040" opacity="0.7"/>
      <circle cx="420" cy="20" r="2"   fill="#f0c040" opacity="0.6"/>
      <circle cx="300" cy="10" r="3"   fill="#f0c040" opacity="0.75"/>
      <circle cx="180" cy="15" r="6"  fill="rgba(240,192,64,0.15)"/>
      <circle cx="300" cy="10" r="7"  fill="rgba(240,192,64,0.15)"/>
    </svg>
  </td></tr>
  </table>

</td></tr>
</table>
</body>
</html>"""


class EmailConfirmacionObserver(Observer):

    def actualizar(self, reservacion):
        nombre   = reservacion.cliente.usuario.get_full_name()
        correo   = reservacion.cliente.usuario.email
        parque   = reservacion.parque.nombre
        direccion= reservacion.parque.direccional
        tipo     = reservacion.get_tipo_visita_display()
        inicio   = reservacion.fecha_inicio.strftime('%d de %B de %Y')
        termino  = reservacion.fecha_termino.strftime('%d de %B de %Y')
        personas = reservacion.num_personas
        pk       = reservacion.pk

        asunto = f'🌿 Reservación confirmada — Festival Luciérnagas 2026 #{pk}'

        texto = (f'Hola {nombre},\n\nTu reservación #{pk} en {parque} fue confirmada.\n'
                 f'Fechas: {inicio} → {termino}\nTipo: {tipo}\nPersonas: {personas}\n\n— MEC Solutions')

        inner = f"""
    <!-- Header -->
    <tr>
      <td style="background:linear-gradient(135deg,#3d2c1a 0%,#573d21 100%);
                 padding:36px 40px 28px;text-align:center;">
        <!-- Hojas decorativas header -->
        <svg width="300" height="30" viewBox="0 0 300 30" xmlns="http://www.w3.org/2000/svg" style="display:block;margin:0 auto 16px;">
          <g fill="#8a9e7a" opacity="0.4">
            <ellipse cx="30"  cy="15" rx="25" ry="9" transform="rotate(-20 30 15)"/>
            <ellipse cx="270" cy="15" rx="25" ry="9" transform="rotate(20 270 15)"/>
            <ellipse cx="150" cy="8"  rx="35" ry="8" transform="rotate(0 150 8)"/>
          </g>
          <circle cx="80"  cy="20" r="2.5" fill="#f0c040" opacity="0.9"/>
          <circle cx="80"  cy="20" r="6"   fill="rgba(240,192,64,0.2)"/>
          <circle cx="220" cy="18" r="2"   fill="#ffd060" opacity="0.8"/>
          <circle cx="220" cy="18" r="5"   fill="rgba(240,192,64,0.15)"/>
          <circle cx="150" cy="24" r="2.5" fill="#f0c040" opacity="0.85"/>
          <circle cx="150" cy="24" r="6"   fill="rgba(240,192,64,0.2)"/>
        </svg>
        <div style="display:inline-block;background:rgba(138,158,122,0.25);
                    border:1px solid rgba(138,158,122,0.4);border-radius:20px;
                    padding:5px 18px;margin-bottom:14px;">
          <span style="font-size:11px;letter-spacing:0.14em;text-transform:uppercase;
                       color:#b5c4a0;font-family:Arial,sans-serif;">✓ Reservación confirmada</span>
        </div>
        <h1 style="margin:0;font-family:Georgia,serif;font-size:26px;font-weight:400;
                   color:#ece0d2;line-height:1.2;">
          ¡Tu lugar en el festival<br>
          <em style="color:#e3a36e;font-style:italic;">está confirmado!</em>
        </h1>
        <p style="margin:12px 0 0;font-size:13px;color:rgba(236,224,210,0.6);font-family:Arial,sans-serif;">
          Hola <strong style="color:#ece0d2;">{nombre}</strong>, te esperamos.
        </p>
      </td>
    </tr>

    <!-- Cuerpo -->
    <tr>
      <td style="padding:28px 40px 8px;">
        <!-- Tabla de datos con estilo orgánico -->
        <table width="100%" cellpadding="0" cellspacing="0"
               style="border:1px solid rgba(87,61,33,0.1);border-radius:2px;overflow:hidden;">
          <tr>
            <td colspan="2" style="background:#3d2c1a;padding:10px 18px;">
              <span style="font-size:10px;letter-spacing:0.16em;text-transform:uppercase;
                           color:rgba(236,224,210,0.6);font-family:Arial,sans-serif;">
                Detalle de la reservación
              </span>
            </td>
          </tr>
          <tr style="border-bottom:1px solid rgba(87,61,33,0.08);">
            <td style="padding:13px 18px;background:rgba(87,61,33,0.03);font-size:10px;
                       letter-spacing:0.1em;text-transform:uppercase;color:#a89070;
                       font-family:Arial,sans-serif;width:38%;">Nº Reservación</td>
            <td style="padding:13px 18px;font-size:14px;color:#e3a36e;font-weight:bold;
                       font-family:Georgia,serif;text-align:right;">#{pk}</td>
          </tr>
          <tr style="border-bottom:1px solid rgba(87,61,33,0.08);">
            <td style="padding:13px 18px;background:rgba(87,61,33,0.03);font-size:10px;
                       letter-spacing:0.1em;text-transform:uppercase;color:#a89070;font-family:Arial,sans-serif;">Parque</td>
            <td style="padding:13px 18px;font-size:13px;color:#3d2c1a;font-family:Georgia,serif;text-align:right;">{parque}</td>
          </tr>
          <tr style="border-bottom:1px solid rgba(87,61,33,0.08);">
            <td style="padding:13px 18px;background:rgba(87,61,33,0.03);font-size:10px;
                       letter-spacing:0.1em;text-transform:uppercase;color:#a89070;font-family:Arial,sans-serif;">Dirección</td>
            <td style="padding:13px 18px;font-size:12px;color:#7a6550;font-family:Arial,sans-serif;text-align:right;">{direccion}</td>
          </tr>
          <tr style="border-bottom:1px solid rgba(87,61,33,0.08);">
            <td style="padding:13px 18px;background:rgba(87,61,33,0.03);font-size:10px;
                       letter-spacing:0.1em;text-transform:uppercase;color:#a89070;font-family:Arial,sans-serif;">Tipo de visita</td>
            <td style="padding:13px 18px;font-size:13px;color:#3d2c1a;font-family:Arial,sans-serif;text-align:right;">{tipo}</td>
          </tr>
          <tr style="border-bottom:1px solid rgba(87,61,33,0.08);">
            <td style="padding:13px 18px;background:rgba(87,61,33,0.03);font-size:10px;
                       letter-spacing:0.1em;text-transform:uppercase;color:#a89070;font-family:Arial,sans-serif;">Fechas</td>
            <td style="padding:13px 18px;font-size:13px;color:#3d2c1a;font-family:Arial,sans-serif;text-align:right;">{inicio}<br>→ {termino}</td>
          </tr>
          <tr>
            <td style="padding:13px 18px;background:rgba(87,61,33,0.03);font-size:10px;
                       letter-spacing:0.1em;text-transform:uppercase;color:#a89070;font-family:Arial,sans-serif;">Personas</td>
            <td style="padding:13px 18px;font-size:13px;color:#3d2c1a;font-family:Arial,sans-serif;text-align:right;">{personas}</td>
          </tr>
        </table>
      </td>
    </tr>

    <!-- Nota recordatorio -->
    <tr>
      <td style="padding:20px 40px 28px;">
        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:rgba(87,61,33,0.04);border:1px solid rgba(87,61,33,0.1);
                      border-radius:2px;">
          <tr>
            <td style="padding:14px 18px;font-size:12px;color:#7a6550;
                       font-family:Arial,sans-serif;line-height:1.7;text-align:center;">
              🌿 Los martes los parques están cerrados por mantenimiento.<br>
              📅 El festival opera de <strong style="color:#3d2c1a;">junio a agosto 2026</strong>.
            </td>
          </tr>
        </table>
      </td>
    </tr>
"""

        html = _html_base(inner)
        _enviar_correo(asunto, texto, html, correo)


class EmailCancelacionObserver(Observer):

    def actualizar(self, reservacion):
        nombre   = reservacion.cliente.usuario.get_full_name()
        correo   = reservacion.cliente.usuario.email
        parque   = reservacion.parque.nombre
        tipo     = reservacion.get_tipo_visita_display()
        inicio   = reservacion.fecha_inicio.strftime('%d de %B de %Y')
        termino  = reservacion.fecha_termino.strftime('%d de %B de %Y')
        personas = reservacion.num_personas
        pk       = reservacion.pk

        asunto = f'🍂 Reservación cancelada — Festival Luciérnagas 2026 #{pk}'

        texto = (f'Hola {nombre},\n\nTu reservación #{pk} en {parque} fue cancelada.\n'
                 f'Fechas: {inicio} → {termino}\n\n— MEC Solutions')

        inner = f"""
    <!-- Header cancelación -->
    <tr>
      <td style="background:linear-gradient(135deg,#573d21 0%,#4a3318 100%);
                 padding:36px 40px 28px;text-align:center;">
        <svg width="300" height="30" viewBox="0 0 300 30" xmlns="http://www.w3.org/2000/svg" style="display:block;margin:0 auto 16px;">
          <g fill="#8a9e7a" opacity="0.35">
            <ellipse cx="30"  cy="15" rx="25" ry="9" transform="rotate(-20 30 15)"/>
            <ellipse cx="270" cy="15" rx="25" ry="9" transform="rotate(20 270 15)"/>
          </g>
          <!-- Hojas más opacas/caídas para cancelación -->
          <g fill="#c8a870" opacity="0.45">
            <ellipse cx="150" cy="20" rx="40" ry="9" transform="rotate(8 150 20)"/>
          </g>
          <circle cx="80"  cy="18" r="2" fill="#f0c040" opacity="0.5"/>
          <circle cx="220" cy="16" r="2" fill="#f0c040" opacity="0.5"/>
        </svg>
        <div style="display:inline-block;background:rgba(227,163,110,0.2);
                    border:1px solid rgba(227,163,110,0.35);border-radius:20px;
                    padding:5px 18px;margin-bottom:14px;">
          <span style="font-size:11px;letter-spacing:0.14em;text-transform:uppercase;
                       color:#e3a36e;font-family:Arial,sans-serif;">Reservación cancelada</span>
        </div>
        <h1 style="margin:0;font-family:Georgia,serif;font-size:26px;font-weight:400;
                   color:#ece0d2;line-height:1.2;">
          Tu reservación<br>
          <em style="color:#e3a36e;font-style:italic;">fue cancelada</em>
        </h1>
        <p style="margin:12px 0 0;font-size:13px;color:rgba(236,224,210,0.6);font-family:Arial,sans-serif;">
          Hola <strong style="color:#ece0d2;">{nombre}</strong>
        </p>
      </td>
    </tr>

    <tr>
      <td style="padding:28px 40px 8px;">
        <table width="100%" cellpadding="0" cellspacing="0"
               style="border:1px solid rgba(87,61,33,0.1);border-radius:2px;overflow:hidden;">
          <tr>
            <td colspan="2" style="background:#573d21;padding:10px 18px;">
              <span style="font-size:10px;letter-spacing:0.16em;text-transform:uppercase;
                           color:rgba(236,224,210,0.6);font-family:Arial,sans-serif;">
                Reservación #{pk} — Cancelada
              </span>
            </td>
          </tr>
          <tr style="border-bottom:1px solid rgba(87,61,33,0.08);">
            <td style="padding:13px 18px;background:rgba(87,61,33,0.03);font-size:10px;
                       letter-spacing:0.1em;text-transform:uppercase;color:#a89070;font-family:Arial,sans-serif;width:38%;">Parque</td>
            <td style="padding:13px 18px;font-size:13px;color:#3d2c1a;font-family:Georgia,serif;text-align:right;">{parque}</td>
          </tr>
          <tr style="border-bottom:1px solid rgba(87,61,33,0.08);">
            <td style="padding:13px 18px;background:rgba(87,61,33,0.03);font-size:10px;
                       letter-spacing:0.1em;text-transform:uppercase;color:#a89070;font-family:Arial,sans-serif;">Tipo</td>
            <td style="padding:13px 18px;font-size:13px;color:#3d2c1a;font-family:Arial,sans-serif;text-align:right;">{tipo}</td>
          </tr>
          <tr style="border-bottom:1px solid rgba(87,61,33,0.08);">
            <td style="padding:13px 18px;background:rgba(87,61,33,0.03);font-size:10px;
                       letter-spacing:0.1em;text-transform:uppercase;color:#a89070;font-family:Arial,sans-serif;">Fechas</td>
            <td style="padding:13px 18px;font-size:13px;color:#3d2c1a;font-family:Arial,sans-serif;text-align:right;">{inicio}<br>→ {termino}</td>
          </tr>
          <tr>
            <td style="padding:13px 18px;background:rgba(87,61,33,0.03);font-size:10px;
                       letter-spacing:0.1em;text-transform:uppercase;color:#a89070;font-family:Arial,sans-serif;">Personas</td>
            <td style="padding:13px 18px;font-size:13px;color:#3d2c1a;font-family:Arial,sans-serif;text-align:right;">{personas}</td>
          </tr>
        </table>
      </td>
    </tr>

    <tr>
      <td style="padding:20px 40px 28px;">
        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:rgba(87,61,33,0.04);border:1px solid rgba(87,61,33,0.1);border-radius:2px;">
          <tr>
            <td style="padding:14px 18px;font-size:12px;color:#7a6550;
                       font-family:Arial,sans-serif;line-height:1.7;text-align:center;">
              🌿 ¿Fue un error? Puedes realizar una nueva reservación desde el sistema.<br>
              Los espacios liberados quedan disponibles para otros visitantes.
            </td>
          </tr>
        </table>
      </td>
    </tr>
"""

        html = _html_base(inner, color_header='#573d21')
        _enviar_correo(asunto, texto, html, correo)


class ReservacionSubject:
    def __init__(self):
        self._observers = []

    def agregar_observer(self, observer: Observer):
        self._observers.append(observer)

    def notificar(self, reservacion):
        for observer in self._observers:
            observer.actualizar(reservacion)
