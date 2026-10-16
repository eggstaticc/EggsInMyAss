import pystray
from PIL import Image, ImageDraw
import tkinter as tk
import threading
import requests
from bs4 import BeautifulSoup

class JarvisApp:
    def __init__(self):
        # Create a simple blue circle icon using Pillow
        img = Image.new('RGB', (64, 64), color=(0, 100, 255))
        d = ImageDraw.Draw(img)
        d.ellipse([10, 10, 54, 54], fill=(0, 50, 150))
        
        self.tray_icon = pystray.Icon(
            "jarvis", 
            img, 
            "JARVIS", 
            menu=pystray.Menu(
                pystray.MenuItem("Open Interface", self.open_window),
                pystray.MenuItem("Quit", self.quit_app)
            )
        )
        
        # Run the tray icon in a background thread so it doesn't block the UI
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        print("Jarvis is running.")

    def open_window(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel()
        self.window.title("JARVIS - Uncensored")
        self.window.geometry("500x400")
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.window.withdraw())

        # Input Frame
        input_frame = tk.Frame(self.window)
        input_frame.pack(pady=10, padx=10, fill="x")
        
        tk.Label(input_frame, text="Query:", font=("Arial", 10)).pack(side="left")
        self.input_box = tk.Entry(input_frame, width=45)
        self.input_box.pack(side="left", padx=5)
        self.input_box.bind("<Return>", lambda e: self.process_query())
        
        btn = tk.Button(input_frame, text="Search", command=self.process_query)
        btn.pack(side="right")

        # Output Frame
        output_frame = tk.Frame(self.window)
        output_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.output_box = tk.Text(output_frame, height=15, width=60, state='disabled')
        scrollbar = tk.Scrollbar(output_frame, command=self.output_box.yview)
        self.output_box.configure(yscrollcommand=scrollbar.set)
        
        self.output_box.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def process_query(self):
        query = self.input_box.get().strip()
        if not query:
            return
        
        self.output_box.config(state='normal')
        self.output_box.delete("1.0", "end")
        
        try:
            response_text = self.fetch_uncensored(query)
            self.output_box.insert("end", f"Query: {query}\n\nResponse:\n{response_text}")
        except Exception as e:
            self.output_box.insert("end", f"Error: {e}")
        
        self.output_box.config(state='disabled')

    def fetch_uncensored(self, query):
        """
        Performs a raw Google search to avoid API filters.
        Returns the top 3 results' titles and snippets.
        """
        url = f"https://www.google.com/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        try:
            res = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            results = []
            for item in soup.find_all('div', class_='g'):
                title_tag = item.find('h3')
                snippet_tag = item.find('div', class_=['VwiC3b', 'Mu4QLc'])
                
                if title_tag and snippet_tag:
                    results.append(f"[{title_tag.text}]: {snippet_tag.text[:150]}...")
                    
                if len(results) >= 3:
                    break
            
            if results:
                return "\n".join(results)
            else:
                return "No results found."
                
        except Exception as e:
            return f"Connection failed: {e}"

    def quit_app(self, item):
        self.tray_icon.stop()
        if self.window:
            self.window.destroy()

if __name__ == "__main__":
    app = JarvisApp()
    # Keep the main thread alive
    while True:
        pass
