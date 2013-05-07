from django.contrib import admin
from .models import BlogPost

class BlogPostAdmin(admin.ModelAdmin):
    name = 'BlogPost'

admin.site.register(BlogPost, BlogPostAdmin)

