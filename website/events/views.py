from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods
import requests
from .models import posts, getEventByID_model, eventSearchByKeywords_model, eventsSortedByCreationDate_model, eventsSortedByEndDate_model, eventsMultipleFiltersAndInput_model
from .models import eventAPI, createEvent_model, removeEvent_model, updateEvent_model, eventsSortedByStartDate_model, eventsSortedByUpdateDate_model



def events(request):
    events = eventAPI()
    is_login = "access_token" in request.session
    return render(request, 'pages/events/events.html', {'eventAPI': events, "is_login": is_login})

def getEventByID(request, id):
    event = getEventByID_model(id)
    is_login = "access_token" in request.session
    user_id = request.session.get('user_id')
    return render(request, 'pages/events/singleEvent.html', {'event': event, "is_login": is_login})

def eventForm(request):
    is_login = "access_token" in request.session
    if not is_login:
        return redirect("login")
    return render(request, 'pages/events/event_form.html',{"creator_id": request.session.get("user_id")})

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
                'creator_id':request.POST.get('creator_id'),
                'eventType': request.POST.get('eventType'),
                'location': request.POST.get('location'),
                'capacity': int(request.POST.get('capacity', 0)),
                'link': request.POST.get('link') or None,
                'zoom_link': request.POST.get('zoom_link') or None,
                'hosted_by': request.POST.get('hosted_by'),
                'event_start_date': request.POST.get('event_start_date'),
                'event_end_date': request.POST.get('event_end_date'),
            }
            headers = {
                "Authorization": f"Bearer {request.session.get('access_token')}",
                "Content-Type": "application/json"
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
            created_event = createEvent_model(form_data, headers)
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
    Ask user to make sure they want to remore.
    Remove an event by ID via external API.
    
    """
    if request.method == 'POST':
        removeEvent_model(id)
        return redirect('/events/')

    event = getEventByID_model(id)
    return render(request, 'pages/events/event_remove_confirm.html', {'event': event})


def eventFormUpdate(request, id):
    """
    Display and process the event update form for the event with the given ID and data for update.
    """
    def _format_for_datetime_local(dt_value):
        """
        Convert various datetime strings to the HTML datetime-local format (YYYY-MM-DDTHH:MM).
        Falls back to the original value if parsing fails.
        """
        if not dt_value:
            return dt_value
        if isinstance(dt_value, datetime):
            return dt_value.strftime("%Y-%m-%dT%H:%M")
        # Handle common ISO formats including trailing Z
        try:
            cleaned = str(dt_value).replace("Z", "+00:00")
            parsed = datetime.fromisoformat(cleaned)
            return parsed.strftime("%Y-%m-%dT%H:%M")
        except Exception:
            return dt_value
        
    def _handle_registered_students_format(regisStu):
        """
        Convert stored registered_students into a comma-separated string for the form.
        """
        if not regisStu:
            return ""
        if isinstance(regisStu, str):
            return regisStu
        try:
            result = ", ".join(str(s) for s in regisStu)
            print(result)
            return result
        except Exception:
            return str(regisStu)

    if request.method == 'POST':
        try:
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

            students_raw = request.POST.get('registered_students', '')
            if students_raw:
                form_data['registered_students'] = [
                    int(s.strip()) if s.strip().isdigit() else s.strip()
                    for s in students_raw.split(',')
                    if s.strip()
                ]
            else:
                form_data['registered_students'] = []

            updateEvent_model(id, form_data)
            return redirect('getEventByID', id=id)

        except requests.RequestException as e:
            error_message = f"API Error: {str(e)}"
            if hasattr(e.response, 'json'):
                try:
                    error_detail = e.response.json()
                    error_message = error_detail.get('detail', error_message)
                except ValueError:
                    pass

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

    event = getEventByID_model(id)
    event['event_start_date'] = _format_for_datetime_local(event.get('event_start_date'))
    event['event_end_date'] = _format_for_datetime_local(event.get('event_end_date'))
    event['registered_students'] = _handle_registered_students_format(event.get('registered_students'))
    return render(request, 'pages/events/event_update_form.html', {'event': event, 'is_update': True})


def eventSearchByKeywords(request):
    "Search all event by the input keywords"
    query = (request.GET.get('query') or request.GET.get('q') or "").strip()
    if not query:
        return redirect('events')
    events_data = eventSearchByKeywords_model(query)
    return render(request, 'pages/events/events.html', {'eventAPI': events_data, 'query': query})

def eventsSortedByCreationDate(request):
    events_data = eventsSortedByCreationDate_model()
    return render(request, 'pages/events/events.html', {'eventAPI': events_data})
    
    
def eventsSortedByStartDate(request):
    events_data = eventsSortedByStartDate_model()
    return render(request, 'pages/events/events.html', {'eventAPI': events_data})

def eventsSortedByEndDate(request):
    events_data = eventsSortedByEndDate_model()
    return render(request, 'pages/events/events.html', {'eventAPI': events_data})
    
def eventsSortedByUpdateDate(request):
    events_data = eventsSortedByUpdateDate_model()
    return render(request, 'pages/events/events.html', {'eventAPI': events_data})

def eventsMultipleFiltersAndInput(request):
    value = request.GET.get('value')
    filter = request.GET.get('filter')
    params = {
        filter : value,
        "limit": 10,
        "page": 1
    }
    events_data = eventsMultipleFiltersAndInput_model(params)
    return render(request, 'pages/events/events.html', {'eventAPI': events_data})