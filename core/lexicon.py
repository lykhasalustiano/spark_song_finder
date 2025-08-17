import json
import glob
import os

class LexiconManager:
    def __init__(self):
        # Get absolute path to the lexicons directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.lexicon_dir = os.path.join(current_dir, 'lexicons')
        
        if not os.path.exists(self.lexicon_dir):
            os.makedirs(self.lexicon_dir)
            print(f"Created lexicons directory at: {self.lexicon_dir}")
        else:
            print(f"Found lexicons directory at: {self.lexicon_dir}")
        
    def load_all_lexicons(self):
        combined_data = {"songs": []}
        
        # Look for any .json files in lexicons directory
        json_files = glob.glob(os.path.join(self.lexicon_dir, '*.json'))
        
        if not json_files:
            print(f"No JSON files found in {self.lexicon_dir}")
            return combined_data
        
        for file_path in json_files:
            print(f"Loading: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    artist_data = json.load(f)
                    # Add artist to each song
                    for song in artist_data.get("songs", []):
                        song["artist"] = artist_data["artist"]
                        combined_data["songs"].append(song)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        print(f"Total songs loaded: {len(combined_data['songs'])}")
        return combined_data
    
def build_artist_song_map(*artist_lexicons):
    """Build a mapping of all songs with their artists"""
    song_map = []
    for artist_data in artist_lexicons:
        artist = artist_data.get("artist", "")
        for song in artist_data.get("songs", []):
            song["artist"] = artist
            song_map.append(song)
    return song_map