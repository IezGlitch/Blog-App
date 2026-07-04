from django.shortcuts import render, get_object_or_404
from .models import Post
from django.views.generic import ListView
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from .forms import CommentForm,EmailPostForm,SearchForm
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import (SearchVector,SearchQuery,SearchRank)
from django.contrib.postgres.search import TrigramSimilarity

def post_list(request, tag_slug=None):
    post_list=Post.published.all()
    tag=None
    if tag_slug:
        tag=get_object_or_404(Tag, slug=tag_slug)
        post_list=post_list.filter(tags__in=[tag])
    paginator=Paginator(post_list,3)
    page_number=request.GET.get('page',1)
    try:
        posts=paginator.page(page_number)
    except EmptyPage:
        posts=paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts=paginator.page(1)
    return render(request,"blog/post/list.html",{'posts':posts, 'tag':tag})

'''class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 3
    template_name = 'blog/post/list.html'''


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    post_tags_ids=post.tags.values_list('id', flat=True)
    similar_posts=Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts=similar_posts.annotate(matching_tags=Count('tags')).order_by('-matching_tags','-publish')
    active_comments =post.comments.filter(active=True)
    comment_form =CommentForm()

    return render(request, 'blog/post/detail.html', {'post': post,'comments': active_comments,'form': comment_form,'similar_posts':similar_posts})
def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())

            subject = f"{cd['name']} recommends you to read {post.title}"
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )

            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']]
            )

            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', { 
        'post': post,
        'form': form,
        'sent': sent
    })


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id , status=Post.Status.PUBLISHED)
    comment =None
    form=CommentForm(data=request.POST)
    if form.is_valid():
        comment=form.save(commit=False)
        comment.post =post
        comment.save()
    return render(request, 'blog/post/share.html',{'post': post, 'form': form, 'comment': comment})

def tag_list(request):
    tags = (
        Tag.objects.annotate(post_count=Count("taggit_taggeditem_items"))
        .filter(post_count__gt=0)
        .order_by("-post_count", "name")
    )
    return render(request, "blog/post/tag_list.html", {"tags": tags})


def post_search(request):
    form=SearchForm()
    query=None
    results=[]

    if 'query' in request.GET:
        form=SearchForm(request.GET)
        if form.is_valid():
            query=form.cleaned_data['query']
            # search_vector=SearchVector('title','body',config='spanish')
            # search_query=SearchQuery(query,config='spanish')
            search_vector=SearchVector('title',weight='A')+SearchVector('body',weight='B')
            search_query=SearchQuery(query)
            '''results=(Post.published.annotate(search=search_vector,
                                             rank=SearchRank(search_vector,search_query))
                                             .filter(rank__gte=0.3).order_by('-rank'))'''
            results=(Post.published.annotate(similarity=TrigramSimilarity('title',query))
                     .filter(similarity__gt=0.1).order_by('-similarity'))
    return render(request, 'blog/post/search.html',{'form':form,'query':query ,'results':results})