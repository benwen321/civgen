import AudioRecorder from './AudioRecorder';

function App() {
  const wsUrl = import.meta.env.VITE_WS_URL;
  
  return (
    <div>
      <h1>My React App</h1>
      <AudioRecorder wsUrl={wsUrl} />
    </div>
  );
}

export default App;
