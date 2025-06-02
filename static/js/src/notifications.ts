const eventSource = new EventSource('/sse/notifications/');

function createToastContainer(): HTMLElement {
    const container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);

    const style = document.createElement('style');
    style.textContent = `
        #toast-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .toast {
            min-width: 250px;
            padding: 15px;
            border-radius: 4px;
            background-color: #333;
            color: white;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            opacity: 1;
            transition: opacity 0.5s;
        }
        .toast-info {
            background-color: #2196F3;
        }
        .toast-success {
            background-color: #4CAF50;
        }
        .toast-fade-out {
            opacity: 0;
        }
    `;
    document.head.appendChild(style);
    
    return container;
}

function showNotification(message: string, type: string = 'info'): void {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-fade-out');
        setTimeout(() => {
            toast.remove();
        }, 500);
    }, 5000);
}

eventSource.addEventListener('newBoard', (event) => {
    console.log('New board event received:', event);
    const data = JSON.parse(event.data);
    const message = `User ${data.creator_username} created a new board: ${data.board_name}.`;
    showNotification(message, 'success');
});

eventSource.addEventListener('newPath', (event) => {
    console.log('New path event received:', event);
    const data = JSON.parse(event.data);
    const message = `User ${data.user_username} created a solution on a board ${data.board_name}.`;
    showNotification(message, 'info');
});

eventSource.onopen = () => {
    console.log('Connection to SSE established');
};

eventSource.onerror = () => {
    console.error('Error occurred in SSE connection');
};

(window as any).notifications = {
    show: showNotification,
    closeConnection: () => eventSource.close()
};
