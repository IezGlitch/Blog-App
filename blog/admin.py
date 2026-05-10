from django.contrib import admin
from .models import Post
from .models import Comment,Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title','slug', 'author', 'publish', 'status']
    list_filter = ['status', 'publish', 'created']
    search_fields = ['title', 'body']
    date_hierarchy = 'publish'
    prepopulated_fields = {'slug': ['title']}
    show_facets = admin.ShowFacets.ALWAYS  # optional (Django 5+)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'email', 'body']