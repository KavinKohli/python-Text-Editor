import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox, ttk
import keyword
import time
import threading
import os

AUTO_SAVE_INTERVAL = 60

# FILE OPERATIONS
def open_file(window, text_edit):
    filepath = askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not filepath:
        return
    try:
        with open(filepath, "r") as f:
            text_edit.delete(1.0, tk.END)
            text_edit.insert(tk.END, f.read())
        window.title(f"Text Editor - {filepath}")
    except Exception as e:
        messagebox.showerror("Error", f"Unable to open file:\n{e}")

def save_file(window, text_edit):
    filepath = asksaveasfilename(filetypes=[("Text Files", "*.txt")], defaultextension=".txt")
    if not filepath:
        return
    try:
        with open(filepath, "w") as f:
            f.write(text_edit.get(1.0, tk.END))
        window.title(f"Text Editor - {filepath}")
    except Exception as e:
        messagebox.showerror("Error", f"Unable to save file:\n{e}")

# AUTO SAVE THREAD
def auto_save(window, text_edit):
    while True:
        time.sleep(AUTO_SAVE_INTERVAL)
        title = window.title()
        if title.startswith("Text Editor - "):
            filepath = title.split(" - ", 1)[1]
            with open(filepath, "w") as f:
                f.write(text_edit.get(1.0, tk.END))

def start_auto_save_thread(window, text_edit):
    t = threading.Thread(target=auto_save, args=(window, text_edit), daemon=True)
    t.start()

# SEARCH & REPLACE
def search_replace(text_edit):
    top = tk.Toplevel()
    top.title("Search & Replace")
    top.geometry("300x140")

    tk.Label(top, text="Search:").pack()
    search_entry = tk.Entry(top)
    search_entry.pack()

    tk.Label(top, text="Replace:").pack()
    replace_entry = tk.Entry(top)
    replace_entry.pack()

    def replace_all():
        find = search_entry.get()
        replace = replace_entry.get()
        text = text_edit.get(1.0, tk.END)
        text_edit.delete(1.0, tk.END)
        text_edit.insert(1.0, text.replace(find, replace))

    tk.Button(top, text="Replace All", command=replace_all).pack(pady=5)

# LINE NUMBERS
def update_line_numbers(text_edit, line_numbers):
    text = ""
    row, _ = text_edit.index("end").split(".")
    for i in range(1, int(row)):
        text += f"{i}\n"
    line_numbers.config(state="normal")
    line_numbers.delete(1.0, tk.END)
    line_numbers.insert(1.0, text)
    line_numbers.config(state="disabled")

# SYNTAX HIGHLIGHT
def syntax_highlight(event=None, text_widget=None):
    code = text_widget.get("1.0", tk.END)
    text_widget.tag_remove("keyword", "1.0", tk.END)

    for kw in keyword.kwlist:
        start = "1.0"
        while True:
            pos = text_widget.search(rf"\b{kw}\b", start, tk.END, regexp=True)
            if not pos:
                break
            end = f"{pos}+{len(kw)}c"
            text_widget.tag_add("keyword", pos, end)
            start = end

# MAIN UI
def toggle_dark_mode(window, text_edit, line_numbers):
    bg = "#1e1e1e"
    fg = "#ffffff"
    text_edit.config(bg=bg, fg=fg, insertbackground=fg)
    line_numbers.config(bg="#252526", fg="#888888")

def main():
    window = tk.Tk()
    window.title("Text Editor")
    window.geometry("1000x650")

    # MENU BAR
    menu_bar = tk.Menu(window)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Open  (Ctrl+O)", command=lambda: open_file(window, text_edit))
    file_menu.add_command(label="Save  (Ctrl+S)", command=lambda: save_file(window, text_edit))
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=window.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)

    edit_menu = tk.Menu(menu_bar, tearoff=0)
    edit_menu.add_command(label="Search & Replace  (Ctrl+F)", command=lambda: search_replace(text_edit))
    menu_bar.add_cascade(label="Edit", menu=edit_menu)

    view_menu = tk.Menu(menu_bar, tearoff=0)
    view_menu.add_command(label="Dark Mode", command=lambda: toggle_dark_mode(window, text_edit, line_numbers))
    menu_bar.add_cascade(label="View", menu=view_menu)

    window.config(menu=menu_bar)

    # TEXT + LINE NUMBERS + SCROLLBAR
    frame = tk.Frame(window)
    frame.pack(fill="both", expand=True)

    line_numbers = tk.Text(frame, width=5, padx=5, state="disabled", bg="#efefef")
    line_numbers.pack(side="left", fill="y")

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    text_edit = tk.Text(frame, font=("Consolas", 15), undo=True, wrap="word", yscrollcommand=scrollbar.set)
    text_edit.pack(fill="both", expand=True)
    scrollbar.config(command=text_edit.yview)

    text_edit.tag_configure("keyword", foreground="cyan")

    text_edit.bind("<KeyRelease>", lambda e: [syntax_highlight(text_widget=text_edit),
                                              update_line_numbers(text_edit, line_numbers)])

    # SHORTCUTS
    window.bind("<Control-s>", lambda x: save_file(window, text_edit))
    window.bind("<Control-o>", lambda x: open_file(window, text_edit))
    window.bind("<Control-f>", lambda x: search_replace(text_edit))

    start_auto_save_thread(window, text_edit)

    window.mainloop()

main()
