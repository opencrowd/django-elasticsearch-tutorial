from functools import partial
from django.template import Library
from simple.models import get_comments, get_comment_count, get_posts, get_top_authors, get_reference_id
from simple.forms import CommentForm

r = register = Library()

@r.filter
def truncate_char_to_space(value, arg):
    data = str(value)
    if len(value) < arg:
        return data

    if data.find(' ', arg, arg+5) == -1:
        return data[:arg] + '...'
    else:
        return data[:arg] + data[arg:data.find(' ', arg)] + '...'

@r.inclusion_tag('simple/tags/blog_detail.html', takes_context=True)
def blog_detail(context):
    return dict(blog_post=context['object'],
                comments=get_comments(reference_to=get_reference_id(context['object'], 'author'), is_spam=False),
                user=context['user'])


@r.inclusion_tag('simple/tags/blog_summary.html', takes_context=True)
def blog_summary(context):
    return dict(blog_post=context['object'],
                comment_count=get_comment_count(reference_to=get_reference_id(context['object'], 'author'), is_spam=False),
                user=context['user'])

@r.inclusion_tag('simple/tags/recent_posts.html', takes_context=True)
def recent_posts(context):
    blog_posts = get_posts('-created_on')
    return dict(blog_posts=blog_posts[:5],
                user=context['user'])

@r.inclusion_tag('simple/tags/recent_comments.html', takes_context=True)
def recent_comments(context):
    rcomments = get_comments('-created_on', is_spam=False)
    return dict(comments=rcomments[:5],
                user=context['user'])

@r.inclusion_tag('simple/tags/user_actions.html', takes_context=True)
def user_actions(context):
    return dict(user=context['user'])

@r.inclusion_tag('simple/tag/prolific_authors.html', takes_context=True)
def prolific_authors(context):
    authors = get_top_authors()
    return dict(authors=authors[:5],
                user=context['user'])

@r.inclusion_tag('simple/tags/comments.html', takes_context=True)
def comments(context, reference_to=None, depth=0):
    blog_post = context.get('object')
    if not reference_to:
        reference_id = get_reference_id(blog_post, 'author')
        reference_type = 'post'
    else:
        reference_id = get_reference_id(reference_to)
        reference_type = 'comment'
    comment_list = get_comments(reference_to=reference_id, is_spam=False)
    return dict(comments=comment_list,
                blog_post=blog_post,
                form=CommentForm(reference_type=reference_type, reference_to=reference_id),
                user=context['user'],
                depth=depth,
                next_depth=depth+1,
                span=12-depth)



