from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre



class Producto(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    cantidad = models.PositiveIntegerField(default=0)
    ubicacion = models.CharField(max_length=100)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    umbral_stock_bajo = models.PositiveIntegerField(default=5)  # umbral para alerta
    categorias = models.ManyToManyField(Categoria, blank=True)
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"




class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('USO_PROYECTO', 'Uso en Proyecto'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO_CHOICES)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    proyecto = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.producto.nombre} - {self.cantidad} unidades"
    

#historial de precios de compra
class PrecioCompra(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='precios_compra')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_compra = models.DateField()

    def __str__(self):
        return f"{self.producto.nombre} - ${self.precio} ({self.fecha_compra})"
