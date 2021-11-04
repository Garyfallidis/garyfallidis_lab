
import bleach
import datetime
import markdown

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse

# markdown allowed tags that are not filtered by bleach

allowed_html_tags = bleach.ALLOWED_TAGS + ['p', 'pre', 'table', 'img',
                                           'h1', 'h2', 'h3', 'h4', 'h5',
                                           'h6', 'b', 'i', 'strong', 'em',
                                           'tt', 'br', 'blockquote',
                                           'code', 'ul', 'ol', 'li',
                                           'dd', 'dt', 'a', 'tr', 'td',
                                           'div', 'span', 'hr']

allowed_attrs = ['href', 'class', 'rel', 'alt', 'class', 'src', 'id']

# Create your models here.


class WebsiteSection(models.Model):
    title = models.CharField(max_length=200)
    body_markdown = models.TextField()
    body_html = models.TextField(editable=False)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    modified = models.DateTimeField(editable=False, auto_now_add=True)

    # determines for what purpose the article is used. Eg: index-header, body,
    # installation-page, getting-started-page etc
    website_position_id = models.SlugField(max_length=100,
                                           unique=True,
                                           db_index=True)

    # fixed sections cannot be added or deleted, pages can be added or deleted
    # and pages can also be listed in the nav bar
    SECTION_TYPE_CHOICES = (
        ('fixed', 'Fixed Section'),
        ('page', 'Page'),
    )
    section_type = models.CharField(max_length=100,
                                    choices=SECTION_TYPE_CHOICES,
                                    default='page')
    show_in_nav = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("view_section", "Can see available sections"),
            ("edit_section", "Can edit available sections"),
        )

    def save(self, *args, **kwargs):
        html_content = markdown.markdown(self.body_markdown,
                                         extensions=['codehilite'])
        # print(html_content)
        # bleach is used to filter html tags like <script> for security
        self.body_html = bleach.clean(html_content, allowed_html_tags,
                                      allowed_attrs)
        self.modified = datetime.datetime.now()

        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(WebsiteSection, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class EventPost(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=140)
    description_img = models.FileField(upload_to='event_images/', null=True, blank=True)
    body_markdown = models.TextField(null=True, blank=True)
    body_html = models.TextField(editable=False)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now()+timezone.timedelta(hours=1))
    keywords = models.CharField(max_length=200, null=True, blank=True)
    attachments = models.FileField(upload_to='event_images/', null=True, blank=True)

    slug = models.SlugField(max_length=150, unique=True)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    modified = models.DateTimeField(editable=False, auto_now_add=True)
    is_highlighted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        html_content = markdown.markdown(self.body_markdown, extensions=['codehilite'])
        date = datetime.date.today()
        self.slug = '%i/%i/%i/%s' % (date.year, date.month, date.day, slugify(self.title))

        # bleach is used to filter html tags like <script> for security
        self.body_html = bleach.clean(html_content, allowed_html_tags,
                                      allowed_attrs)
        self.modified = datetime.datetime.now()

        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(EventPost, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("/event/%i/" % self.slug)


class Publication(models.Model):
    """
    Model for storing publication information.
    """
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    doi = models.CharField(max_length=100, null=True, blank=True)
    # entry type like article, inproceedings, book etc
    entry_type = models.CharField(max_length=100, null=True, blank=True)
    # name of journal in case of article or booktitle in case of
    # inproceedings
    published_in = models.CharField(max_length=200, null=True, blank=True)
    publisher = models.CharField(max_length=200, null=True, blank=True)
    year_of_publication = models.CharField(max_length=4, null=True, blank=True)
    month_of_publication = models.CharField(max_length=10, null=True, blank=True)
    bibtex = models.TextField(null=True, blank=True)
    project_url = models.CharField(max_length=200, null=True, blank=True)
    pdf = models.FileField(null=True, blank=True, upload_to="publication_uploads/")
    abstract = models.TextField(null=True, blank=True)
    is_highlighted = models.BooleanField(default=False)

    created = models.DateTimeField(editable=False, auto_now_add=True)
    modified = models.DateTimeField(editable=False, auto_now_add=True)

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()

        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(Publication, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Course(models.Model):
    """
    Model for storing Course information.
    """
    title = models.CharField(max_length=200)
    acronym = models.CharField(max_length=200)
    level = models.CharField(max_length=200)
    prerequisite = models.CharField(max_length=200)
    semester = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    syllabus = models.FileField(blank=True, null=True, upload_to="course_uploads/")

    created = models.DateTimeField(editable=False, auto_now_add=True)
    modified = models.DateTimeField(editable=False, auto_now_add=True)

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()

        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(Course, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class CarouselImage(models.Model):
    """
    Model for storing image links for carousel.
    """
    image_caption = models.CharField(max_length=200)
    image_description = models.TextField(blank=True, null=True)
    target_url = models.URLField(blank=True, null=True)
    image_url = models.URLField(max_length=200)
    display_description = models.BooleanField(default=True)

    created = models.DateTimeField(editable=False, auto_now_add=True)
    modified = models.DateTimeField(editable=False, auto_now_add=True)

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()

        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(CarouselImage, self).save(*args, **kwargs)

    def __str__(self):
        return self.image_url


class Profile(models.Model):
    """
    Model for storing more information about user
    """
    STATUS_CHOICE = (
        (1, '1.Current Team'),
        (2, '2.Current Students'),
        (3, '3.Collaborators'),
        (4, '4.Visitors'),
        (5, '5.Old Members'),
        (6, '6.Director'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=100, blank=True, null=True,)
    avatar_img = models.ImageField(upload_to='avatar_images/', blank=True, null=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",)
    contact_number = models.CharField(validators=[phone_regex], blank=True, null=True, max_length=15) # validators should be a list

    contact_url = models.URLField(blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=1, default=1, choices=STATUS_CHOICE)
    rank = models.IntegerField(blank=True, default=99)

    profile_page_markdown = models.TextField(null=True, blank=True)
    profile_page_html = models.TextField(null=True, blank=True, editable=False)

    def avatar_url(self):
        """
        Returns the URL of the image associated with this Object.
        If an image hasn't been uploaded yet, it returns a stock image

        :returns: str -- the image url

        """
        if self.avatar_img and hasattr(self.avatar_img, 'url'):
            return self.avatar_img.url
        else:
            return "{0}{1}/{2}".format(settings.STATIC_URL, 'images', 'user-1633250_640.png')

    def save(self, *args, **kwargs):
        html_content = markdown.markdown(self.profile_page_markdown,
                                         extensions=['codehilite'])
        # bleach is used to filter html tags like <script> for security
        self.profile_page_html = bleach.clean(html_content, allowed_html_tags,
                                              allowed_attrs)
        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name()


class BlogPost(models.Model):
    """
    Model to store blog posts
    """
    title = models.CharField(max_length=100, unique=True)
    keywords = models.CharField(max_length=200, null=True, blank=True)
    slug = models.SlugField(max_length=150, unique=True)
    body = models.TextField()
    posted = models.DateTimeField(db_index=True, auto_now_add=True)
    authors = models.ManyToManyField(Profile)
    attachments = models.FileField(upload_to='blog_images/', null=True, blank=True, )
    show_in_lab_blog = models.BooleanField(default=True)
    show_in_my_blog = models.BooleanField(default=True)
    body_html = models.TextField(null=True, blank=True, editable=False)
    is_highlighted = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        date = datetime.date.today()
        self.slug = '%i/%i/%i/%s' % (date.year, date.month, date.day, slugify(self.title))
        html_content = markdown.markdown(self.body, extensions=['markdown.extensions.codehilite', 'markdown.extensions.toc'])

        # bleach is used to filter html tags like <script> for security
        self.body_html = bleach.clean(html_content, allowed_html_tags,
                                      allowed_attrs)
        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(BlogPost, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def created(self):
        return self.posted

    def get_absolute_url(self):
        return reverse("/blog/%i/" % self.slug)


class Research(models.Model):
    """
    Model for storing new research activity
    """
    title = models.CharField(max_length=100)
    position = models.PositiveSmallIntegerField(default=0)
    show_in_page = models.BooleanField(default=True)
    background_img = models.ImageField(upload_to='research_images/', blank=True, null=True)
    default_static_background_img_name = models.CharField(max_length=200, blank=True, null=True)

    description_page_markdown = models.TextField(null=True, blank=True)
    description_page_html = models.TextField(null=True, blank=True, editable=False)

    def tag(self):
        """ Returns website tag for internal cross reference"""
        return "_".join(self.title.lower().split())

    def background_url(self):
        """
        Returns the URL of the image associated with this Object.
        If an image hasn't been uploaded yet, it returns a stock image

        :returns: str -- the image url

        """
        if self.background_img and hasattr(self.background_img, 'url'):
            return self.background_img.url
        else:
            return "{0}{1}/{2}".format(settings.STATIC_URL, 'images', self.default_static_background_img_name)

    def save(self, *args, **kwargs):
        html_content = markdown.markdown(self.description_page_markdown, extensions=['codehilite'])
        # bleach is used to filter html tags like <script> for security
        self.description_page_html = bleach.clean(html_content, allowed_html_tags, allowed_attrs)
        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(Research, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class JournalImage(models.Model):
    """
    Model for storing Journal.
    """
    title = models.CharField(max_length=200)
    cover = models.ImageField(upload_to='journal_images/')
    caption = models.CharField(max_length=200, blank=True, null=True)
    link_url = models.URLField(blank=True, null=True)
    display = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(JournalImage, self).save(*args, **kwargs)

    def __str__(self):
        return self.cover.url


class CareerModel(models.Model):
    """
    Model to store blog posts
    """
    name = models.CharField(max_length=100, default="default")
    body_internal = models.TextField()
    body_external = models.TextField()
    attachments = models.FileField(upload_to='careers_images/', null=True, blank=True, )
    body_internal_html = models.TextField(null=True, blank=True, editable=False)
    body_external_html = models.TextField(null=True, blank=True, editable=False)


    def save(self, *args, **kwargs):
        html_internal_content = markdown.markdown(self.body_internal,
                                         extensions=['markdown.extensions.codehilite', 'markdown.extensions.toc'])
        html_external_content = markdown.markdown(self.body_external,
                                         extensions=['markdown.extensions.codehilite', 'markdown.extensions.toc'])

        # bleach is used to filter html tags like <script> for security
        self.body_internal_html = bleach.clean(html_internal_content, allowed_html_tags,
                                               allowed_attrs)

        # bleach is used to filter html tags like <script> for security
        self.body_external_html = bleach.clean(html_external_content, allowed_html_tags,
                                               allowed_attrs)

        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(CareerModel, self).save(*args, **kwargs)


class Software(models.Model):
    """
    Model for storing Lab Software
    """
    title = models.CharField(max_length=100)
    position = models.PositiveSmallIntegerField(default=0)
    show_in_page = models.BooleanField(default=True)
    website_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    background_img = models.ImageField(upload_to='software_images/', blank=True, null=True)
    default_static_background_img_name = models.CharField(max_length=200, blank=True, null=True)

    description_page_markdown = models.TextField(null=True, blank=True)
    description_page_html = models.TextField(null=True, blank=True, editable=False)

    def tag(self):
        """Returns website tag for internal cross reference."""
        return "_".join(self.title.lower().split())

    def background_url(self):
        """
        Returns the URL of the image associated with this Object.
        If an image hasn't been uploaded yet, it returns a stock image

        :returns: str -- the image url

        """
        if self.background_img and hasattr(self.background_img, 'url'):
            return self.background_img.url
        else:
            return "{0}{1}/{2}".format(settings.STATIC_URL, 'images', self.default_static_background_img_name)

    def save(self, *args, **kwargs):
        html_content = markdown.markdown(self.description_page_markdown, extensions=['codehilite'])
        # bleach is used to filter html tags like <script> for security
        self.description_page_html = bleach.clean(html_content, allowed_html_tags, allowed_attrs)
        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(Software, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
