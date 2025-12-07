from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import (
    discussionAPI,
    getDiscussionByID_model,
    getCommentsByDiscussion_model,
    createDiscussion_model,
    get_course_discussion_model,
    get_course_comments_model,
    create_course_comment_model,
    removeDiscussion_model,
)
from base.views import getAuthen
import requests


def discussion_list(request):
    discussions = discussionAPI() or []
    # Paginate discussions: 10 per page
    page_number = request.GET.get('page', 1)
    paginator = Paginator(discussions, 10)
    page_obj = paginator.get_page(page_number)
    authen = getAuthen(request)
    return render(request, 'pages/discussions/discussions.html', {
        'discussions': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'authen': authen,
    })


def discussion_detail(request, pk):
    discussion = getDiscussionByID_model(pk)
    comments = getCommentsByDiscussion_model(pk)
    context = {
        'discussion': discussion,
        'comments': comments,
    }
    # include authen so templates can show login-only UI
    context['authen'] = getAuthen(request)
    return render(request, 'pages/discussions/discussion_detail.html', context)


def discussion_create(request):
    """Handle form POST from website to create a discussion via the discussions-service API.

    Expects POST keys: 'author', 'title', 'body'. Redirects to the list view on success.
    """
    if request.method == 'POST':
        form_author = request.POST.get('author', '').strip()
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        authen = getAuthen(request)
        # prefer logged-in user's email/name when available
        author = authen.get('user_email') or form_author or 'Anonymous'

        # Minimal validation
        if title and body:
            payload = {'author': author, 'title': title, 'body': body}
            if authen.get('user_id'):
                payload['creator_id'] = authen.get('user_id')
            try:
                createDiscussion_model(payload)
                # Successful create
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'ok': True}, status=201)
                return redirect('discussions')
            except Exception as exc:
                # API error
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'ok': False, 'error': 'Upstream service error.'}, status=502)
                # otherwise fall through to redirect
                pass
        else:
            # Validation failed
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'error': 'Title and body are required.'}, status=400)

    # Default fallback for non-POST or non-AJAX
    return redirect('discussions')


def comment_create(request, pk):
    """Handle POST from discussion detail to create a new comment via the discussions-service API.

    Expects POST keys: 'author', 'body'. Redirects back to discussion detail.
    """
    if request.method == 'POST':
        form_author = request.POST.get('author', '').strip()
        body = request.POST.get('body', '').strip()
        authen = getAuthen(request)
        author = authen.get('user_email') or form_author or 'Anonymous'
        if body:
            payload = {'discussion': pk, 'author': author, 'body': body}
            if authen.get('user_id'):
                payload['creator_id'] = authen.get('user_id')
            try:
                # Import locally to avoid circular import risks
                from .models import createComment_model
                createComment_model(payload)
            except Exception:
                # swallow errors for now; could add messages
                pass

    return redirect('discussion_detail', pk=pk)


def course_discussion_detail(request, course_subject, course_id):
    discussion = get_course_discussion_model(course_subject, course_id)
    comments = get_course_comments_model(course_subject, course_id)

    context = {
        'discussion': discussion,
        'comments': comments,
        'course_subject': course_subject,
        'course_id': course_id,
    }
    return render(request, 'pages/courses/course_discussion_detail.html', context)


def course_comment_create(request, course_subject, course_id):
    """Handle POST from course discussion detail to create a new comment."""
    if request.method == 'POST':
        author = request.POST.get('author', '').strip() or 'Anonymous'
        body = request.POST.get('body', '').strip()
        discussion_id = request.POST.get('discussion_id')

        if body and discussion_id:
            authen = getAuthen(request)
            payload = {'discussion': discussion_id, 'author': author, 'body': body}
            if authen.get('user_id'):
                payload['creator_id'] = authen.get('user_id')
            try:
                create_course_comment_model(payload)
            except Exception:
                # swallow errors for now; could add messages
                pass

    return redirect('course_discussion_detail', course_subject=course_subject, course_id=course_id)

def removeDiscussion(request, id):
    """
    Handle discussion deletion by ID via the discussions-service API.
    Confirm deletion via a GET request and process deletion via POST.
    """
    if request.method == 'POST':
        headers = {
            "Authorization": f"Bearer {request.session.get('access_token')}",
                "Content-Type": "application/json",
                "X-User-ID": str(request.session.get('user_id') or '')
        }
        try:
            removeDiscussion_model(id, headers)
            return redirect('discussions')
        except requests.RequestException as e:
            return JsonResponse({'error': 'Failed to delete discussion. Please try again later.'}, status=500)

    # For GET requests, render a confirmation page
    discussion = getDiscussionByID_model(id)
    authen = getAuthen(request)
    return render(request, 'pages/discussions/discussion_remove_confirm.html', {
        'discussion': discussion,
        'authen': authen
    })