from django.shortcuts import render
from .models import discussionAPI, getDiscussionByID_model

def discussion_list(request):
    discussions = discussionAPI()
    return render(request, 'pages/discussions/discussions.html', {'discussions': discussions})

def discussion_detail(request, pk):
    discussion = getDiscussionByID_model(pk)
    return render(request, 'pages/discussions/discussion_detail.html', {'discussion': discussion})