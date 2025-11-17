from django.shortcuts import render
from .models import discussionAPI, getDiscussionByID_model, getCommentsByDiscussion_model

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