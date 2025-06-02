# Server-Sent Events (SSE) Implementation

This module provides real-time notifications for the Django application using Server-Sent Events (SSE).

## Features

- Real-time notifications for new boards and paths (solutions)
- Persistent connection with keep-alive support
- Django signals integration for automatic event dispatching
- Simple client-side API using native EventSource

## Endpoints

- `/sse/notifications/` - The SSE endpoint that clients connect to
- `/sse/` - A demo page showing real-time events
- `/sse/test/` - A page to manually trigger test events

## Event Types

### New Board Event

```json
{
  "event": "newBoard",
  "data": {
    "board_id": "123",
    "board_name": "Example Board",
    "creator_username": "username"
  }
}
```

### New Path (Solution) Event

```json
{
  "event": "newPath",
  "data": {
    "path_id": "456",
    "board_id": "123",
    "board_name": "Example Board",
    "user_username": "solver"
  }
}
```

## Usage in Templates

```html
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Connect to the SSE endpoint
        const eventSource = new EventSource('/sse/notifications/');
        
        // Handle generic messages
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            console.log('Generic message:', data);
        };
        
        // Handle new board events
        eventSource.addEventListener('newBoard', function(event) {
            const data = JSON.parse(event.data);
            console.log('New board created:', data);
        });
        
        // Handle new path events
        eventSource.addEventListener('newPath', function(event) {
            const data = JSON.parse(event.data);
            console.log('New solution submitted:', data);
        });
        
        // Handle connection errors
        eventSource.onerror = function(error) {
            console.error('SSE connection error:', error);
        };
    });
</script>
```

## Notes on Implementation

- Simple in-memory queue for events (would use Redis or similar in production)
- Keep-alive comments sent every few seconds
- Logging of all SSE events for debugging purposes
