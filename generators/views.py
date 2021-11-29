from django.shortcuts import render, redirect, get_object_or_404
from .forms import GeneratorForm
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import Generator

# Create your views here.


def config_generator(request, success=None):
    if success:
        context = {'success': success}
    else:
        context = {}
    gens = Generator.objects.all()
    context['generators'] = gens
    return render(request, 'generators/generator_config.html', context)


def create_generator(request):
    if request.method == 'POST':
        form = GeneratorForm(request.POST)
        if form.is_valid():
            form.save()
            context = {
                'success': 'Генератор был успешно добавлен!',
            }
            return HttpResponseRedirect(reverse('generators:generator-config-success', kwargs=context))
    else:
        form = GeneratorForm()
    return render(request, 'generators/generator_create.html', {'form': form})


def detail_generator(request, use_area):
    obj = get_object_or_404(Generator, use_area=use_area)
    objForm = GeneratorForm(instance=obj)
    context = {
        'instance': obj.use_area,
        'form': objForm,
    }
    return render(request, 'generators/generator_detail.html', context)


def delete_generator(request, use_area):
    obj = get_object_or_404(Generator, use_area=use_area)
    obj.delete()
    context = {
        'success': 'Генератор был успешно удален!',
    }
    return HttpResponseRedirect(reverse('generators:generator-config-success', kwargs=context))


def save_generator(request):
    context = {}
    if request.method == 'POST':
        generator_form = GeneratorForm(request.POST, instance=Generator.objects.get(pk=request.POST['use_area']))
        if generator_form.is_valid():
            generator_form.save()
            context = {
                'success': 'Генератор был успешно отредактирован!',
            }
            return HttpResponseRedirect(reverse('generators:generator-config-success', kwargs=context))
    return render(request, 'generators/generator_detail.html', context)


def ajax_generate(request):
    use_area = request.GET['use_area']
    if use_area:
        new_obj = Generator.set_new(use_area)
        return HttpResponse(str(new_obj))
    else:
        return HttpResponse('')
