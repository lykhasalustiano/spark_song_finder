import speech_recognition as sr
import time

class VoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.microphone = None
        self._initialize_microphone()
    
    def _initialize_microphone(self):
        """Initialize microphone with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.microphone = sr.Microphone()
                print("Microphone initialized successfully")
                return
            except Exception as e:
                print(f"Microphone initialization attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
        print("Could not initialize microphone after multiple attempts")
    
    def listen_for_search(self):
        """Capture voice input with improved error handling"""
        if not self.microphone:
            print("Microphone not available for voice search")
            return None
            
        print("Listening for your song search... (speak now)")
        try:
            with self.microphone as source:
                # Longer adjustment for better noise handling
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print("Speak now...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            print("Processing your speech...")
            query = self.recognizer.recognize_google(audio)
            print(f"You said: {query}")
            return query
        except sr.WaitTimeoutError:
            print("Listening timed out. Please try again.")
            return None
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during voice recognition: {e}")
            return None