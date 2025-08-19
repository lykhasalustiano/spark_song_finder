import whisper
import pyaudio
import numpy as np
import json
from difflib import get_close_matches
import re
from collections import defaultdict
import time
from core.lexicon import LexiconManager

class SongFinder:
    def __init__(self, whisper_model_size="base"):
        self.lexicon_manager = LexiconManager()
        self.song_data = self.lexicon_manager.load_all_lexicons()
        
        # Initialize Whisper model
        self.whisper_model = whisper.load_model(whisper_model_size)
        
        # Initialize PyAudio for voice recording
        self.audio = pyaudio.PyAudio()
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.channels = 1
        self.format = pyaudio.paInt16
        
        # Build search index
        self.ngram_index = self._build_ngram_index()

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

    def load_all_lexicons(self):
        """Load all lexicons through the manager"""
        return self.lexicon_manager.load_all_lexicons()

    def _build_ngram_index(self, n=3):
        """Build an n-gram index for better fuzzy matching"""
        index = defaultdict(list)
        for song_idx, song in enumerate(self.song_data["songs"]):
            # Index title, artist, and first line of lyrics
            texts_to_index = [
                song.get('Title', ''),
                song.get('Artist', ''),
                song.get('Lyric', '').split('\n')[0] if song.get('Lyric') else ''
            ]
            
            for text in texts_to_index:
                text = text.lower()
                words = re.findall(r'\w+', text)
                for i in range(len(words) - n + 1):
                    ngram = ' '.join(words[i:i+n])
                    index[ngram].append(song_idx)
        return index

    def _ngram_search(self, query, n=3, threshold=0.6):
        """Search using n-gram similarity"""
        query = query.lower()
        query_words = re.findall(r'\w+', query)
        query_ngrams = set()
        
        for i in range(len(query_words) - n + 1):
            query_ngrams.add(' '.join(query_words[i:i+n]))
        
        song_matches = defaultdict(int)
        for ngram in query_ngrams:
            for song_idx in self.ngram_index.get(ngram, []):
                song_matches[song_idx] += 1
        
        # Calculate similarity scores
        results = []
        for song_idx, count in song_matches.items():
            similarity = count / max(len(query_ngrams), 1)
            if similarity >= threshold:
                results.append((similarity, self.song_data["songs"][song_idx]))
        
        return [song for (score, song) in sorted(results, reverse=True)]

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
            result = self.whisper_model.transcribe(audio_data, language="en")
            query = result["text"].strip()
            
            print(f"You said: {query}")
            return query if query else None
            
        except Exception as e:
            print(f"Unexpected error during voice recognition: {e}")
            return None

    def search_songs(self, query):
        """Multi-stage search with exact, n-gram, and fuzzy matching"""
        if not query:
            return []
        
        query = query.lower()
        results = []
        
        # Stage 1: Exact matches
        for song in self.song_data["songs"]:
            if (query in song.get("Title", "").lower() or 
                query in song.get("Artist", "").lower() or 
                query in song.get("Lyric", "").lower()):
                results.append(song)
        
        if results:
            return results
        
        # Stage 2: N-gram matching
        ngram_results = self._ngram_search(query)
        if ngram_results:
            return ngram_results
        
        # Stage 3: Fuzzy matching
        all_terms = []
        song_map = {}
        for song in self.song_data["songs"]:
            terms = [
                song.get("Title", "").lower(),
                song.get("Artist", "").lower(),
                *song.get("Lyric", "").lower().split()[:10]
            ]
            for term in terms:
                if term:  # Skip empty terms
                    all_terms.append(term)
                    song_map[term] = song
        
        close_matches = get_close_matches(query, all_terms, n=10, cutoff=0.3)
        seen_songs = set()
        results = []
        for match in close_matches:
            song = song_map[match]
            song_id = f"{song.get('Title', '')}_{song.get('Artist', '')}"
            if song_id not in seen_songs:
                results.append(song)
                seen_songs.add(song_id)
        
        return results
    
    def __del__(self):
        """Clean up PyAudio resources"""
        if hasattr(self, 'audio'):
            self.audio.terminate()