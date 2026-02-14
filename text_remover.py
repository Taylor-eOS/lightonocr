import tkinter as tk
from tkinter import filedialog, messagebox

class SimpleCleaner:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Text Cleaner - select to remove")
        self.root.geometry("1000x800")
        top = tk.Frame(self.root)
        top.pack(fill="x", pady=6, padx=8)
        tk.Button(top, text="Load file", command=self.load).pack(side="left", padx=6)
        tk.Button(top, text="Save result", command=self.save).pack(side="left", padx=6)
        tk.Button(top, text="Next ---", command=self.next_separator).pack(side="left", padx=6)
        self.status = tk.Label(top, text="No file loaded", font=("sans", 11))
        self.status.pack(side="left", padx=25)
        text_frame = tk.Frame(self.root)
        text_frame.pack(fill="both", expand=True, padx=8, pady=8)
        self.text = tk.Text(text_frame, font=("Courier", 10), wrap="word", spacing1=2, spacing3=2)
        self.text.pack(side="left", fill="both", expand=True)
        self.scroll = tk.Scrollbar(text_frame, command=self.text.yview)
        self.scroll.pack(side="right", fill="y")
        self.text.config(yscrollcommand=self.scroll.set)
        self.text.bind("<ButtonRelease-1>", self.remove_on_release)

    def load(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", content)
            self.text.see("1.0")
            self.status.config(text=f"Loaded {path.split('/')[-1]} - select text and release mouse to remove")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file\n{e}")

    def remove_on_release(self, event):
        try:
            start = self.text.index(tk.SEL_FIRST)
            end = self.text.index(tk.SEL_LAST)
        except tk.TclError:
            return
        if start == end:
            return
        self.text.delete(start, end)
        self.text.tag_remove(tk.SEL, "1.0", tk.END)
        self.status.config(text="Selection removed")

    def next_separator(self):
        try:
            pos = self.text.index("insert + 1c")
        except tk.TclError:
            pos = "1.0"
        while True:
            found = self.text.search("---", pos, tk.END)
            if not found:
                self.status.config(text="No more --- separators below current position")
                return
            line_start = self.text.index(f"{found} linestart")
            line_end = self.text.index(f"{found} lineend")
            line_text = self.text.get(line_start, line_end).strip()
            if line_text == "---":
                self.text.mark_set("insert", found)
                self.text.see(found)
                self.text.tag_remove(tk.SEL, "1.0", tk.END)
                self.status.config(text="Jumped to next --- separator")
                return
            pos = self.text.index(f"{found} + 3c")

    def save(self):
        content = self.text.get("1.0", tk.END).rstrip("\n")
        if not content.strip():
            messagebox.showinfo("Empty", "Nothing to save")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title="Save cleaned text")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Saved", f"Saved to\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    SimpleCleaner(root)
    root.mainloop()

