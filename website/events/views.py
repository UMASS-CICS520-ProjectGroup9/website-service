from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods
import requests
from .models import posts, getEventByID_model
from .models import eventAPI, createEvent_model, removeEvent_model

# Configuration for external API
EXTERNAL_API_BASE_URL = "https://api.example.com/v1"  # Replace with actual API URL
API_KEY = ""  # Better to get from settings.py or environment variables

def events(request):
    events = eventAPI()
    return render(request, 'pages/events/events.html', {'eventAPI': events})

def getEventByID(request, id):
    event = getEventByID_model(id)
    return render(request, 'pages/events/singleEvent.html', {'event': event})

def eventForm(request):
    return render(request, 'pages/events/event_form.html')

@require_http_methods(["GET", "POST"])
def eventFormCreation(request):
    """
    Handle event form submission to external API service.
    GET: Display the form
    POST: Submit to external API
    """
    
    if request.method == 'POST':
        
        try:
            # Parse form data similar to our local implementation
            form_data = {
                'title': request.POST.get('title'),
                'description': request.POST.get('description'),
                'creator': request.POST.get('creator'),
                'eventType': request.POST.get('eventType'),
                'location': request.POST.get('location'),
                'capacity': int(request.POST.get('capacity', 0)),
                'link': request.POST.get('link') or None,
                'zoom_link': request.POST.get('zoom_link') or None,
                'hosted_by': request.POST.get('hosted_by'),
                'event_start_date': request.POST.get('event_start_date'),
                'event_end_date': request.POST.get('event_end_date'),
            }

            # Handle registered_students
            students_raw = request.POST.get('registered_students', '')
            if students_raw:
                form_data['registered_students'] = [
                    int(s.strip()) if s.strip().isdigit() else s.strip()
                    for s in students_raw.split(',')
                    if s.strip()
                ]
            else:
                form_data['registered_students'] = []

            # Headers for the external API
            # headers = {
            #     'Authorization': f'Bearer {API_KEY}',
            #     'Content-Type': 'application/json',
            #     'Accept': 'application/json'
            # }

            # First, create the event using POST
            # create_response = requests.post(
            #     f"{EXTERNAL_API_BASE_URL}/api/events/create/",
            #     json=form_data,
            #     headers=headers
            # )
            created_event = createEvent_model(form_data)
            print("Created event response:", created_event)
            event_id = created_event.get('eventID')
            if not event_id:
                raise ValueError("Event ID not returned from API.")
            # On success, redirect to the event detail page
            return redirect('getEventByID', id=event_id)
        
        except requests.RequestException as e:
            error_message = f"API Error: {str(e)}"
            if hasattr(e.response, 'json'):
                try:
                    error_detail = e.response.json()
                    error_message = error_detail.get('detail', error_message)
                except ValueError:
                    pass

            # if request.headers.get('HX-Request'):
            #     return HttpResponse(
            #         render_to_string('base/partials/form_error.html',
            #                        {'error': error_message}),
            #         status=400,
            #         content_type='text/html'
            #     )
            return JsonResponse({'error': error_message}, status=400)

        except ValueError as e:
            error_message = f"Validation error: {str(e)}"
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    render_to_string('pages/events/form_error.html',
                                   {'error': error_message}),
                    status=400,
                    content_type='text/html'
                )
            return JsonResponse({'error': error_message}, status=400)

    # GET request - show the form
    return redirect('eventForm')


def removeEvent(request, id):
    """
    Remove an event by ID via external API.
    """
    result = removeEvent_model(id)
    return redirect('/events/')
