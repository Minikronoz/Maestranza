from django.urls import path
from . import views
from .views import ProductoListView, ProductoCreateView, ProductoUpdateView, ProductoDeleteView,MovimientoInventarioListView, MovimientoInventarioCreateView, AlertaStockBajoListView, ProductosVencimientoListView, ProductoDetailView, PrecioCompraCreateView

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('list/', ProductoListView.as_view(), name='producto-list'),
    path('nuevo/', ProductoCreateView.as_view(), name='producto-nuevo'),
    path('editar/<int:pk>/', ProductoUpdateView.as_view(), name='producto-editar'),
    path('eliminar/<int:pk>/', ProductoDeleteView.as_view(), name='producto-eliminar'),
    path('movimientos/', MovimientoInventarioListView.as_view(), name='movimiento-list'),
    path('movimientos/nuevo/', MovimientoInventarioCreateView.as_view(), name='movimiento-nuevo'),
    path('alertas/stock-bajo/', AlertaStockBajoListView.as_view(), name='alerta-stock-bajo'),
    path('productos/vencimiento/', ProductosVencimientoListView.as_view(), name='productos-vencimiento'),
    path('producto/<str:codigo>/', ProductoDetailView.as_view(), name='producto-detalle'),
    path('producto/<str:codigo>/nuevo-precio/', PrecioCompraCreateView.as_view(), name='precio-compra-nuevo'),
]

