from functools import partial
from django.template import Library
from blog.models import get_comments, get_comment_count, get_posts, get_top_authors, get_reference_id
from blog.forms import CommentForm

r = register = Library()

@r.filter
def truncate_char_to_space(value, arg):
    try:
        data = str(value)
    except:
        data = unicode(value)
    if len(value) < arg:
        return data

    if data.find(' ', arg, arg+5) == -1:
        return data[:arg] + '...'
    else:
        return data[:arg] + data[arg:data.find(' ', arg)] + '...'

@r.inclusion_tag('blog/tags/blog_detail.html', takes_context=True)
def blog_detail(context):
    return dict(blog_post=context['object'],
                comments=get_comments(reference_to=get_reference_id(context['object'], 'author'), is_spam=False),
                user=context['user'])


@r.inclusion_tag('blog/tags/blog_summary.html', takes_context=True)
def blog_summary(context):
    return dict(blog_post=context['object'],
                comment_count=get_comment_count(reference_to=get_reference_id(context['object'], 'author'), is_spam=False),
                user=context['user'])

@r.inclusion_tag('blog/tags/recent_posts.html', takes_context=True)
def recent_posts(context):
    blog_posts = get_posts(False, '-created_on')
    return dict(blog_posts=blog_posts[:5],
                user=context['user'])

@r.inclusion_tag('blog/tags/recent_comments.html', takes_context=True)
def recent_comments(context):
    rcomments = get_comments('-created_on', is_spam=False)
    return dict(comments=rcomments[:5],
                user=context['user'])

@r.inclusion_tag('blog/tags/user_actions.html', takes_context=True)
def user_actions(context):
    return dict(user=context['user'])

@r.inclusion_tag('blog/tag/prolific_authors.html', takes_context=True)
def prolific_authors(context):
    authors = get_top_authors()
    return dict(authors=authors[:5],
                user=context['user'])


class TreeNode(object):
    def __init__(self, value=None, parent=None, depth=0):
        self.value = value
        self.parent = parent
        if self.parent is not None:
            self.parent.children.append(self)
        self.children = []
        self.depth = depth

    def __getattr__(self, key):
        try:
            if not 'key' in self.__dict__:
                return getattr(self.value, key)
        except AttributeError:
            return None

    def __len__(self):
        return len(self.children)

    def __getitem__(self, index):
        return self.children[index]

    def __iter__(self):
        return iter(self.children)

    def __repr__(self):
        return '%s' % type(self.value)

@r.inclusion_tag('blog/tags/comments.html', takes_context=True)
def comments(context, reference_to=None, depth=0):
    blog_post = context.get('object')
    if not isinstance(reference_to, (list, tuple, TreeNode)):
        if not reference_to:
            reference_id = get_reference_id(blog_post, 'author')
            reference_type = 'post'
        else:
            reference_id = get_reference_id(reference_to)
            reference_type = 'comment'
        comment_list = get_comments('serial', 'path', post=blog_post.slug, is_spam=False)
        comment_tree = TreeNode()
        current_tree = comment_tree
        for comment in comment_list:
            comment.reply_form = CommentForm(reference_type='comment', reference_to=comment.get_meta().id)
            depth = len(comment.path.split('/')) - 2
            if depth > current_tree.depth:
                current_tree = TreeNode(comment, current_tree, depth)
            elif depth <= current_tree.depth:
                if depth:
                    current_tree = TreeNode(comment, current_tree.parent, depth)
                else:
                    current_tree = TreeNode(comment, comment_tree, depth)
    else:
        comment_tree = reference_to
        reference_type = 'comment'
        reference_id = get_reference_id(reference_to.value)
    return dict(comments=comment_tree.children,
                blog_post=blog_post,
                comment_reply_form=CommentForm(reference_type=reference_type, reference_to=reference_id),
                user=context['user'])



