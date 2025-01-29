import React, { useState, useRef } from "react";

interface AudioRecorderProps {
    wsUrl: string; // WebSocket URL passed as a prop
}

const AudioRecorder: React.FC<AudioRecorderProps> = ({ wsUrl }) => {
    const [socket, setSocket] = useState<WebSocket | null>(null);
    const mediaRecorder = useRef<MediaRecorder | null>(null);
    const [isRecording, setIsRecording] = useState(false);

    // Function to start recording
    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder.current = new MediaRecorder(stream);
            const ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                console.log("WebSocket connected.");
                setSocket(ws);
                mediaRecorder.current?.start(1000); // Send audio every second
                setIsRecording(true);
            };

            mediaRecorder.current.ondataavailable = (event) => {
                if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
                    ws.send(event.data);
                }
            };

            ws.onclose = () => {
                console.log("WebSocket disconnected.");
                stopRecording();
            };

        } catch (error) {
            console.error("Error accessing microphone:", error);
        }
    };

    // Function to stop recording
    const stopRecording = () => {
        if (mediaRecorder.current) {
            mediaRecorder.current.stop();
            mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
        }
        if (socket) {
            socket.close();
            setSocket(null);
        }
        setIsRecording(false);
    };

    return (
        <div className="flex flex-col items-center space-y-4 p-4">
            <h2 className="text-xl font-bold">Live Audio Streaming</h2>
            <button 
                className={`px-4 py-2 rounded ${isRecording ? "bg-red-500" : "bg-green-500"} text-white`} 
                onClick={isRecording ? stopRecording : startRecording}
            >
                {isRecording ? "Stop Recording" : "Start Recording"}
            </button>
        </div>
    );
};

export default AudioRecorder;
