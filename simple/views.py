# Create your views here.
from django.template import RequestContext, defaultfilters
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from .models import get_post, get_post_by_slug, get_posts, index_post, get_author, create_author, get_reference, index_comment
from .forms import BlogForm, CommentForm
from pyes import ES
from pyes.query import MatchAllQuery, FilteredQuery
from pyes.filters import TermFilter, TermsFilter
from datetime import datetime
from django.conf import settings
import markdown

USE_AKISMET = getattr(settings, 'USE_AKISMET', True)


def blog_detail_slug(request, slug):
    post = get_post_by_slug(slug)
    return render_to_response('simple/blogpost_detail.html',
                              {'object': post},
                              context_instance=RequestContext(request))

def blog_detail(request, parent, pk):
    post = get_post(parent, pk)
    return render_to_response('simple/blogpost_detail.html',
                              {'object': post},
                              context_instance=RequestContext(request))

def blog_list(request):
    posts = get_posts('-created_on')
    return render_to_response('simple/blogpost_list.html',
                              {'object_list': posts},
                              context_instance=RequestContext(request))


def blog_edit(request, parent=None, pk=None):
    if parent and pk:
        post = get_post(parent, pk)
        author = post.author
    else:
        try:
            author = get_author(name=request.user.username)[0]
        except:
            author = create_author(name=request.user.username)
        post = dict(author=author)
    if request.method == 'POST':
        form = BlogForm(request.POST, initial=post)
        if form.is_valid():
            body = form.cleaned_data['body']
            if form.cleaned_data['is_markdown']:
                body = markdown.markdown(body)
            post['author'] = author
            post['title'] = form.cleaned_data['title']
            if form.cleaned_data['summary']:
                post['summary'] = form.cleaned_data['summary']
            post['body'] = body
            post['slug'] = defaultfilters.slugify(post['title'])
            post['body_clean'] = form.cleaned_data['body']
            post['body_lower'] = form.cleaned_data['body']
            post['updated_on'] = datetime.utcnow()
            if 'created_on' not in post:
                post['created_on'] = datetime.utcnow()
            blog_id = index_post(author, post, post['slug'])
            return HttpResponseRedirect(reverse('blogpost_detail_by_slug', args=(blog_id,)))
        else:
            form = BlogForm(initial=post)
    else:
        form = BlogForm(initial=post)
    return render_to_response('simple/blogpost_form.html',
                              {'object': post, 'form': form},
                              context_instance=RequestContext(request))


def blog_delete(request, parent, pk):
    pass

def comment_edit(request, reference_type, reference_to):
    referent = None
    while reference_type != 'post':
        # chase back to a blog post
        referent = get_reference(reference_to, reference_type)
        reference_to = referent.reference_to
        reference_type = referent.reference_type
    referent = get_reference(reference_to, reference_type)
    if request.method == 'POST':
        form = CommentForm(data=request.POST, reference_type=reference_type, reference_to=reference_to)
        if form.is_valid():
            comment = dict(comment=form.cleaned_data['comment'],
                           pingback=form.cleaned_data['pingback'],
                           comment_author=form.cleaned_data['name'],
                           created_on=datetime.utcnow(),
                           reference_type=reference_type,
                           reference_to=reference_to)
            if USE_AKISMET:
                try:
                    import akismet
                    api = akismet.Akismet(agent='ElasticUnicorn')
                    if api.verify_key():
                        data = dict(
                            user_ip=request.META.get('REMOTE_ADDR'),
                            user_agent=request.META.get('HTTP_USER_AGENT'),
                            referrer=request.META.get('HTTP_REFERER', 'unknown'),
                            SERVER_ADDR=request.META.get('SERVER_ADDR', ''),
                            SERVER_ADMIN=request.META.get('SERVER_ADMIN', ''),
                            SERVER_NAME=request.META.get('SERVER_NAME', ''),
                            SERVER_PORT= request.META.get('SERVER_PORT', ''),
                            SERVER_SIGNATURE=request.META.get('SERVER_SIGNATURE', ''),
                            SERVER_SOFTWARE=request.META.get('SERVER_SOFTWARE', ''),
                            HTTP_ACCEPT=request.META.get('HTTP_ACCEPT', ''),
                            )
                        comment['is_spam'] = api.comment_check(comment['comment'], data=data)
                    else:
                        comment['is_spam'] = True
                except:
                    comment['is_spam'] = True
            else:
                comment['is_spam'] = False
            comment['is_spam'] = False
            if referent:
                comment['post_author'] = referent.author
                comment['post'] = referent.get_meta().id
                comment['post_title'] = referent.title
            else:
                referent = get_reference(reference_to, reference_type)
                comment['post_author'] = referent.author
                comment['post'] = referent.get_meta().id
                comment['post_title'] = referent.title
            index_comment(comment)
        return HttpResponseRedirect(reverse('blogpost_detail_by_slug', args=(referent.get_meta().id,)))
    return HttpResponseRedirect(reverse('blogpost_detail_by_slug', args=(referent.get_meta().id,)))

