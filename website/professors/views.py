from django.shortcuts import render, redirect
from .models import get_professors_api, get_professor_api, create_review_api

def professors(request):
    query = request.GET.get('query', '')
    professors_list = get_professors_api(query)
    return render(request, 'pages/professors/professors.html', {'professors': professors_list, 'query': query})

def professor_detail(request, pk):
    professor = get_professor_api(pk)
    if not professor:
        return redirect('professors')
        
    if request.method == 'POST':
        data = {
            'author': request.POST.get('author'),
            'rating': request.POST.get('rating'),
            'comment': request.POST.get('comment')
        }
        if create_review_api(pk, data):
            return redirect('professor_detail', pk=pk)
            
    return render(request, 'pages/professors/professor_detail.html', {'professor': professor})
