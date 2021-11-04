"""More information: https://rahmonov.me/posts/introduction-to-python-social-auth/ """
from django.conf import settings
from django.shortcuts import redirect

from .tools import has_commit_permission
from .models import Profile

USER_FIELDS = ['username', 'email']


def create_user(strategy, backend, details, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    if backend.name != 'github':
        return redirect('website:access_denied')

    try:
        access_token = kwargs.get('response', {}).get('access_token', '')
    except Exception:
        access_token = ''

    has_permission = has_commit_permission(
        access_token, settings.REPOSITORY_NAME)

    if not has_permission:
        return redirect('website:access_denied')

    fields = dict((name, kwargs.get(name, details.get(name)))
                  for name in backend.setting('USER_FIELDS', USER_FIELDS))
    if not fields:
        return

    return {'is_new': True,
            'user': strategy.create_user(**fields)
            }


def create_profile(strategy, backend, details, user=None, *args, **kwargs):
    profile = Profile.objects.filter(user=user)
    if not profile.exists():
        prof = Profile.objects.create(user=user, profile_page_markdown="")
        prof.save()
