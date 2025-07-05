from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView,DetailView
from datetime import timedelta
from .models import Categoria, Producto, MovimientoInventario, PrecioCompra
from .forms import ProductoForm, UserRegisterForm, PrecioCompraForm, ReporteInventarioForm
from .decorators import GroupRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F,Q
from django.utils import timezone
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render
import datetime
import openpyxl


class ProductoListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    login_url = 'login'
    group_required = ['Administrador', 'Gestor de Inventario', 'Encargado de Logística']
    model = Producto
    template_name = 'inventario/producto_list.html'
    context_object_name = 'productos'

    
    

class ProductoCreateView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    login_url = 'login'
    group_required = ['Administrador', 'Gestor de Inventario']
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto_form.html'
    success_url = reverse_lazy('producto-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Si no es admin, ocultamos el campo nuevas_categorias
        if not self.request.user.groups.filter(name='Administrador').exists():
            form.fields.pop('nuevas_categorias')
        return form

    def form_valid(self, form):
        # Guardar el producto sin M2M para obtener ID
        self.object = form.save(commit=False)
        self.object.save()

        # Guardar las categorías seleccionadas en el formulario
        form.save_m2m()

        # Si es admin, crear y asignar nuevas categorías
        if self.request.user.groups.filter(name='Administrador').exists():
            nuevas_cats = form.cleaned_data.get('nuevas_categorias')
            if nuevas_cats:
                lista_cats = [c.strip() for c in nuevas_cats.split(',') if c.strip()]
                for nombre_cat in lista_cats:
                    cat_obj, created = Categoria.objects.get_or_create(nombre=nombre_cat)
                    self.object.categorias.add(cat_obj)

        return super().form_valid(form)



class ProductoUpdateView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    login_url = 'login'
    group_required = ['Administrador', 'Gestor de Inventario']
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto_form.html'
    success_url = reverse_lazy('producto-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Si no es admin, ocultamos el campo nuevas_categorias
        if not self.request.user.groups.filter(name='Administrador').exists():
            form.fields.pop('nuevas_categorias')
        return form

    def form_valid(self, form):
        # Guardar el producto sin M2M para tener ID
        self.object = form.save(commit=False)
        self.object.save()

        # Guardar categorías seleccionadas
        form.save_m2m()

        # Si es admin, procesar nuevas categorías y asignarlas
        if self.request.user.groups.filter(name='Administrador').exists():
            nuevas_cats = form.cleaned_data.get('nuevas_categorias')
            if nuevas_cats:
                lista_cats = [c.strip() for c in nuevas_cats.split(',') if c.strip()]
                for nombre_cat in lista_cats:
                    cat_obj, created = Categoria.objects.get_or_create(nombre=nombre_cat)
                    self.object.categorias.add(cat_obj)

        return super().form_valid(form)


    
    
class ProductoDeleteView(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    login_url = 'login'
    group_required = ['Administrador']
    model = Producto
    template_name = 'inventario/producto_confirm_delete.html'
    success_url = reverse_lazy('producto-list')


# Registro de usuarios con asignación de grupo
class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'inventario/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        group = form.cleaned_data['group']
        user.groups.add(group)
        return response


# Página de inicio
class HomeView(TemplateView):
    template_name = 'inventario/home.html'


# Vista para listar movimientos (usuarios autorizados)
class MovimientoInventarioListView(LoginRequiredMixin, ListView):
    model = MovimientoInventario
    template_name = 'inventario/movimiento_list.html'
    context_object_name = 'movimientos'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        allowed_groups = [
            'Administrador', 'Gestor de Inventario', 'Encargado de Logística',
            'Auditor de Inventario', 'Comprador', 'Jefe de Producción'
        ]
        if any(user.groups.filter(name=grp).exists() for grp in allowed_groups):
            return MovimientoInventario.objects.all().order_by('-fecha')
        else:
            return MovimientoInventario.objects.none()


# Vista para crear movimientos (solo grupos autorizados)
class MovimientoInventarioCreateView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = MovimientoInventario
    fields = ['producto', 'tipo_movimiento', 'cantidad', 'proyecto', 'observaciones']
    template_name = 'inventario/movimiento_form.html'
    success_url = reverse_lazy('movimiento-list')
    group_required = ['Administrador', 'Gestor de Inventario', 'Encargado de Logística']

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        producto = form.cleaned_data['producto']
        cantidad = form.cleaned_data['cantidad']
        tipo = form.cleaned_data['tipo_movimiento']

        if tipo in ['ENTRADA', 'TRANSFERENCIA']:
            producto.cantidad += cantidad
        elif tipo in ['SALIDA', 'USO_PROYECTO']:
            if producto.cantidad < cantidad:
                form.add_error('cantidad', 'Cantidad insuficiente en inventario.')
                return self.form_invalid(form)
            producto.cantidad -= cantidad
        producto.save()
        return super().form_valid(form)


# Vista para alertas de stock bajo
class AlertaStockBajoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = 'inventario/alerta_stock_bajo.html'
    context_object_name = 'productos_alerta'

    def get_queryset(self):
        return Producto.objects.filter(cantidad__lte=F('umbral_stock_bajo')).order_by('cantidad')


#Alerta de Proximo Vencimiento

class ProductosVencimientoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = 'inventario/productos_vencimiento.html'
    context_object_name = 'productos_vencimiento'

    def get_queryset(self):
        hoy = timezone.now().date()
        fecha_alerta = hoy + timedelta(days=30)  # Avisar 30 días antes
        return Producto.objects.filter(
            Q(fecha_vencimiento__lte=fecha_alerta) & Q(fecha_vencimiento__isnull=False)
        ).order_by('fecha_vencimiento')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        return context
    
#agregar precio de compra
class PrecioCompraCreateView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = PrecioCompra
    form_class = PrecioCompraForm
    template_name = 'inventario/precio_compra_form.html'
    group_required = ['Administrador', 'Gestor de Inventario']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['producto'] = self.producto
        return context

    def dispatch(self, request, *args, **kwargs):
        # Obtener el producto por codigo para usar en todo el proceso
        self.producto = Producto.objects.get(codigo=kwargs['codigo'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['producto'] = self.producto.pk
        return initial

    def form_valid(self, form):
        form.instance.producto = self.producto
        return super().form_valid(form)

    def get_success_url(self):
        # Redirigir al detalle del producto usando codigo
        return reverse_lazy('producto-detalle', kwargs={'codigo': self.producto.codigo})
    
    

#mostrar historial de precios de compra en detalle del producto
class ProductoDetailView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = Producto
    template_name = 'inventario/producto_detail.html'
    context_object_name = 'producto'
    slug_field = 'codigo'  # Buscar por campo codigo
    slug_url_kwarg = 'codigo'
    group_required = ['Administrador', 'Gestor de Inventario', 'Encargado de Logística']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['precios_compra'] = self.object.precios_compra.order_by('-fecha_compra')
        return context
    

#vista manejar formulario y generar excel
class ReporteInventarioView(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ['Administrador', 'Gestor de Inventario']

    def get(self, request):
        form = ReporteInventarioForm()
        return render(request, 'inventario/reporte_inventario.html', {'form': form})

    def post(self, request):
        form = ReporteInventarioForm(request.POST)
        if form.is_valid():
            productos = Producto.objects.all()

            fecha_inicio = form.cleaned_data.get('fecha_inicio')
            fecha_fin = form.cleaned_data.get('fecha_fin')
            categorias = form.cleaned_data.get('categorias')

            if fecha_inicio:
                productos = productos.filter(fecha_vencimiento__gte=fecha_inicio)
            if fecha_fin:
                productos = productos.filter(fecha_vencimiento__lte=fecha_fin)
            if categorias and categorias.exists():
                productos = productos.filter(categorias__in=categorias).distinct()

            # Crear Excel
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Reporte Inventario"

            # Encabezados
            headers = ['Código', 'Nombre', 'Cantidad', 'Ubicación', 'Fecha Vencimiento', 'Categorías']
            ws.append(headers)

            for p in productos:
                categorias_str = ", ".join([c.nombre for c in p.categorias.all()])
                fecha_ven = p.fecha_vencimiento.strftime("%d/%m/%Y") if p.fecha_vencimiento else ""
                row = [p.codigo, p.nombre, p.cantidad, p.ubicacion, fecha_ven, categorias_str]
                ws.append(row)

            # Preparar respuesta para descargar
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
            filename = f"reporte_inventario_{datetime.date.today()}.xlsx"
            response['Content-Disposition'] = f'attachment; filename={filename}'
            wb.save(response)
            return response

        return render(request, 'inventario/reporte_inventario.html', {'form': form})