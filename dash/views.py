from django.shortcuts import render

def post_list(request):
    return render(request, 'dash/post_list.html', {})
