import operator
from functools import reduce

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from django.shortcuts import render

from . import pages_utils as utils
import website.tools as tools
import website.models as models


# Definition of views:
def index(request):
    all_news = utils.get_news_posts(3)
    all_journal = models.JournalImage.objects.filter(display=True)
    keywords = [item for blog in all_news for item in blog.keywords.split(",")]

    context = {'latest_blog_posts': all_news,
               'all_journal': all_journal,
               'meta': tools.get_meta_tags_dict(keywords=keywords),
               }
    return render(request, 'website/index.html', context)


def page(request, position_id):
    context = {}
    section = utils.get_website_section(position_id)
    if not section:
        raise Http404("Page does not exist")

    context['section'] = section
    page_title = "DIPY - %s" % (section.title,)
    context['meta'] = tools.get_meta_tags_dict(title=page_title)
    return render(request, 'website/section_page.html', context)


def news_page(request):
    all_highlights = utils.get_highlight(3)
    all_events = models.EventPost.objects.exclude(end_date__lt=timezone.now())
    all_news = utils.get_news_posts()
    page = request.GET.get('page', 1)

    paginator = Paginator(all_news, 3)
    try:
        current_news = paginator.page(page)
    except PageNotAnInteger:
        current_news = paginator.page(1)
    except EmptyPage:
        current_news = paginator.page(paginator.num_pages)

    context = {'all_news': current_news,
               'all_events': all_events,
               'all_highlights': all_highlights,
               'meta': tools.get_meta_tags_dict(title="DIPY - News / Events"),
               }
    return render(request, 'website/news.html', context)


def blog_post(request, slug):
    blog_post = models.BlogPost.objects.get(slug=slug)
    keywords = [item for item in blog_post.keywords.split(",")]
    context = {'blog_post': blog_post,
               'meta': tools.get_meta_tags_dict(title=slug, keywords=keywords),
               }
    return render(request, 'website/blog_post.html', context)


def event_post(request, slug):
    event_posted = models.EventPost.objects.get(slug=slug)
    keywords = [item for item in event_posted.keywords.split(",")]
    context = {'event_post': event_posted,
               'meta': tools.get_meta_tags_dict(title=slug, keywords=keywords),
               }
    return render(request, 'website/event_post.html', context)


def careers_page(request):
    all_careers = models.CareerModel.objects.first()
    context = {'all_careers': all_careers}

    return render(request, 'website/careers.html', context)


def research(request):
    all_research = models.Research.objects.filter(show_in_page=True).order_by('position')
    context = {'all_research': all_research,
               'meta': tools.get_meta_tags_dict(title="DIPY - Research"),
               }
    return render(request, 'website/research.html', context)


def publications(request):
    all_publications = models.Publication.objects.all()
    if request.method == 'GET':
        if 'search' in request.GET:
            search_words_list = request.GET['search-words']
            search_words_list = search_words_list.split()
            all_publications = []
            if search_words_list:
                all_publications = models.Publication.objects.filter(
                    reduce(operator.and_, (Q(title__icontains=q)
                                           for q in search_words_list)) |
                    reduce(operator.and_, (Q(abstract__icontains=q)
                                           for q in search_words_list)) |
                    reduce(operator.and_, (Q(bibtex__icontains=q)
                                           for q in search_words_list)) |
                    reduce(operator.and_, (Q(author__icontains=q)
                                           for q in search_words_list))
                    )
        if 'order-by' in request.GET:
            print('order-by: ')
            print(request.GET['select-item-one'])
            # Todo: implement order-by

    context = {'all_publications': all_publications,
               'meta': tools.get_meta_tags_dict(title="DIPY - Publications"),
               }
    return render(request, 'website/publications.html', context)


def teaching(request):
    context = {'all_courses': models.Course.objects.all(),
               'meta': tools.get_meta_tags_dict(title="DIPY - Teaching"),
               }
    return render(request, 'website/teaching.html', context)


def software(request):
    context = {'all_software': models.Software.objects.all(),
               'meta': tools.get_meta_tags_dict(title="DIPY - Software"),
               }
    return render(request, 'website/software.html', context)


def people(request):
    director_profiles = models.Profile.objects.filter(status=models.Profile.STATUS_CHOICE[5][0]).order_by('rank')
    team_profiles = models.Profile.objects.filter(status=models.Profile.STATUS_CHOICE[0][0]).order_by('rank')
    collaborator_profiles = models.Profile.objects.filter(status=models.Profile.STATUS_CHOICE[2][0]).order_by('rank')
    alumni_profiles = models.Profile.objects.filter(status=models.Profile.STATUS_CHOICE[4][0]).order_by('rank')
    context = {'director_profiles': director_profiles,
               'team_profiles': team_profiles,
               'collaborator_profiles': collaborator_profiles,
               'alumni_profiles': alumni_profiles,
               'meta': tools.get_meta_tags_dict(),
               }
    return render(request, 'website/people.html', context)


def people_profile(request, username):
    user = models.User.objects.get(username=username)
    profile = models.Profile.objects.get(user=user)
    my_blog_posts = models.BlogPost.objects.filter(authors=profile,
                                                   show_in_my_blog=True)
    context = {'profile': profile,
               'my_blog_posts': my_blog_posts,
               'meta': tools.get_meta_tags_dict(),
               }
    return render(request, 'website/people_profile.html', context)


def honeycomb(request):
    context = {'all_youtube_videos': tools.get_youtube_videos('UCHnEuCRDGFOR5cfEo0nD3pw', 100),
               'meta': tools.get_meta_tags_dict(title="DIPY - Gallery"),
               }
    return render(request, 'website/honeycomb.html', context)


@login_required
@tools.github_permission_required
def dashboard(request):
    context = {'meta': tools.get_meta_tags_dict(),
               }
    return render(request, 'website/dashboard.html', context)


def dashboard_login(request):
    next_url = request.GET.get('next')
    context = {'next': next_url,
               'meta': tools.get_meta_tags_dict(),
               }
    return render(request, 'website/dashboard_login.html', context)


def access_denied(request):
    context = {'meta': tools.get_meta_tags_dict(title="DIPY - Access Deny"),
               }
    return render(request, 'website/access_denied.html', context)


def custom404(request):
    context = {'meta': tools.get_meta_tags_dict(title="DIPY - 404 Page Not Found"),
               }
    return render(request, 'website/error_pages/404.html', context, status=400)


def custom500(request):
    context = {'meta': tools.get_meta_tags_dict(title="DIPY - 500 Error Occured"),
               }
    return render(request, 'website/error_pages/404.html', context, status=400)
