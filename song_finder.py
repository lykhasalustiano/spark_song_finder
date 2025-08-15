import speech_recognition as sr
import json
import glob
import os
from difflib import get_close_matches
import re
from collections import defaultdict
import time

class SongFinder:
    def __init__(self):
        # Create lexicons directory if it doesn't exist
        if not os.path.exists('lexicons'):
            os.makedirs('lexicons')
            
        self.lexicon_files = glob.glob(os.path.join('lexicons', '*_lexicon.json'))
        self.song_data = self.load_all_lexicons()
        
        # Initialize voice recognition with better error handling
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.microphone = self._initialize_microphone()
        
        # Build n-gram index for better search
        self.ngram_index = self._build_ngram_index()

    def _initialize_microphone(self):
        """Initialize microphone with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                mic = sr.Microphone()
                print("Microphone initialized successfully")
                return mic
            except Exception as e:
                print(f"Microphone initialization attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
        print("Could not initialize microphone after multiple attempts")
        return None

    def load_all_lexicons(self):
        all_songs = {"songs": []}
        if not self.lexicon_files:
            print("No lexicon files found in lexicons/ folder")
            print("Please add artist lexicon files in the format: lexicons/<artist>_lexicon.json")
            return all_songs
        
        for file in self.lexicon_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    artist_data = json.load(f)
                    for song in artist_data.get("songs", []):
                        song["artist"] = artist_data["artist"]
                        all_songs["songs"].append(song)
            except Exception as e:
                print(f"Error loading {file}: {e}")
        return all_songs

    def _build_ngram_index(self, n=3):
        """Build an n-gram index for better fuzzy matching"""
        index = defaultdict(list)
        for song_idx, song in enumerate(self.song_data["songs"]):
            # Index title, artist, and first line of lyrics
            for text in [song['title'], song['artist'], song['lyrics'].split('\n')[0]]:
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
            return self.expand_voice_query(query)
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

    def expand_voice_query(self, query):
        """Expand voice queries for better matching"""
        if not query:
            return query
            
        # Simple expansion - can be enhanced further
        expansions = {
            "tay swift": "taylor swift",
            "ed sheer": "ed sheeran",
            "shape of": "shape of you",
            "love store": "love story",
            "blank sp": "blank space",
            "shake it": "shake it off",
            "think out": "thinking out loud",
            "bad hab": "bad habits"
        }
        return expansions.get(query.lower(), query)

    def search_songs(self, query):
        """Multi-stage search with exact, n-gram, and fuzzy matching"""
        if not query:
            return []
        
        query = query.lower()
        results = []
        
        # Stage 1: Exact matches
        for song in self.song_data["songs"]:
            if (query in song["artist"].lower() or 
                query in song["title"].lower() or 
                query in song["lyrics"].lower()):
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
                song["title"].lower(),
                song["artist"].lower(),
                *song["lyrics"].lower().split()[:10]
            ]
            for term in terms:
                all_terms.append(term)
                song_map[term] = song
        
        close_matches = get_close_matches(query, all_terms, n=5, cutoff=0.4)
        seen_songs = set()
        for match in close_matches:
            song = song_map[match]
            if song["title"] not in seen_songs:
                results.append(song)
                seen_songs.add(song["title"])
        
        return results