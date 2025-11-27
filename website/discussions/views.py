from django.shortcuts import render, redirect
from .models import (
    discussionAPI,
    getDiscussionByID_model,
    getCommentsByDiscussion_model,
    createDiscussion_model,
)


def discussion_list(request):
    discussions = discussionAPI()
    return render(request, 'pages/discussions/discussions.html', {'discussions': discussions})


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