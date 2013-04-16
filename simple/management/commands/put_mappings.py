from django.core.management.base import BaseCommand, CommandError
import pyes
from pyes import mappings

author = {
    "name": mappings.StringField(name="name", index="analyzed", index_analyzer="standard", store=False).as_dict()
}

blogpost = {
    "author": mappings.StringField(name="author", index="not_analyzed", store=False).as_dict(),
    "body": mappings.MultiField(name="body", fields=[
            mappings.StringField(name="body", index="analyzed", index_anlayzer="standard", store=False),
            mappings.StringField(name="body_snowball", index="analyzed", index_analyzer="snowball", store=False),
            ]).as_dict(),
    "created_on": mappings.DateField(name="created_on", index="not_analyzed", store=False).as_dict(),
    "updated_on": mappings.DateField(name="updated_on", index="not_analyzed", store=False).as_dict(),
    "title": mappings.StringField(name="title", index="not_analyzed", store=False).as_dict(),
    }

comment = {
    "comment": mappings.StringField(name="comment", index="analyzed", index_analyzer="standard", store=False).as_dict(),
    "created_on": mappings.DateField(name="created_on", index="not_analyzed", store=False).as_dict(),
    "is_spam": mappings.BooleanField(name="is_spam", index="not_analyzed", store=False).as_dict(),
    "reference_to": mappings.StringField(name="reference_to", index="not_analyzed", store=False).as_dict(),
    "reference_type": mappings.StringField(name="reference_type", index="not_analyzed", store=False).as_dict(),
    "post": mappings.StringField(name="post", index="not_analyzed", store=False).as_dict(),
    "post_author": mappings.StringField(name="post_author", index="not_analyzed", store=False).as_dict(),
    "post_title": mappings.StringField(name="post_title", index="not_analyzed", store=False).as_dict(),
    "pingback": mappings.StringField(name="pingback", index="not_analyzed", store=False).as_dict(),
    }

class Command(BaseCommand):
    help = "Installs JSON schema for ElasticSearch based on model definitions"

    def __init__(self, *args, **kwargs):
        super(BaseCommand, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        mappings = [
            {"author": {"properties": author}},
            {"post": {"_parent": {"type": "author"}, "properties": blogpost}},
            {"comment": {"properties": comment}},
            ]
        es = pyes.es.ES()
        for _mapping_dict in mappings:
            _type = _mapping_dict.keys()[0]
            _mapping = {_type: _mapping_dict[_type]}
            es.indices.create_index_if_missing("blog")
            es.indices.put_mapping(doc_type=_type, indices="blog", mapping=_mapping)
            self.stdout.write("-- %s\n" % _type)
            self.stdout.flush()
        self.stdout.write("Finished\n")
        self.stdout.flush()
