const CACHE_NAME = 'analytics-demo-v1';
const API_BASE_URL = 'http://localhost:8000';

// Install event
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    self.skipWaiting();
});

// Activate event
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...');
    event.waitUntil(self.clients.claim());
});

// Message event - handle messages from the main thread
self.addEventListener('message', (event) => {
    console.log('Service Worker received message:', event.data);

    if (event.data.type === 'SEND_EVENT') {
        sendEventToBackend(event.data.data, event.source);
    }
});

async function sendEventToBackend(eventData, source) {
    try {
        const response = await fetch(`${API_BASE_URL}/events`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(eventData)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        // Send success message back to the main thread
        source.postMessage({
            type: 'EVENT_SENT',
            data: result
        });

        console.log('Event sent successfully:', result);

    } catch (error) {
        console.error('Error sending event:', error);

        // Send error message back to the main thread
        source.postMessage({
            type: 'EVENT_ERROR',
            error: error.message
        });
    }
}
