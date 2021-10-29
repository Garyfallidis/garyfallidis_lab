from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from website.tools import github_permission_required
from website.forms import AddEditCarouselImageForm
from website.models import CarouselImage


@login_required
@github_permission_required
def dashboard_carousel(request):
    all_carousel_images = CarouselImage.objects.all()
    context = {'all_carousel_images': all_carousel_images}
    return render(request, 'website/dashboard_carousel.html', context)


@login_required
@github_permission_required
def add_carousel_image(request):
    context = {}
    if request.method == 'POST':
        submitted_form = AddEditCarouselImageForm(request.POST)
        if submitted_form.is_valid():
            submitted_form.save()
            return redirect(reverse('dashboard_carousel'))
        else:
            context['form'] = submitted_form
            return render(request, 'website/addeditcarousel.html', context)

    form = AddEditCarouselImageForm()
    context['form'] = form
    return render(request, 'website/addeditcarousel.html', context)


@login_required
@github_permission_required
def edit_carousel_image(request, carousel_image_id):
    try:
        carousel_image = CarouselImage.objects.get(
            id=carousel_image_id)
    except:
        raise Http404("Website Section does not exist")

    context = {}
    if request.method == 'POST':
        submitted_form = AddEditCarouselImageForm(request.POST,
                                                  instance=carousel_image)
        if submitted_form.is_valid():
            submitted_form.save()
            return redirect(reverse('dashboard_carousel'))
        else:
            context['form'] = submitted_form
            return render(request, 'website/addeditcarousel.html', context)

    form = AddEditCarouselImageForm(instance=carousel_image)
    context['form'] = form
    return render(request, 'website/addeditcarousel.html', context)


@login_required
@github_permission_required
def delete_carousel_image(request, carousel_image_id):
    try:
        n = CarouselImage.objects.get(id=carousel_image_id)
    except:
        raise Http404("Carousel Image does not exist")
    n.delete()
    return redirect(reverse('dashboard_carousel'))
