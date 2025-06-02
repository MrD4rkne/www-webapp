import json
import time
import uuid
from datetime import datetime
from django.http import StreamingHttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages

# A dictionary to store active clients
# This is a simple in-memory solution for this lab
# In production, you would use something like Redis
active_clients = {}

# A simple queue to store events that need to be sent
event_queue = []


def add_event(event_type, data):
    """
    Add an event to the queue to be sent to all connected clients.
    """
    event = {
        "event": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    event_queue.append(event)
    return event


def event_stream():
    """
    Generator function that yields SSE formatted data
    """
    # Generate a unique client ID
    client_id = str(datetime.now().timestamp())
    active_clients[client_id] = True
    
    try:
        # Send a welcome message
        yield f"data: {json.dumps({'message': 'Connected to SSE stream'})}\n\n"
        
        while True:
            # Check if there are any events to send
            if event_queue:
                event = event_queue.pop(0)
                yield f"event: {event['event']}\n"
                yield f"data: {json.dumps(event['data'])}\n\n"
            else:
                # Send a keep-alive comment every 15 seconds
                yield ": keep-alive\n\n"
                
            # Sleep to prevent excessive CPU usage
            time.sleep(3)
    finally:
        # Remove client when connection is closed
        if client_id in active_clients:
            del active_clients[client_id]


@method_decorator(csrf_exempt, name='dispatch')
class SSENotificationsView(View):
    """
    Server-Sent Events view that maintains a persistent connection 
    and sends events to the client.
    """
    def get(self, request, *args, **kwargs):
        response = StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream'
        )
        # Add headers to ensure proper SSE behavior
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'  # Disable buffering in Nginx
        return response


class SSEDemoView(TemplateView):
    """
    Demo view that shows a UI for testing SSE notifications
    """
    template_name = 'notifications/sse.html'


class SSETestView(TemplateView):
    """
    View for testing SSE events manually
    """
    template_name = 'notifications/test.html'


class TriggerTestEventView(View):
    """
    View to manually trigger SSE events for testing
    """
    def post(self, request, *args, **kwargs):
        event_type = request.POST.get('event_type')
        
        if event_type == 'newBoard':
            # Trigger a new board event
            data = {
                "board_id": str(uuid.uuid4()),
                "board_name": request.POST.get('board_name', 'Test Board'),
                "creator_username": request.POST.get('creator_username', 'TestUser')
            }
        elif event_type == 'newPath':
            # Trigger a new path event
            data = {
                "path_id": str(uuid.uuid4()),
                "board_id": request.POST.get('board_id', '123'),
                "board_name": request.POST.get('path_board_name', 'Test Board'),
                "user_username": request.POST.get('user_username', 'PathCreator')
            }
        else:
            messages.error(request, "Invalid event type")
            return HttpResponseRedirect(reverse('notifications:test'))
        
        # Add the event to the queue
        add_event(event_type, data)
        
        messages.success(request, f"Test {event_type} event sent successfully")
        return HttpResponseRedirect(reverse('notifications:test'))
