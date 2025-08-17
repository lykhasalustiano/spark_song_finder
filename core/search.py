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
    
