"""
Modelos de usuarios — MEC Solutions
Diagrama de clases: «abstract» Usuario → Cliente, Administrador
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UsuarioManager(BaseUserManager):
    """Manager personalizado que usa email como identificador en lugar de username."""

    def create_user(self, email, nombre, apellido, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio.')
        email = self.normalize_email(email)
        user  = self.model(email=email, nombre=nombre, apellido=apellido, **extra_fields)
        user.set_password(password)   # Aplica hashing automático (RNF04)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre, apellido, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, nombre, apellido, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Clase base del sistema de autenticación (RF01.1, RF01.2).
    La contraseña se almacena hasheada por Django (RNF04).
    """

    nombre   = models.CharField('Nombre', max_length=100)
    apellido = models.CharField('Apellido(s)', max_length=150)
    email    = models.EmailField('Correo electrónico', unique=True)

    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)   # True → acceso al panel de admin
    fecha_registro = models.DateTimeField(auto_now_add=True)

    objects = UsuarioManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.nombre} {self.apellido} <{self.email}>'

    def get_full_name(self):
        return f'{self.nombre} {self.apellido}'


class Cliente(models.Model):
    """
    Perfil de cliente asociado 1:1 con Usuario.
    Se crea automáticamente al registrarse (CU-03).
    """

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='cliente',
        primary_key=True,
    )

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f'Cliente: {self.usuario.get_full_name()}'

    def ver_reservaciones(self):
        """Devuelve solo las reservaciones activas del cliente (RF01.4)."""
        return self.reservaciones.filter(estado='activa')


class Administrador(models.Model):
    """
    Perfil de administrador.  Se crea manualmente desde el panel de Django Admin.
    Un administrador siempre tiene is_staff=True en su Usuario asociado.
    """

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='administrador',
        primary_key=True,
    )

    class Meta:
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'

    def __str__(self):
        return f'Admin: {self.usuario.get_full_name()}'
