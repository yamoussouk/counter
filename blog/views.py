import re

from django.views import generic

from .models import Post


def mobile(request):
    MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)
    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False


class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'blog/blog_posts.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["canonical"] = f'https://{self.request.META["HTTP_HOST"]}{self.request.META["PATH_INFO"]}'
        context['device'] = mobile(self.request)
        return context


class PostDetail(generic.DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        images = Post.objects.prefetch_related('post_images').filter(id=kwargs["object"].id)
        imgs = images[0].post_images.all()
        context["images"] = imgs
        try:
            next_slug = Post.objects.filter(id__gt=kwargs["object"].id)[0].slug
        except IndexError:
            next_slug = ''
        context["next"] = next_slug
        try:
            prev_slug = Post.objects.filter(id__lt=kwargs["object"].id)[0].slug
        except IndexError:
            prev_slug = ''
        context["prev"] = prev_slug
        context["seo_title"] = images[0].title + ' - Minervastudio'
        context["seo_description"] = images[0].short_description
        context["canonical"] = f'https://{self.request.META["HTTP_HOST"]}{self.request.META["PATH_INFO"]}'
        context['device'] = mobile(self.request)
        return context
