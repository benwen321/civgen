// frontend/src/components/BasicWebSocketClient.tsx
import React, { useState, useEffect, useRef } from 'react';

function BasicWebSocketClient() {
    const [messages, setMessages] = useState<string[]>([]);
    const [inputMessage, setInputMessage] = useState('');
    const websocketRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        // Create WebSocket connection on component mount
        websocketRef.current = new WebSocket('ws://localhost:8000/ws'); // Backend WebSocket URL

        const ws = websocketRef.current;

        ws.onopen = () => {
            console.log('WebSocket connection opened in frontend');
            setMessages(prevMessages => [...prevMessages, 'Frontend: WebSocket connection opened']);
        };

        ws.onmessage = (event) => {
            console.log('Frontend received message:', event.data);
            setMessages(prevMessages => [...prevMessages, `Backend: ${event.data}`]);
        };

        ws.onerror = (error) => {
            console.error('Frontend WebSocket error:', error);
            setMessages(prevMessages => [...prevMessages, `Frontend: WebSocket Error - ${String(error)}`]);
        };

        ws.onclose = () => {
            console.log('WebSocket connection closed in frontend');
            setMessages(prevMessages => [...prevMessages, 'Frontend: WebSocket connection closed']);
        };

        // Cleanup on unmount
        return () => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.close();
            }
        };
    }, []); // Run effect only once on mount and unmount

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setInputMessage(event.target.value);
    };

    const sendMessage = () => {
        if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN && inputMessage.trim()) {
            websocketRef.current.send(inputMessage); // Send message to backend
            setMessages(prevMessages => [...prevMessages, `Frontend: You sent - ${inputMessage}`]);
            setInputMessage(''); // Clear input
        } else {
            alert('WebSocket is not open or message is empty.');
        }
    };

    return (
        <div>
            <h1>Basic WebSocket Client</h1>
            <div>
                <input
                    type="text"
                    value={inputMessage}
                    onChange={handleInputChange}
                    placeholder="Enter message"
                />
                <button onClick={sendMessage} disabled={!websocketRef.current || websocketRef.current.readyState !== WebSocket.OPEN}>
                    Send Message
                </button>
            </div>
            <div>
                <h2>Messages:</h2>
                <ul>
                    {messages.map((message, index) => (
                        <li key={index}>{message}</li>
                    ))}
                </ul>
            </div>
        </div>
    );
}

export default BasicWebSocketClient;