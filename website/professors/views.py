from django.shortcuts import render, redirect
from .models import get_professors_api, get_professor_api, create_review_api, create_professor_api, delete_professor_api

def professors(request):
    query = request.GET.get('query', '')
    token = request.session.get("access_token")
    professors_list = get_professors_api(query, token=token)
    return render(request, 'pages/professors/professors.html', {'professors': professors_list, 'query': query})

def professor_detail(request, pk):
    token = request.session.get("access_token")
    professor = get_professor_api(pk, token=token)
    if not professor:
        return redirect('professors')
        
    if request.method == 'POST':
        data = {
            'author': request.POST.get('author'),
            'rating': request.POST.get('rating'),
            'comment': request.POST.get('comment')
        }
        if create_review_api(pk, data, token=token):
            return redirect('professor_detail', pk=pk)
            
    return render(request, 'pages/professors/professor_detail.html', {'professor': professor})

def add_professor(request):
    role = request.session.get("role")
    if role not in ['ADMIN', 'STAFF']:
        return redirect('professors')

    if request.method == 'POST':
        data = {
            'name': request.POST.get('name'),
            'department': request.POST.get('department'),
            'email': request.POST.get('email'),
            'office': request.POST.get('office'),
        }
        token = request.session.get("access_token")
        if create_professor_api(data, token=token):
            return redirect('professors')
    return render(request, 'pages/professors/add_professor.html')

def delete_professor(request, pk):
    role = request.session.get("role")
    if role not in ['ADMIN', 'STAFF']:
        return redirect('professors')

    if request.method == 'POST':
        token = request.session.get("access_token")
        delete_professor_api(pk, token=token)
    return redirect('professors')
