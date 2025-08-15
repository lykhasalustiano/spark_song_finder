from difflib import get_close_matches
import re
from collections import defaultdict

class EnhancedSongSearcher:
    def __init__(self, song_data):
        self.song_data = song_data
        self.ngram_index = self._build_ngram_index()
        
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
    
    def search_songs(self, query):
        """Search songs with multi-stage matching"""
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