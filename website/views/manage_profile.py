
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from website.tools import github_permission_required
from website.forms import EditProfileForm, UserForm
from website.models import Profile


@login_required
@github_permission_required
def edit_profile(request):
    try:
        Profile.objects.get(user=request.user)
    except Exception:
        raise Http404("Profile does not exist. Contact Admin")

    js_script = """<script>var simplemde = new SimpleMDE({ element: $("#id_profile_page_markdown")[0], forceSync:true }); </script>"""
    context = {'js_script': js_script}
    if request.method == 'POST':
        submitted_user_form = UserForm(request.POST, instance=request.user)
        submitted_profile_form = EditProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if submitted_profile_form.is_valid() and submitted_user_form.is_valid():
            submitted_user_form.save()
            submitted_profile_form.save()
            return redirect(reverse('dashboard'))
        else:
            context['user_form'] = submitted_user_form
            context['profile_form'] = submitted_profile_form
            return render(request, 'website/editprofile.html', context)

    user_form = UserForm(instance=request.user)
    profile_form = EditProfileForm(instance=request.user.profile)
    context['user_form'] = user_form
    context['profile_form'] = profile_form
    return render(request, 'website/editprofile.html', context)
