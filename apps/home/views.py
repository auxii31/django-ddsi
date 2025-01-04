# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from django.db.models import Sum

# Modelos DDSI
from .models import Ingreso  
from .models import Gasto 
from .forms import IngresoForm, GastoForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Campana


def contabilidad_view(request):
      # Calcular la suma de los ingresos
    total_ingresos = Ingreso.objects.all().aggregate(total=Sum('monto_ingreso'))['total'] or 0

    # Calcular la suma de los gastos
    total_gastos = Gasto.objects.all().aggregate(total=Sum('monto_gasto'))['total'] or 0

    # Calcular el balance neto
    balance_neto = total_ingresos - total_gastos

    # Pasar todo al contexto
    return render(request, 'home/contabilidad.html', {
        'total_ingresos': total_ingresos,
        'total_gastos': total_gastos,
        'balance_neto': balance_neto,
    })
    
@login_required(login_url="/login/")
def ingresos_view(request):
    # BUSCAR INGRESOS
    search_query = request.GET.get('search', '')
    if search_query:
        ingresos = Ingreso.objects.filter(id_ingreso__icontains=search_query)
    else:
        ingresos = Ingreso.objects.all()

    context = {
        'ingresos': ingresos,
    }

    # Manejo de formularios para anadir ingresos y gastos
    if request.method == 'POST':
        if 'add_ingreso' in request.POST:  # Si se pulsa el botón de Ingreso
            ingreso_form = IngresoForm(request.POST)
            if ingreso_form.is_valid():
                ingreso_form.save()
                return redirect('ingresos')  # Redirige a la misma página
        elif 'edit_ingreso' in request.POST:  # Si se pulsa el botón de Editar
            # Obtener el id del ingreso desde el formulario POST
            ingreso_id = request.POST.get('ingreso_id')  # El ID viene con el formulario
            ingreso = get_object_or_404(Ingreso, id_ingreso=ingreso_id)
            ingreso_form = IngresoForm(request.POST, instance=ingreso)
            if ingreso_form.is_valid():
                ingreso_form.save()
                return redirect('ingresos')  # Redirige a la misma página
    else:
        ingreso_form = IngresoForm()

    # Si estamos editando un ingreso, obtenemos ese ingreso
    ingreso_id = request.GET.get('edit', None)
    if ingreso_id:
        ingreso = get_object_or_404(Ingreso, id_ingreso=ingreso_id)
        ingreso_form = IngresoForm(instance=ingreso)

    context['ingreso_form'] = ingreso_form

    html_template = loader.get_template('home/ingresos.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def gastos_view(request):
    # BUSCAR GASTOS
    search_query = request.GET.get('search', '')
    if search_query:
        gastos = Gasto.objects.filter(id_gasto__icontains=search_query)
    else:
        gastos = Gasto.objects.all()

    context = {
        'gastos': gastos,
    }

    # Manejo de formularios para anadir gastos y gastos
    if request.method == 'POST':
        if 'add_gasto' in request.POST:  # Si se pulsa el botón de Gasto
            gasto_form = GastoForm(request.POST)
            if gasto_form.is_valid():
                gasto_form.save()
                return redirect('gastos')  # Redirige a la misma página
        elif 'edit_gasto' in request.POST:  # Si se pulsa el botón de Editar
            # Obtener el id del gasto desde el formulario POST
            gasto_id = request.POST.get('gasto_id')  # El ID viene con el formulario
            gasto = get_object_or_404(Gasto, id_gasto=gasto_id)
            gasto_form = GastoForm(request.POST, instance=gasto)
            if gasto_form.is_valid():
                gasto_form.save()
                return redirect('gastos')  # Redirige a la misma página
    else:
        gasto_form = GastoForm()

    # Si estamos editando un gasto, obtenemos ese gasto
    gasto_id = request.GET.get('edit', None)
    if gasto_id:
        gasto = get_object_or_404(Gasto, id_gasto=gasto_id)
        gasto_form = GastoForm(instance=gasto)

    context['gasto_form'] = gasto_form

    html_template = loader.get_template('home/gastos.html')
    return HttpResponse(html_template.render(context, request))



@login_required(login_url="/login/")
def eliminar_ingreso(request, ingreso_id):
    # Asegurarse de que la solicitud sea POST
    if request.method == 'POST':
        ingreso = get_object_or_404(Ingreso, id_ingreso=ingreso_id)
        ingreso.delete()  # Elimina el ingreso de la base de datos

    return redirect('contabilidad')  # Redirige a la vista de contabilidad

@login_required(login_url="/login/")
def eliminar_gasto(request, gasto_id):
    # Asegurarse de que la solicitud sea POST
    if request.method == 'POST':
        gasto = get_object_or_404(Gasto, id_gasto=gasto_id)
        gasto.delete()  # Elimina el ingreso de la base de datos

    return redirect('contabilidad')  # Redirige a la vista de contabilidad

@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
                        

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
    
    

# Vista para listar las campañas
@login_required(login_url="/login/")
def listar_campanas(request):
    # Obtener todas las campañas o filtrar según el estado
    campanas = Campana.objects.all()  # O filtrar, por ejemplo, .filter(estado='activa')
    return render(request, 'home/listar_campanas.html', {'campanas': campanas})



# Vista para dar de alta una campaña (crear una nueva)
@login_required(login_url="/login/")
def dar_de_alta_campana(request):
    if request.method == 'POST':
        form = CampanaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaña creada con éxito')
            return redirect('listar_campanas')  # Redirige a la lista de campañas
    else:
        form = CampanaForm()
    return render(request, 'home/dar_de_alta_campana.html', {'form': form})

'''
# Vista para modificar una campaña existente
@login_required(login_url="/login/")
def modificar_campana(request, campaign_id):
    campana = get_object_or_404(Campana, id_campana=campaign_id)

    # Restricciones semánticas: no permitir cambios en ciertos campos si la campaña está activa
    if campana.estado == 'activa' and request.method == 'POST':
        # Si la campaña está activa, no permitir cambios en ciertos campos (como el tipo de campaña)
        form = CampanaForm(request.POST, instance=campana)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaña modificada con éxito')
            return redirect('listar_campanas')
    elif request.method == 'POST':
        form = CampanaForm(request.POST, instance=campana)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaña modificada con éxito')
            return redirect('listar_campanas')
    else:
        form = CampanaForm(instance=campana)

    return render(request, 'home/modificar_campana.html', {'form': form, 'campana': campana})


# Vista para eliminar una campaña
@login_required(login_url="/login/")
def eliminar_campana(request, campaign_id):
    if request.method == 'POST':
        campana = get_object_or_404(Campana, id_campana=campaign_id)
        campana.delete()  # Elimina la campaña de la base de datos
        messages.success(request, 'Campaña eliminada con éxito')
    return redirect('listar_campanas')  # Redirige a la lista de campañas


# Resto de vistas

@login_required(login_url="/login/")
def contabilidad_view(request):
    total_ingresos = Ingreso.objects.all().aggregate(total=Sum('monto_ingreso'))['total'] or 0
    total_gastos = Gasto.objects.all().aggregate(total=Sum('monto_gasto'))['total'] or 0
    balance_neto = total_ingresos - total_gastos
    return render(request, 'home/contabilidad.html', {
        'total_ingresos': total_ingresos,
        'total_gastos': total_gastos,
        'balance_neto': balance_neto,
    })


@login_required(login_url="/login/")
def ingresos_view(request):
    search_query = request.GET.get('search', '')
    if search_query:
        ingresos = Ingreso.objects.filter(id_ingreso__icontains=search_query)
    else:
        ingresos = Ingreso.objects.all()

    context = {'ingresos': ingresos}

    if request.method == 'POST':
        if 'add_ingreso' in request.POST:
            ingreso_form = IngresoForm(request.POST)
            if ingreso_form.is_valid():
                ingreso_form.save()
                return redirect('ingresos')
        elif 'edit_ingreso' in request.POST:
            ingreso_id = request.POST.get('ingreso_id')
            ingreso = get_object_or_404(Ingreso, id_ingreso=ingreso_id)
            ingreso_form = IngresoForm(request.POST, instance=ingreso)
            if ingreso_form.is_valid():
                ingreso_form.save()
                return redirect('ingresos')
    else:
        ingreso_form = IngresoForm()

    ingreso_id = request.GET.get('edit', None)
    if ingreso_id:
        ingreso = get_object_or_404(Ingreso, id_ingreso=ingreso_id)
        ingreso_form = IngresoForm(instance=ingreso)

    context['ingreso_form'] = ingreso_form
    html_template = loader.get_template('home/ingresos.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def gastos_view(request):
    search_query = request.GET.get('search', '')
    if search_query:
        gastos = Gasto.objects.filter(id_gasto__icontains=search_query)
    else:
        gastos = Gasto.objects.all()

    context = {'gastos': gastos}

    if request.method == 'POST':
        if 'add_gasto' in request.POST:
            gasto_form = GastoForm(request.POST)
            if gasto_form.is_valid():
                gasto_form.save()
                return redirect('gastos')
        elif 'edit_gasto' in request.POST:
            gasto_id = request.POST.get('gasto_id')
            gasto = get_object_or_404(Gasto, id_gasto=gasto_id)
            gasto_form = GastoForm(request.POST, instance=gasto)
            if gasto_form.is_valid():
                gasto_form.save()
                return redirect('gastos')
    else:
        gasto_form = GastoForm()

    gasto_id = request.GET.get('edit', None)
    if gasto_id:
        gasto = get_object_or_404(Gasto, id_gasto=gasto_id)
        gasto_form = GastoForm(instance=gasto)

    context['gasto_form'] = gasto_form
    html_template = loader.get_template('home/gastos.html')
    return HttpResponse(html_template.render(context, request))
'''