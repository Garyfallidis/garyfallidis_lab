import re

from django import template
import markdown

register = template.Library()


# converts all youtube URLs in the text to embed HTML
@register.filter(name='youtube_embed_url')
def youtube_embed_url(value, args=None):
    size = (640,360)
    arg_list = [int(a) for a in args.split(',')] if args else []
    if len(arg_list) == 2:
        size = (arg_list[0],arg_list[1])
    exp = re.compile(r'((http|https)\:\/\/www\.youtube\.com\/watch\?v=([a-zA-Z0-9]*))')
    matches = exp.findall(value)
    processed_str = value
    template = '<div class="youtube-wrapper"><iframe class="youtube-embed" width="{0}" height="{1}" \
                title="youtube-frame" src="https://www.youtube.com/embed/%s?rel=0&modestbranding=1" \
                frameborder="0" allowfullscreen></iframe></div>'.format(size[0],size[1])
    for match in matches:
        processed_str = processed_str.replace(match[0], template % match[2])
    return processed_str


# converts Markdown to HTML
@register.filter(name='markdown_to_html')
def markdown_to_html(value):
    processed_str = markdown.markdown(value, extensions=['codehilite'])
    return processed_str

# Get model type name
@register.filter(name='get_class')
def get_class(value):
  return value.__class__.__name__