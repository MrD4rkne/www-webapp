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

KEEP_ALIVE_INTERVAL = 15 # seconds

# A dictionary to store active clients
# This is a simple in-memory solution for this lab
# In production, you would use something like Redis
active_clients = {}

def add_event(event_type, data):
    """
    Add an event to the queue to be sent to all connected clients.
    """
    event = {
        "event": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    print(f"Adding event: {event}")

    with event_condition:
        for client_id in active_clients:
            active_clients[client_id].append(event)
            # Notify waiting threads
            event_condition.notify_all()
    return event


from threading import Condition

# A condition variable to signal new events
event_condition = Condition()

def event_stream():
    """
    Generator function that yields SSE formatted data
    """
    client_id = uuid.uuid4().hex
    active_clients[client_id] = []

    try:
        # Send a welcome message
        yield f"data: {json.dumps({'message': 'Connected to SSE stream'})}\n\n"
        
        while True:
            with event_condition:
                # Wait for a signal or timeout
                event_condition.wait(timeout=KEEP_ALIVE_INTERVAL)

            if active_clients[client_id]:
                event = active_clients[client_id].pop(0)
                yield f"event: {event['event']}\n"
                yield f"data: {json.dumps(event['data'])}\n\n"
            else:
                # Send keep-alive if no events
                yield ": keep-alive\n\n"
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