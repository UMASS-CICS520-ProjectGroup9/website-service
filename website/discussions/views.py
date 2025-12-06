from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .models import (
    discussionAPI,
    getDiscussionByID_model,
    getCommentsByDiscussion_model,
    createDiscussion_model,
    get_course_discussion_model,
    get_course_comments_model,
    create_course_comment_model,
)
import requests


def discussion_list(request):
    discussions = discussionAPI() or []
    # Paginate discussions: 10 per page
    page_number = request.GET.get('page', 1)
    paginator = Paginator(discussions, 10)
    page_obj = paginator.get_page(page_number)
    return render(request, 'pages/discussions/discussions.html', {
        'discussions': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
    })


def discussion_detail(request, pk):
    discussion = getDiscussionByID_model(pk)
    comments = getCommentsByDiscussion_model(pk)
    context = {
        'discussion': discussion,
        'comments': comments,
    }
    return render(request, 'pages/discussions/discussion_detail.html', context)


def discussion_create(request):
    """Handle form POST from website to create a discussion via the discussions-service API.

    Expects POST keys: 'author', 'title', 'body'. Redirects to the list view on success.
    """
    if request.method == 'POST':
        author = request.POST.get('author', '').strip()
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()

        # Minimal validation
        if title and body:
            payload = {'author': author or 'Anonymous', 'title': title, 'body': body}
            try:
                createDiscussion_model(payload)
            except Exception:
                # For now, ignore API errors and fall through to redirect (could show message)
                pass

    return redirect('discussions')


def comment_create(request, pk):
    """Handle POST from discussion detail to create a new comment via the discussions-service API.

    Expects POST keys: 'author', 'body'. Redirects back to discussion detail.
    """
    if request.method == 'POST':
        author = request.POST.get('author', '').strip() or 'Anonymous'
        body = request.POST.get('body', '').strip()
        if body:
            payload = {'discussion': pk, 'author': author, 'body': body}
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
            payload = {'discussion': discussion_id, 'author': author, 'body': body}
            try:
                create_course_comment_model(payload)
            except Exception:
                # swallow errors for now; could add messages
                pass

    return redirect('course_discussion_detail', course_subject=course_subject, course_id=course_id)