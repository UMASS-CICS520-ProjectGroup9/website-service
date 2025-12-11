from django.shortcuts import render, redirect
from .models import get_professors_api, get_professor_api, create_review_api, create_professor_api, delete_professor_api, delete_review_api

def professors(request):
    query = request.GET.get('query', '')
    token = request.session.get("access_token")
    error = None
    professors_list = []
    try:
        professors_list = get_professors_api(query, token=token)
    except Exception as e:
        error = str(e) or "An error occurred while fetching professors."
    authen = {
        "is_login": "access_token" in request.session,
        "user_email": request.session.get("email"),
        "role": request.session.get("role"),
        "user_id": request.session.get("user_id")
    }
    context = {'professors': professors_list, 'query': query, 'authen': authen}
    if error:
        context['error'] = error
    return render(request, 'pages/professors/professors.html', context)

def professor_detail(request, pk):
    token = request.session.get("access_token")
    professor = get_professor_api(pk, token=token)
    if not professor:
        return redirect('professors')
    authen = {
        "is_login": "access_token" in request.session,
        "user_email": request.session.get("email"),
        "role": request.session.get("role"),
        "user_id": request.session.get("user_id")
    }
    error = None
    if request.method == 'POST':
        data = {
            'author': request.POST.get('author'),
            'rating': request.POST.get('rating'),
            'comment': request.POST.get('comment')
        }
        try:
            success = create_review_api(pk, data, token=token)
        except Exception as e:
            error = str(e) or "An error occurred while adding the review."
            success = False
        if success:
            return redirect('professor_detail', pk=pk)
        else:
            error = error or "Failed to add review. Please check your input."
    context = {'professor': professor, 'authen': authen}
    if error:
        context['error'] = error
    return render(request, 'pages/professors/professor_detail.html', context)

def add_professor(request):
    role = request.session.get("role")
    if role not in ['ADMIN', 'STAFF']:
        return redirect('professors')
    authen = {
        "is_login": "access_token" in request.session,
        "user_email": request.session.get("email"),
        "role": request.session.get("role"),
        "user_id": request.session.get("user_id")
    }
    error = None
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name'),
            'department': request.POST.get('department'),
            'email': request.POST.get('email'),
            'office': request.POST.get('office'),
        }
        token = request.session.get("access_token")
        try:
            success = create_professor_api(data, token=token)
        except Exception as e:
            error = str(e) or "An error occurred while adding the professor."
            success = False
        if success:
            return redirect('professors')
        else:
            error = error or "Failed to add professor. Please check your input."
    return render(request, 'pages/professors/add_professor.html', {'authen': authen, 'error': error} if error else {'authen': authen})

def delete_professor(request, pk):
    role = request.session.get("role")
    if role not in ['ADMIN', 'STAFF']:
        return redirect('professors')
    authen = {
        "is_login": "access_token" in request.session,
        "user_email": request.session.get("email"),
        "role": request.session.get("role"),
        "user_id": request.session.get("user_id")
    }
    if request.method == 'POST':
        token = request.session.get("access_token")
        success = False
        error = None
        try:
            success = delete_professor_api(pk, token=token)
        except Exception as e:
            error = str(e) or "An error occurred while deleting the professor."
        if not success or error:
            # Render the professors page with error
            query = ''
            try:
                professors_list = get_professors_api(query, token=token)
            except Exception:
                professors_list = []
            authen = {
                "is_login": "access_token" in request.session,
                "user_email": request.session.get("email"),
                "role": request.session.get("role"),
                "user_id": request.session.get("user_id")
            }
            context = {
                'professors': professors_list,
                'query': query,
                'authen': authen,
                'error': error or "Failed to delete professor."
            }
            return render(request, 'pages/professors/professors.html', context)
    return redirect('professors')

def delete_review(request, prof_pk, review_pk):
    token = request.session.get("access_token")
    authen = {
        "is_login": "access_token" in request.session,
        "user_email": request.session.get("email"),
        "role": request.session.get("role"),
        "user_id": request.session.get("user_id")
    }
    # Call the API to delete the review
    delete_review_api(prof_pk, review_pk, token=token)
    # Redirect back to the referring page or professors list
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('professors')
