import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import base64
from io import BytesIO
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---- Core Logic ----
def vectorize(Text):
    return TfidfVectorizer().fit_transform(Text).toarray()

def similarity(doc1, doc2):
    return cosine_similarity([doc1, doc2])[0][1]

def check_plagiarism(file1, file2):
    try:
        with open(file1, encoding='utf-8') as f1, open(file2, encoding='utf-8') as f2:
            text1 = f1.read()
            text2 = f2.read()
            vectors = vectorize([text1, text2])
            score = similarity(vectors[0], vectors[1])
            return round(score * 100, 2)  # Return as percentage
    except Exception as e:
        raise e

# ---- Custom themed elements ----
class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, width=200, height=40, color="#4a6ee0", hover_color="#3254c5", **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, **kwargs)
        self.color = color
        self.hover_color = hover_color
        self.command = command
        self.text = text
        
        # Draw button
        self.create_rounded_rect(0, 0, width, height, radius=10, fill=self.color)
        self.text_id = self.create_text(width/2, height/2, text=text, fill="white", font=("Helvetica", 12, "bold"))
        
        # Bind events
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius=10, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_hover(self, event):
        self.itemconfig(1, fill=self.hover_color)
        self.config(cursor="hand2")
        
    def on_leave(self, event):
        self.itemconfig(1, fill=self.color)
        self.config(cursor="")
        
    def on_click(self, event):
        if self.command:
            self.command()

class FileDropArea(tk.Canvas):
    def __init__(self, parent, command, **kwargs):
        super().__init__(parent, highlightthickness=1, highlightbackground="#e6e6e6", **kwargs)
        self.command = command
        self.files = []
        self.max_files = 2
        
        # Create the visual elements
        self.create_rectangle(0, 0, self.winfo_reqwidth(), self.winfo_reqheight(), 
                             fill="#f7f9fc", outline="")
        
        self.create_text(self.winfo_reqwidth()/2, self.winfo_reqheight()/2 - 15, 
                        text="Drag & Drop Files Here", font=("Arial", 14))
        self.create_text(self.winfo_reqwidth()/2, self.winfo_reqheight()/2 + 15, 
                        text="or click to browse", font=("Arial", 10), fill="#888888")
        
        # Bind events
        self.bind("<Button-1>", self.browse_files)
        self.bind("<Enter>", lambda e: self.config(cursor="hand2"))
        self.bind("<Leave>", lambda e: self.config(cursor=""))
        
    def browse_files(self, event=None):
        file_paths = filedialog.askopenfilenames(filetypes=[("Text Files", "*.txt")])
        if file_paths:
            self.files = file_paths[:self.max_files]  # Limit to max_files
            if self.command:
                self.command(self.files)

# Result visualization component
class ResultGauge(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.width = kwargs.get('width', 200)
        self.height = kwargs.get('height', 200)
        
    def update_score(self, score):
        self.delete("all")
        
        # Determine color based on score
        if score >= 70:
            color = "#ff5252"  # Red
            label = "High Similarity"
        elif score >= 40:
            color = "#ffab40"  # Orange
            label = "Moderate Similarity"
        else:
            color = "#66bb6a"  # Green
            label = "Low Similarity"
            
        # Draw arc background
        self.create_arc(10, 10, self.width-10, self.height-10, 
                        start=180, extent=180, 
                        style="arc", width=20, outline="#e0e0e0")
        
        # Draw score arc
        angle = 180 * (score / 100)
        self.create_arc(10, 10, self.width-10, self.height-10, 
                        start=180, extent=angle, 
                        style="arc", width=20, outline=color)
        
        # Draw score text
        self.create_text(self.width/2, self.height/2, 
                        text=f"{score}%", 
                        font=("Arial", 24, "bold"), fill=color)
        
        # Draw label
        self.create_text(self.width/2, self.height/2 + 30, 
                        text=label, 
                        font=("Arial", 12), fill="#555555")

# ---- GUI Functionality ----
def upload_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("Text Files", "*.txt")])
    if file_paths:
        update_file_display(file_paths)

def update_file_display(file_paths):
    global file1_label, file2_label, file1_path, file2_path
    
    # Clear previous file information
    for widget in file_display.winfo_children():
        widget.destroy()
    
    # Reset file paths
    file1_path = file2_path = None
    
    # Update with new file information
    if len(file_paths) >= 1:
        file1_path = file_paths[0]
        file1_frame = tk.Frame(file_display, bg="#f0f4f8", padx=10, pady=5)
        file1_frame.pack(fill="x", pady=5)
        file1_label = tk.Label(file1_frame, text=f"File 1: {os.path.basename(file1_path)}", 
                               bg="#f0f4f8", anchor="w", font=("Arial", 10))
        file1_label.pack(side="left", fill="x", expand=True)
        
        remove_btn1 = tk.Label(file1_frame, text="×", fg="red", cursor="hand2", bg="#f0f4f8", font=("Arial", 12, "bold"))
        remove_btn1.pack(side="right")
        remove_btn1.bind("<Button-1>", lambda e: remove_file(1))
    
    if len(file_paths) >= 2:
        file2_path = file_paths[1]
        file2_frame = tk.Frame(file_display, bg="#f0f4f8", padx=10, pady=5)
        file2_frame.pack(fill="x", pady=5)
        file2_label = tk.Label(file2_frame, text=f"File 2: {os.path.basename(file2_path)}", 
                               bg="#f0f4f8", anchor="w", font=("Arial", 10))
        file2_label.pack(side="left", fill="x", expand=True)
        
        remove_btn2 = tk.Label(file2_frame, text="×", fg="red", cursor="hand2", bg="#f0f4f8", font=("Arial", 12, "bold"))
        remove_btn2.pack(side="right")
        remove_btn2.bind("<Button-1>", lambda e: remove_file(2))
    
    # Enable/disable analyze button based on file selection
    if len(file_paths) >= 2:
        analyze_btn.config(state="normal")
    else:
        analyze_btn.config(state="disabled")

def remove_file(file_num):
    global file1_path, file2_path
    
    if file_num == 1:
        file1_path = None
    else:
        file2_path = None
    
    # Update file display
    if file1_path:
        file_paths = [file1_path]
        if file2_path:
            file_paths.append(file2_path)
    elif file2_path:
        file_paths = [file2_path]
    else:
        file_paths = []
    
    update_file_display(file_paths)

def analyze_plagiarism():
    global file1_path, file2_path
    
    if not file1_path or not file2_path:
        messagebox.showwarning("Warning", "Please select exactly 2 .txt files to compare.")
        return
    
    try:
        # Show loading state
        result_display.configure(state='normal')
        result_display.delete("1.0", tk.END)
        result_display.insert(tk.END, "Analyzing...\n")
        result_display.configure(state='disabled')
        root.update()
        
        # Calculate similarity
        score = check_plagiarism(file1_path, file2_path)
        
        # Update gauge
        result_gauge.update_score(score)
        
        # Update text display
        result_display.configure(state='normal')
        result_display.delete("1.0", tk.END)
        
        # Show file names
        result_display.insert(tk.END, f"📄 {os.path.basename(file1_path)}\n", "file")
        result_display.insert(tk.END, f"📄 {os.path.basename(file2_path)}\n\n", "file")
        
        # Show score text
        result_display.insert(tk.END, "Content Similarity Score: ")
        
        # Colored score
        if score >= 70:
            result_display.insert(tk.END, f"{score}%\n\n", "high")
            result_display.insert(tk.END, "⚠️ High similarity detected! These documents contain significant matching content.\n", "high_desc")
        elif score >= 40:
            result_display.insert(tk.END, f"{score}%\n\n", "medium")
            result_display.insert(tk.END, "⚠️ Moderate similarity detected. Some portions of the content may be similar.\n", "medium_desc")
        else:
            result_display.insert(tk.END, f"{score}%\n\n", "low")
            result_display.insert(tk.END, "✅ Low similarity detected. The documents appear to be mostly original.\n", "low_desc")
        
        result_display.configure(state='disabled')
        
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---- GUI Setup ----
# Create main window
root = tk.Tk()
root.title("📚 Plagiarism Checker Pro")
root.geometry("800x600")
root.configure(bg="#ffffff")
root.resizable(True, True)

# Define global variables
file1_path = None
file2_path = None

# Create custom title bar
header = tk.Frame(root, bg="#4a6ee0", height=60)
header.pack(fill="x")

title = tk.Label(header, text="Plagiarism Checker Pro", font=("Helvetica", 18, "bold"), 
                fg="white", bg="#4a6ee0")
title.pack(pady=15)

# Main content area
main_frame = tk.Frame(root, bg="#ffffff")
main_frame.pack(fill="both", expand=True, padx=20, pady=10)

# Left panel (file selection and controls)
left_panel = tk.Frame(main_frame, bg="#ffffff", width=350)
left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

instruction = tk.Label(left_panel, text="Select two text files to compare", 
                     font=("Arial", 12), bg="#ffffff", fg="#555555")
instruction.pack(pady=(0, 10), anchor="w")

# File selection area
file_frame = tk.Frame(left_panel, bg="#ffffff")
file_frame.pack(fill="x")

upload_btn = tk.Button(file_frame, text="Select Files", command=upload_files,
                      bg="#4a6ee0", fg="white", font=("Arial", 10), 
                      activebackground="#3254c5", activeforeground="white",
                      relief="flat", padx=15, pady=5)
upload_btn.pack(side="left", pady=10)

# File display area
file_display = tk.Frame(left_panel, bg="#ffffff")
file_display.pack(fill="x", pady=10)

# Analyze button
analyze_btn = tk.Button(left_panel, text="Analyze Plagiarism", command=analyze_plagiarism,
                      bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), 
                      activebackground="#388E3C", activeforeground="white",
                      relief="flat", padx=20, pady=10, state="disabled")
analyze_btn.pack(pady=20)

# Result gauge (visual representation)
gauge_frame = tk.Frame(left_panel, bg="#ffffff")
gauge_frame.pack(fill="x", pady=10)

result_gauge = ResultGauge(gauge_frame, width=200, height=200, bg="#ffffff")
result_gauge.pack(pady=10)

# Right panel (results display)
right_panel = tk.Frame(main_frame, bg="#ffffff", width=450)
right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

results_label = tk.Label(right_panel, text="Analysis Results", font=("Arial", 14, "bold"), 
                        bg="#ffffff", fg="#333333")
results_label.pack(anchor="w", pady=(0, 10))

result_frame = tk.Frame(right_panel, bd=1, relief="solid", bg="#ffffff", highlightbackground="#e0e0e0")
result_frame.pack(fill="both", expand=True)

result_display = tk.Text(result_frame, font=("Consolas", 11), wrap=tk.WORD, 
                        bg="#f8f9fa", fg="#333333", padx=10, pady=10,
                        state='disabled', height=15)
result_display.pack(side="left", fill="both", expand=True)

# Scrollbar for result display
scrollbar = ttk.Scrollbar(result_frame, command=result_display.yview)
scrollbar.pack(side="right", fill="y")
result_display.config(yscrollcommand=scrollbar.set)

# Tag configurations for color
result_display.tag_configure("high", foreground="#ff5252", font=("Consolas", 11, "bold"))
result_display.tag_configure("medium", foreground="#ffab40", font=("Consolas", 11, "bold"))
result_display.tag_configure("low", foreground="#66bb6a", font=("Consolas", 11, "bold"))
result_display.tag_configure("file", foreground="#4a6ee0", font=("Consolas", 11))
result_display.tag_configure("high_desc", foreground="#ff5252")
result_display.tag_configure("medium_desc", foreground="#ffab40")
result_display.tag_configure("low_desc", foreground="#66bb6a")

# Footer
footer = tk.Frame(root, bg="#f0f4f8", height=30)
footer.pack(fill="x", side="bottom")

footer_text = tk.Label(footer, text="© 2025 Plagiarism Checker Pro", 
                     font=("Arial", 8), bg="#f0f4f8", fg="#888888")
footer_text.pack(pady=8)

# Starting message
result_display.configure(state='normal')
result_display.insert(tk.END, "Welcome to Plagiarism Checker Pro!\n\n", "file")
result_display.insert(tk.END, "Please select two text files to analyze their similarity.\n\n")
result_display.insert(tk.END, "How to use:\n")
result_display.insert(tk.END, "1. Click 'Select Files' to choose two .txt files\n")
result_display.insert(tk.END, "2. Click 'Analyze Plagiarism' to compare them\n")
result_display.insert(tk.END, "3. Review the similarity score and analysis results\n")
result_display.configure(state='disabled')

# Set initial gauge value
result_gauge.update_score(0)

# Start application
root.mainloop()
