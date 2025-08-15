import json
import glob
import os

class LexiconManager:
    def __init__(self):
        if not os.path.exists('lexicons'):
            os.makedirs('lexicons')
        self.lexicon_files = glob.glob(os.path.join('lexicons', '*_lexicon.json'))
        
import json

def load_all_lexicons():
    """Load all artist lexicon files as separate variables"""
    with open("lexicon/taylor swift.json", "r", encoding="utf-8") as f:
        taylor_swift = json.load(f)
    with open("lexicon/ed sheran.json", "r", encoding="utf-8") as f:
        ed_sheran = json.load(f)
    
    return taylor_swift, ed_sheran

def build_artist_song_map(*artist_lexicons):
    """Build a mapping of all songs with their artists"""
    song_map = []
    for artist_data in artist_lexicons:
        artist = artist_data.get("artist", "")
        for song in artist_data.get("songs", []):
            song["artist"] = artist
            song_map.append(song)
    return song_map