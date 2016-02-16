from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.shortcuts import redirect
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
import feedparser
import nltk

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    return render(request, 'dash/post_list.html', {'posts':posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'dash/post_detail.html', {'post': post})

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            #post.published_date = timezone.now()
            post.save()
            return redirect('dash.views.post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'dash/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('dash.views.post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'dash/post_edit.html', {'form': form})

@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'dash/post_draft_list.html', {'posts': posts})

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('dash.views.post_detail', pk=pk)

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('dash.views.post_list')


def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/accounts/register_success')
    form = UserCreationForm()
    #print args
    return render(request, 'dash/register.html', {'form': form})

def register_success(request):
    return render(request, 'dash/register_success.html')


feeds = [
    'http://www.sfgate.com/rss/feed/Tech-News-449.php',
    'http://feeds.feedburner.com/TechCrunch/startups',
    'http://news.cnet.com/8300-1001_3-92.xml',
    'http://www.zdnet.com/news/rss.xml',
    'http://www.computerweekly.com/rss/Latest-IT-news.xml',
    'http://feeds.reuters.com/reuters/technologyNews',
    'http://www.tweaktown.com/news-feed/'
]

    
def feedTech(request):
    corpus = []
    titles=[]
    ct = -1
    for feed in feeds:
        d = feedparser.parse(feed)
        for e in d['entries']:
            words = nltk.wordpunct_tokenize((e['description']))
            words.extend(nltk.wordpunct_tokenize(e['title']))
            lowerwords=[x.lower() for x in words if len(x) > 1]
            ct += 1
            print (ct, "TITLE",e['title'])
            corpus.append(lowerwords)
            titles.append(e['title'])
    return render(request, 'dash/feeds.html')
