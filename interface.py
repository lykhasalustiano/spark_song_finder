import tkinter as tk
from PIL import Image, ImageTk
import os
import sys

# Ensure imports work in all cases
try:
    from song_finder import SongFinder
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from song_finder import SongFinder

class SongFinderUI:
    def __init__(self, root):
        self.root = root
        self.song_finder = SongFinder()
        self.setup_ui()
    
    def setup_ui(self):
        self.root.title("Song Spark Finder")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#191414") 

        # HEADER
        header = tk.Frame(self.root, bg="#191414", height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # BORDER LINE
        border_line = tk.Frame(self.root, bg="#B3B3B3", height=1)
        border_line.pack(fill="x", side="top")

        # LOGO
        logo_path = r"C:\Users\lykha\spark_song_finder\icon\logo.png"
        logo_img = Image.open(logo_path).resize((80, 90), Image.LANCZOS)
        self.logo_icon = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(header, image=self.logo_icon, bg="#191414")
        logo_label.pack(side="right", padx=15, pady=5)

        # SEARCH BAR
        search_canvas = tk.Canvas(header, bg="#191414", highlightthickness=0, width=280, height=36)
        search_canvas.pack(side="left", padx=(15, 5), pady=12)

        # Search bar background
        self.create_rounded_rect(search_canvas, 0, 0, 280, 36, r=18, fill="#6D6D6D")

        # Search icon
        icon_path = r"C:\Users\lykha\spark_song_finder\icon\photo_2025-08-13_23-24-30-removebg-preview.png"
        icon_img = Image.open(icon_path).resize((20, 20), Image.LANCZOS)
        self.search_icon = ImageTk.PhotoImage(icon_img)
        search_canvas.create_image(15, 18, image=self.search_icon)

        # Divider line
        search_canvas.create_line(30, 6, 30, 30, fill="#B3B3B3", width=1)

        # Search entry
        placeholder = "Search for a song..."
        self.search_entry = tk.Entry(search_canvas, font=("Arial", 12), bg="#6D6D6D", fg="#B3B3B3",
                                    borderwidth=0, insertbackground="white", width=22)
        self.search_entry.place(x=40, y=7)
        self.search_entry.insert(0, placeholder)

        # Placeholder behavior
        def on_entry_click(event):
            if self.search_entry.get() == placeholder:
                self.search_entry.delete(0, "end")
                self.search_entry.config(fg="white")

        def on_focus_out(event):
            if self.search_entry.get() == "":
                self.search_entry.insert(0, placeholder)
                self.search_entry.config(fg="#B3B3B3")

        self.search_entry.bind("<FocusIn>", on_entry_click)
        self.search_entry.bind("<FocusOut>", on_focus_out)

        # Microphone icon
        mic_path = r"C:\Users\lykha\spark_song_finder\icon\microphone-removebg-preview.png"
        mic_img = Image.open(mic_path).resize((26, 26), Image.LANCZOS)
        self.mic_icon = ImageTk.PhotoImage(mic_img)
        self.mic_label = tk.Label(header, image=self.mic_icon, bg="#191414")
        self.mic_label.pack(side="left", pady=10)

        # SUGGESTION CONTAINER
        suggestion_width = 570
        suggestion_height = 190
        window_width = 600
        center_x = (window_width - suggestion_width) // 2

        self.suggestion_canvas = tk.Canvas(self.root, bg="#191414", highlightthickness=0,
                                          width=suggestion_width, height=suggestion_height)
        self.suggestion_canvas.place(x=center_x, y=85)

        # Initial suggestion box
        self.create_rounded_rect(self.suggestion_canvas, 5, 5, suggestion_width-5, suggestion_height, r=5, fill="#101010")  
        self.create_rounded_rect(self.suggestion_canvas, 0, 0, suggestion_width-5, suggestion_height-5, r=5, fill="#6D6D6D")
        self.suggestion_canvas.create_text(suggestion_width//2, suggestion_height//2,
                                          text="Suggested songs will appear here...",
                                          font=("Arial", 14), fill="white")

        # Connect UI elements
        self.mic_label.bind("<Button-1>", self.on_voice_search)
        self.search_entry.bind("<Return>", self.on_text_search)

        # Store song canvases
        self.song_canvases = []

    def create_rounded_rect(self, canvas, x1, y1, x2, y2, r=18, **kwargs):
        points = [
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    def on_voice_search(self, event):
        # Show listening state
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Listening... Speak now")
        self.search_entry.config(fg="white")
        self.root.update()
        
        # Capture voice input
        query = self.song_finder.listen_for_search()
        
        if query:
            # Expand query for better matching
            expanded_query = self.song_finder.expand_voice_query(query)
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, expanded_query)
            self.display_results(expanded_query)
        else:
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, "Could not understand voice input")
            self.search_entry.config(fg="#ff4444")
            self.root.after(2000, lambda: self.search_entry.delete(0, tk.END))

    def on_text_search(self, event):
        query = self.search_entry.get()
        if query and query != "Search for a song...":
            self.display_results(query)

    def display_results(self, query):
        # Clear previous results
        for canvas in self.song_canvases:
            canvas.destroy()
        self.song_canvases = []

        results = self.song_finder.search_songs(query)
        print(f"Search for '{query}' returned {len(results)} results")  # Debug
        
        if not results:
            self.show_no_results()
            return

        # Update suggestion box with first result
        self.update_suggestion_box(results[0])

        # Show all results in song containers
        self.show_search_results(results)

    def update_suggestion_box(self, song):
        self.suggestion_canvas.delete("all")
        
        # Background
        self.create_rounded_rect(self.suggestion_canvas, 5, 5, 565, 185, r=5, fill="#101010")  
        self.create_rounded_rect(self.suggestion_canvas, 0, 0, 565, 180, r=5, fill="#6D6D6D")
        
        # Song info
        self.suggestion_canvas.create_text(100, 40, 
                                         text=song['title'], 
                                         font=("Arial", 16, "bold"), 
                                         fill="white", 
                                         anchor="w")
        
        self.suggestion_canvas.create_text(100, 70, 
                                         text=f"by {song['artist']}", 
                                         font=("Arial", 12), 
                                         fill="#B3B3B3", 
                                         anchor="w")
        
        # Fix for f-string with newline
        lyrics_lines = song['lyrics'].split('\n')
        first_line = lyrics_lines[0][:60] + "..." if lyrics_lines else ""
        self.suggestion_canvas.create_text(100, 100, 
                                         text=first_line, 
                                         font=("Arial", 12), 
                                         fill="white", 
                                         anchor="w",
                                         width=400)

    def show_no_results(self):
        self.suggestion_canvas.delete("all")
        self.create_rounded_rect(self.suggestion_canvas, 5, 5, 565, 185, r=5, fill="#101010")  
        self.create_rounded_rect(self.suggestion_canvas, 0, 0, 565, 180, r=5, fill="#6D6D6D")
        self.suggestion_canvas.create_text(282, 90, 
                                         text="No songs found matching your search", 
                                         font=("Arial", 14), 
                                         fill="white")

    def show_search_results(self, results):
        song_container_width = 570
        song_container_height = 40
        song_gap = 10
        start_y = 300
        center_x = (600 - song_container_width) // 2

        for i, song in enumerate(results):
            y_pos = start_y + i * (song_container_height + song_gap)
            
            song_canvas = tk.Canvas(self.root, bg="#191414", highlightthickness=0,
                                  width=song_container_width, height=song_container_height)
            song_canvas.place(x=center_x, y=y_pos)
            
            # Rounded rectangle container
            rect_id = self.create_rounded_rect(song_canvas, 0, 0, song_container_width, 
                                             song_container_height, r=5, fill="#6D6D6D")
            
            # Song info
            song_canvas.create_text(20, 20, 
                                  text=f"{song['title']} - {song['artist']}", 
                                  font=("Arial", 12), 
                                  fill="white",
                                  anchor="w")
            
            # Store reference to the song
            song_canvas.song_data = song
            
            # Bind click event
            song_canvas.bind("<Button-1>", lambda e, s=song: self.on_song_click(s))
            
            # Bind hover effect
            song_canvas.bind("<Enter>", lambda e, c=song_canvas, r=rect_id: 
                           self.on_enter(e, c, r))
            song_canvas.bind("<Leave>", lambda e, c=song_canvas, r=rect_id: 
                           self.on_leave(e, c, r))
            
            self.song_canvases.append(song_canvas)

    def on_song_click(self, song):
        """Handle song selection"""
        self.update_suggestion_box(song)

    def on_enter(self, event, canvas, rect_id):
        canvas.itemconfig(rect_id, fill="#808080")

    def on_leave(self, event, canvas, rect_id):
        canvas.itemconfig(rect_id, fill="#6D6D6D")