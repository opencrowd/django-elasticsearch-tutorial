from functools import partial
from BeautifulSoup import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.core.urlresolvers import reverse
from django.core import cache
from django.utils.hashcompat import md5_constructor
# Create your models here.
from datetime import datetime
import time
from pyes import ES
from pyes.query import MatchAllQuery, FilteredQuery, TermQuery
from pyes.filters import TermFilter, TermsFilter, ANDFilter
from django.conf import settings

ELASTICSEARCH_URL = getattr(settings, 'ELASTICSEARCH_URL', 'http://localhost:9200')
ELASTICSEARCH_INDEX = getattr(settings, 'ELASTICSEARCH_INDEX', 'blog')


def strip_html_tags(html_txt):
    if html_txt is None:
        return None
    else:
        return ''.join(BeautifulSoup(html_txt).findAll(text=True)).replace('&nbsp;', ' ')

def _parse_datetime(dt):
    try:
        return datetime(*time.strptime(dt.split('.')[0], "%Y-%m-%dT%H:%M:%S")[:6])
    except AttributeError:
        if isinstance(dt, datetime):
            return dt
        raise

def get_connection():
    return ES(ELASTICSEARCH_URL)

def get_reference(_id, _type):
    parts = _id.split('-!-')
    es = ES()
    if len(parts) == 1:
        return es.get('blog', _type, parts[0])
    return es.get('blog', _type, parts[0], routing=parts[1])

def get_reference_id(obj, parent_field=None):
    if obj.get(parent_field):
        return '%s-!-%s' % (obj.get_meta().id, obj.get(parent_field).get_meta().id)
    return obj.get_meta().id

def get_comments(*order_by, **kwargs):
    filters = [TermFilter(key, value) for key, value in kwargs.items()]
    if filters:
        q = FilteredQuery(MatchAllQuery(), ANDFilter(filters))
    else:
        q = MatchAllQuery()
    ordering = []
    for field in order_by:
        if field.startswith('-'):
            ordering.append(':'.join([field[1:], 'desc']))
        else:
            ordering.append(field)
    es = get_connection()
    sfunc = partial(es.search, q, ELASTICSEARCH_INDEX, 'comment')
    if ordering:
        sfunc = partial(sfunc, sort=ordering[0])
    rs = sfunc()
    results = []
    for row in rs:
        row['reference'] = get_reference(row['reference_to'], row['reference_type'])
        row['created_on'] = _parse_datetime(row['created_on'])
        results.append(row)
    return results

def get_comment_count(**kwargs):
    return len(get_comments(**kwargs))

def get_post_by_slug(slug):
    es = get_connection()
    posts = es.search(FilteredQuery(MatchAllQuery(), TermFilter('slug', slug)), ELASTICSEARCH_INDEX, 'post')
    if not posts.total:
        raise ObjectDoesNotExist
    obj = posts[0]
    obj['author'] = get_author(id=obj['author'])
    if 'created_on' in obj:
        obj['created_on'] = _parse_datetime(obj['created_on'])
    else:
        obj['created_on'] = datetime.utcnow()
    if 'updated_on' in obj:
        obj['updated_on'] = _parse_datetime(obj['updated_on'])
    else:
        obj['updated_on'] = datetime.utcnow()
    return obj

def get_post(author, blog_id):
    es = get_connection()
    obj = es.get(ELASTICSEARCH_INDEX, 'post', blog_id, routing=author)
    obj['author'] = get_author(id=author)
    if 'created_on' in obj:
        obj['created_on'] = _parse_datetime(obj['created_on'])
    else:
        obj['created_on'] = datetime.utcnow()
    if 'updated_on' in obj:
        obj['updated_on'] = _parse_datetime(obj['updated_on'])
    else:
        obj['updated_on'] = datetime.utcnow()
    return obj

def get_posts(*order_by):
    es = get_connection()
    query = MatchAllQuery()
    ordering = []
    for field in order_by:
        if field.startswith('-'):
            ordering.append(':'.join([field[1:], 'desc']))
        else:
            ordering.append(field)
    sfunc = partial(es.search, query, ELASTICSEARCH_INDEX, 'post')
    if ordering:
        sfunc = partial(sfunc, sort=ordering[0])
    rs = sfunc()
    author_cache = {}
    results = [row for row in rs]
    for row in results:
        try:
            row['author'] = author_cache[row['author']]
        except KeyError:
            author = get_author(id=row['author'])
            author_cache[row['author']] = author
            row['author'] = author
        except TypeError:
            pass
        if 'created_on' in row:
            row['created_on'] = _parse_datetime(row['created_on'])
        else:
            row['created_on'] = datetime.utcnow()
        if 'updated_on' in row:
            row['updated_on'] = _parse_datetime(row['updated_on'])
        else:
            row['updated_on'] = datetime.utcnow()
    return results

def index_post(author, post, slug=None):
    es = get_connection()
    author_id = author.get_meta().id
    if slug:
        post_id = slug
    if post.get('slug'):
        post_id = post['slug']
    else:
        try:
            post_id = post.get_meta().id
        except AttributeError:
            post_id = None
    post['author'] = author_id
    return es.index(post, ELASTICSEARCH_INDEX, 'post', id=post_id, parent=author_id)._id

def index_comment(comment):
    es = get_connection()
    post_ref = comment.get('post')
    if post_ref:
        var_key = md5_constructor(post_ref).hexdigest()
        all_key = 'template.cache.comments.%s' % var_key
        cache.get_cache('default').delete(all_key)
    return es.index(comment, ELASTICSEARCH_INDEX, 'comment')._id

def create_author(**kwargs):
    es = get_connection()
    _id = es.index(kwargs, ELASTICSEARCH_INDEX, 'author')._id
    return es.get(ELASTICSEARCH_INDEX, 'author', _id)

def get_author(**kwargs):
    es = get_connection()
    if 'id' in kwargs:
        return es.get('blog', 'author', kwargs['id'])
    filters = [TermFilter(key, value) for key, value in kwargs.items()]
    q = FilteredQuery(MatchAllQuery(), ANDFilter(filters))
    return es.search(q, ELASTICSEARCH_INDEX, 'author')

def get_top_authors():
    q = MatchAllQuery()
    q = q.search()
    q.facet.add_term_facet('author')
    es = get_connection()
    facets = es.search(q, ELASTICSEARCH_INDEX, 'post').facets
    authors = []
    for term in facets['author']['terms']:
        authors.append(get_author(id=term['term']))
    return authors



