import tkinter as tk
from PIL import Image, ImageTk
import os
import sys

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
        header_height = 60
        header = tk.Frame(self.root, bg="#191414", height=header_height)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # BORDER LINE
        border_height = 1
        border_line = tk.Frame(self.root, bg="#B3B3B3", height=border_height)
        border_line.pack(fill="x", side="top")

        # LOGO
        logo_path = r"icon/logo.png"
        logo_img = Image.open(logo_path).resize((80, 90), Image.LANCZOS)
        self.logo_icon = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(header, image=self.logo_icon, bg="#191414")
        logo_label.pack(side="right", padx=15, pady=5)

        # SEARCH BAR
        search_canvas = tk.Canvas(header, bg="#191414", highlightthickness=0, width=280, height=36)
        search_canvas.pack(side="left", padx=(15, 5), pady=12)
        self.create_rounded_rect(search_canvas, 0, 0, 280, 36, r=18, fill="#6D6D6D")

        icon_path = r"icon/search-bar.png"
        icon_img = Image.open(icon_path).resize((20, 20), Image.LANCZOS)
        self.search_icon = ImageTk.PhotoImage(icon_img)
        search_canvas.create_image(15, 18, image=self.search_icon)
        search_canvas.create_line(30, 6, 30, 30, fill="#B3B3B3", width=1)

        placeholder = "Search for a song..."
        self.search_entry = tk.Entry(search_canvas, font=("Arial", 12), bg="#6D6D6D", fg="#B3B3B3",
                                     borderwidth=0, insertbackground="white", width=22)
        self.search_entry.place(x=40, y=7)
        self.search_entry.insert(0, placeholder)

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
        mic_path = r"icon/microphone.png"
        mic_img = Image.open(mic_path).resize((26, 26), Image.LANCZOS)
        self.mic_icon = ImageTk.PhotoImage(mic_img)
        self.mic_label = tk.Label(header, image=self.mic_icon, bg="#191414")
        self.mic_label.pack(side="left", pady=10)

        # SUGGESTION BOX HEADING
        suggestion_width = 570
        suggestion_height = 160
        window_width = 600
        center_x = (window_width - suggestion_width) // 2

        self.suggestion_heading = tk.Label(self.root, text="Match Found", font=("Arial", 16, "bold"),
                                           bg="#191414", fg="white")
        heading_height = 30
        self.suggestion_heading.place(x=center_x, y=header_height + border_height + 10)

        # SUGGESTION BOX
        self.suggestion_canvas = tk.Canvas(self.root, bg="#191414", highlightthickness=0,
                                          width=suggestion_width, height=suggestion_height)
        self.suggestion_canvas.place(x=center_x, y=header_height + border_height + heading_height + 15)
        self.create_rounded_rect(self.suggestion_canvas, 5, 5, suggestion_width-5, suggestion_height, r=5, fill="#101010")  
        self.create_rounded_rect(self.suggestion_canvas, 0, 0, suggestion_width-5, suggestion_height-5, r=5, fill="#E8C999")
        self.suggestion_canvas.create_text(suggestion_width//2, suggestion_height//2,
                                          text="Match Song will appear here...",
                                          font=("Arial", 14), fill="black")

        # Bind suggestion box click
        self.suggestion_canvas.bind("<Button-1>", self.on_match_click)

        # Hover zoom effect for suggestion box
        self.suggestion_canvas.bind("<Enter>", self.on_suggestion_hover)
        self.suggestion_canvas.bind("<Leave>", self.on_suggestion_leave)

        # HEADING FOR OTHER RESULTS
        self.results_heading = tk.Label(self.root, text="Other Related Songs", font=("Arial", 16, "bold"),
                                        bg="#191414", fg="white")
        self.results_heading.place(x=center_x, y=header_height + border_height + suggestion_height + 55)

        # SCROLLABLE RESULTS
        self.results_frame = tk.Frame(self.root, bg="#191414")
        self.results_frame.place(x=center_x, y=header_height + border_height + suggestion_height + 85, width=570, height=360)

        self.results_canvas = tk.Canvas(self.results_frame, bg="#191414", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.results_frame, orient="vertical", command=self.results_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.results_canvas.pack(side="left", fill="both", expand=True)
        self.results_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.inner_frame = tk.Frame(self.results_canvas, bg="#191414")
        self.results_canvas.create_window((0,0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind("<Configure>", lambda e: self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all")))

        self.mic_label.bind("<Button-1>", self.on_voice_search)
        self.search_entry.bind("<Return>", self.on_text_search)

        self.song_canvases = []

    # Rounded rectangle helper
    def create_rounded_rect(self, canvas, x1, y1, x2, y2, r=18, **kwargs):
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2,
            x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    # Voice search
    def on_voice_search(self, event):
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Listening... Speak now")
        self.search_entry.config(fg="white")
        self.root.update()
        
        query = self.song_finder.listen_for_search()
        if query:
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, query)
            self.display_results(query)
        else:
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, "Could not understand voice input")
            self.search_entry.config(fg="#ff4444")
            self.root.after(2000, lambda: self.search_entry.delete(0, tk.END))

    # Text search
    def on_text_search(self, event):
        query = self.search_entry.get()
        if query and query != "Search for a song...":
            self.display_results(query)

    # Display results
    def display_results(self, query):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.song_canvases = []

        results = self.song_finder.search_songs(query)
        print(f"Search for '{query}' returned {len(results)} results")
        
        if not results:
            self.show_no_results()
            return

        self.update_suggestion_box(results[0])
        self.show_search_results(results)

    # Update suggestion box
    def update_suggestion_box(self, song):
        self.suggestion_canvas.delete("all")
        self.create_rounded_rect(self.suggestion_canvas, 5, 5, 565, 150, r=5, fill="#101010")  
        self.create_rounded_rect(self.suggestion_canvas, 0, 0, 565, 145, r=5, fill="#E8C999")
        self.suggestion_canvas.create_text(20, 40, text=song['Title'], font=("Arial", 18, "bold"), fill="black", anchor="w")
        self.suggestion_canvas.create_text(20, 80, text=f"by {song['Artist']}", font=("Arial", 14), fill="#2D2D2D", anchor="w")

        # Save current song for clicking
        self.current_suggestion_song = song

    # No results
    def show_no_results(self):
        self.suggestion_canvas.delete("all")
        self.create_rounded_rect(self.suggestion_canvas, 5, 5, 565, 150, r=5, fill="#101010")  
        self.create_rounded_rect(self.suggestion_canvas, 0, 0, 565, 145, r=5, fill="#6D6D6D")
        self.suggestion_canvas.create_text(282, 75, text="No songs found matching your search", font=("Arial", 14), fill="black")

    # Show search results
    def show_search_results(self, results):
        song_container_height = 60
        song_gap = 12

        for song in results:
            song_canvas = tk.Canvas(self.inner_frame, bg="#191414", highlightthickness=0, width=570, height=song_container_height)
            song_canvas.pack(pady=(0, song_gap))

            rect_id = self.create_rounded_rect(song_canvas, 0, 0, 570, song_container_height, r=5, fill="#E8C999")
            title_id = song_canvas.create_text(20, 20, text=song['Title'], font=("Arial", 14, "bold"), fill="black", anchor="w")
            artist_id = song_canvas.create_text(20, 40, text=song['Artist'], font=("Arial", 12), fill="#2D2D2D", anchor="w")

            song_canvas.song_data = song
            song_canvas.rect_id = rect_id
            song_canvas.title_id = title_id
            song_canvas.artist_id = artist_id

            song_canvas.bind("<Button-1>", lambda e, s=song: self.on_song_click(s))
            song_canvas.bind("<Enter>", lambda e, c=song_canvas: self.on_enter(e, c))
            song_canvas.bind("<Leave>", lambda e, c=song_canvas: self.on_leave(e, c))

            self.song_canvases.append(song_canvas)

    # Hover effects for results
    def on_enter(self, event, canvas):
        canvas.itemconfig(canvas.rect_id, fill="#EAE4D5")
        canvas.itemconfig(canvas.title_id, fill="black")
        canvas.itemconfig(canvas.artist_id, fill="#4A4A4A")
        canvas.scale("all", 0, 0, 1.05, 1.05)

    def on_leave(self, event, canvas):
        canvas.itemconfig(canvas.rect_id, fill="#E8C999")
        canvas.itemconfig(canvas.title_id, fill="black")
        canvas.itemconfig(canvas.artist_id, fill="#2D2D2D")
        canvas.scale("all", 0, 0, 0.95238, 0.95238)

    # Suggestion box hover
    def on_suggestion_hover(self, event):
        self.suggestion_canvas.scale("all", 0, 0, 1.05, 1.05)

    def on_suggestion_leave(self, event):
        self.suggestion_canvas.scale("all", 0, 0, 0.95238, 0.95238)

    # Clicking a song
    def on_song_click(self, song):
        self.update_suggestion_box(song)
        self.open_lyrics_window(song)

    # Clicking match found
    def on_match_click(self, event):
        if hasattr(self, "current_suggestion_song"):
            self.open_lyrics_window(self.current_suggestion_song)

    # Lyrics popup window
    def open_lyrics_window(self, song):
        lyrics_win = tk.Toplevel(self.root)
        lyrics_win.title(f"Lyrics - {song['Title']}")
        lyrics_win.geometry("600x400")
        lyrics_win.resizable(False, False)
        lyrics_win.configure(bg="#E8C999")  # same as suggestion box

        container = tk.Frame(lyrics_win, bg="#E8C999", padx=20, pady=20)
        container.pack(expand=True, fill="both")

        # Get lyrics safely
        lyrics_text = song.get('Lyric') or song.get('lyrics') or "Lyrics not available"

        # Text widget with scrollbar
        text_widget = tk.Text(container, font=("Arial", 14), bg="#E8C999", fg="black", wrap="word")
        text_widget.insert("1.0", lyrics_text)
        text_widget.config(state="disabled")  # read-only
        text_widget.pack(expand=True, fill="both", side="left")

        scrollbar = tk.Scrollbar(container, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        close_btn = tk.Button(container, text="Close", command=lyrics_win.destroy,
                              bg="#101010", fg="white", font=("Arial", 12), relief="flat")
        close_btn.pack(pady=10)