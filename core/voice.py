import whisper
import pyaudio
import wave
import numpy as np
import time
import tempfile
import os

class VoiceRecognizer:
    def __init__(self, model_size="base"):
        """ 
        Initialize Whisper voice recognizer
        model_size: "tiny", "base", "small", "medium", "large"
        """
        self.model = whisper.load_model(model_size)
        self.audio = pyaudio.PyAudio()
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.channels = 1
        self.format = pyaudio.paInt16
    
    def record_audio(self, record_seconds=5):
        """Record audio using PyAudio directly"""
        try:
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            print("Listening... (speak now)")
            frames = []
            
            for _ in range(0, int(self.sample_rate / self.chunk_size * record_seconds)):
                data = stream.read(self.chunk_size)
                frames.append(data)
            
            print("Recording finished")
            stream.stop_stream()
            stream.close()
            
            # Convert to numpy array for Whisper
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            audio_data = audio_data.astype(np.float32) / 32768.0  # Normalize to [-1, 1]
            
            return audio_data
            
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None
    
    def listen_for_search(self):
        """Capture voice input using Whisper with direct PyAudio recording"""
        print("Listening for your song search...")
        
        try:
            # Record audio
            audio_data = self.record_audio(record_seconds=5)
            if audio_data is None:
                return None
            
            print("Processing your speech with Whisper...")
            
            # Transcribe with Whisper
            result = self.model.transcribe(audio_data, language="en")
            query = result["text"].strip()
            
            print(f"You said: {query}")
            return query if query else None
            
        except Exception as e:
            print(f"Unexpected error during voice recognition: {e}")
            return None
    
    def __del__(self):
        """Clean up PyAudio resources"""
        if hasattr(self, 'audio'):
            self.audio.terminate()