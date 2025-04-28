"""
TAG9010 LICENSE
(Freedom First. Surveillance Last. Humanity Rebuilt.)

(Full license text is in the LICENSE file. This program is distributed under the TAG9010 License.)
"""

# --- Tulsi The Democracy Hunter - Core Imports ---
import os
import re
import shutil
import subprocess
import tempfile
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import ast
import sys

# --- Suspicious Patterns ---
suspicious_patterns = {
    'eval() usage': r'\beval\s*\(',
    'exec() usage': r'\bexec\s*\(',
    'subprocess module': r'\bsubprocess\b',
    'os.system call': r'\bos\.system\s*\(',
    'socket usage': r'\bsocket\b',
    'common obfuscation (base64 decode)': r'base64\.b64decode\s*\(',
    'keylogger keyword': r'\bkeylog(?:ger)?\b',
    'backdoor keyword': r'\bbackdoor\b',
    'remote shell keyword': r'\bremote\s*shell\b',
    'pynput listener': r'pynput\.keyboard\.Listener|pynput\.mouse\.Listener'
}

# --- I/O and Device Access Patterns ---
io_patterns = {
    'open() function': r'\bopen\s*\(',
    'reading files': r'\.read\s*\(',
    'writing files': r'\.write\s*\(',
    'network request (requests)': r'\brequests\.(get|post|put|delete|request)\s*\(',
    'network request (urllib)': r'urllib\.request\.',
    'keyboard import': r'\bimport\s+keyboard\b',
    'pynput module': r'\bpynput\b',
    'sounddevice/pyaudio': r'\b(sounddevice|pyaudio)\b',
    'camera access (opencv)': r'\bcv2\.VideoCapture\s*\('
}

# --- File Types Supported ---
FILE_EXTENSIONS = {'.py', '.js', '.java', '.c', '.cpp', '.h', '.php', '.rb', '.pl', '.sh', '.bat', '.ps1', '.html', '.css'}
# --- Utility Functions ---

def update_text_widget(widget, text):
    """Safely updates a Tkinter text widget from any thread."""
    widget.config(state=tk.NORMAL)
    widget.insert(tk.END, text + "\n")
    widget.see(tk.END)  # Scroll to end
    widget.config(state=tk.DISABLED)

def set_widget_state(widget, state):
    """Safely sets the state of a Tkinter widget."""
    widget.config(state=state)

# --- Scanning Functions ---

def scan_code_content(code_content, source_name="Pasted Code"):
    """Scans a string of code content for patterns."""
    findings = []
    for desc, pattern in suspicious_patterns.items():
        try:
            if re.search(pattern, code_content, re.IGNORECASE):
                findings.append(f"{source_name}: Suspicious - {desc}")
        except re.error as e:
            findings.append(f"{source_name}: Regex Error in '{desc}': {e}")
    for desc, pattern in io_patterns.items():
        try:
            if re.search(pattern, code_content, re.IGNORECASE):
                findings.append(f"{source_name}: I/O or Device Access - {desc}")
        except re.error as e:
            findings.append(f"{source_name}: Regex Error in '{desc}': {e}")
    return findings

def scan_file(file_path):
    """Reads and scans a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        display_path = os.path.relpath(file_path)
        return scan_code_content(content, source_name=display_path)
    except Exception as e:
        return [f"{file_path}: Error reading file - {e}"]

def scan_repository(repo_path, progress_callback):
    """Scans a repository directory for suspicious files."""
    all_findings = []
    scanned_files = 0
    for root_dir, _, files in os.walk(repo_path):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in FILE_EXTENSIONS:
                file_path = os.path.join(root_dir, file)
                try:
                    if os.path.getsize(file_path) > 10 * 1024 * 1024:
                        progress_callback(f"Skipping large file: {file_path}")
                        continue
                    file_findings = scan_file(file_path)
                    if file_findings:
                        all_findings.extend(file_findings)
                    scanned_files += 1
                except OSError as e:
                    progress_callback(f"Access error: {file_path} - {e}")
                except Exception as e:
                    progress_callback(f"Error processing {file_path}: {e}")

    progress_callback(f"Finished scanning {scanned_files} files.")
    return all_findings
# --- GUI Core Setup ---

root = tk.Tk()
root.title("Tulsi The Democracy Hunter")
root.geometry("950x700")

# --- Style Setup ---
style = ttk.Style()
available_themes = style.theme_names()
preferred_themes = ['clam', 'alt', 'default', 'vista', 'xpnative']
for theme in preferred_themes:
    if theme in available_themes:
        try:
            style.theme_use(theme)
            break
        except tk.TclError:
            continue

# --- Notebook (Tabs) ---
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both', padx=10, pady=10)

# --- Tab 1: GitHub Repository Scan ---
repo_frame = ttk.Frame(notebook, padding="10")
notebook.add(repo_frame, text="Scan GitHub Repository")

repo_url_entry = ttk.Entry(repo_frame, width=80)
repo_url_entry.pack(pady=5)

scan_repo_button = ttk.Button(repo_frame, text="Download & Scan Repository")
scan_repo_button.pack(pady=5)

repo_results_text = scrolledtext.ScrolledText(repo_frame, height=20, state=tk.DISABLED, wrap=tk.WORD)
repo_results_text.pack(expand=True, fill='both', pady=5)

# --- Tab 2: Local Code Scan ---
code_frame = ttk.Frame(notebook, padding="10")
notebook.add(code_frame, text="Scan Pasted Code")

code_text = scrolledtext.ScrolledText(code_frame, height=15, wrap=tk.WORD)
code_text.pack(expand=True, fill='both', pady=5)

paste_button = ttk.Button(code_frame, text="Paste from Clipboard")
paste_button.pack(pady=5)

scan_code_button = ttk.Button(code_frame, text="Scan Pasted Code")
scan_code_button.pack(pady=5)

code_results_text = scrolledtext.ScrolledText(code_frame, height=8, state=tk.DISABLED, wrap=tk.WORD)
code_results_text.pack(expand=True, fill='both', pady=5)

# --- Tab 3: View Tulsi Code ---
view_code_frame = ttk.Frame(notebook, padding="10")
notebook.add(view_code_frame, text="View Tulsi’s Code")

view_code_text = scrolledtext.ScrolledText(view_code_frame, height=20, wrap=tk.WORD)
view_code_text.pack(expand=True, fill='both', pady=5)

load_code_button = ttk.Button(view_code_frame, text="Load Tulsi's Code")
load_code_button.pack(pady=5)

open_blind_mode_button = ttk.Button(view_code_frame, text="Tulsi in Blind Mode")
open_blind_mode_button.pack(pady=5)
# --- Blind Mode Window ---

def open_tulsi_blind_mode(initial_code):
    """Open a special window for Tulsi Blind Mode."""
    blind_win = tk.Toplevel(root)
    blind_win.title("Tulsi in Blind Mode")
    blind_win.geometry("900x600")

    global blind_text
    blind_text = scrolledtext.ScrolledText(blind_win, height=25, wrap=tk.WORD)
    blind_text.pack(expand=True, fill='both', padx=10, pady=5)
    blind_text.insert(tk.END, initial_code)

    button_frame = ttk.Frame(blind_win)
    button_frame.pack(pady=5)

    undo_button = ttk.Button(button_frame, text="Undo All Changes", command=lambda: reset_blind_text(initial_code))
    undo_button.pack(side=tk.LEFT, padx=5)

    global error_text
    error_text = scrolledtext.ScrolledText(blind_win, height=8, state=tk.DISABLED, wrap=tk.WORD)
    error_text.pack(expand=True, fill='both', padx=10, pady=5)

    blind_text.bind("<<Modified>>", on_blind_text_change)

def reset_blind_text(original_code):
    blind_text.config(state=tk.NORMAL)
    blind_text.delete("1.0", tk.END)
    blind_text.insert(tk.END, original_code)
    blind_text.edit_modified(0)
    update_error_display()

def on_blind_text_change(event=None):
    """Detects text changes and updates error checking."""
    blind_text.edit_modified(0)
    update_error_display()

def update_error_display():
    """Improved error checking for Blind Mode."""
    code = blind_text.get("1.0", tk.END)
    error_text.config(state=tk.NORMAL)
    error_text.delete("1.0", tk.END)

    try:
        compile(code, "<string>", "exec")
        error_text.insert(tk.END, "No syntax errors detected.")
    except SyntaxError as e:
        error_text.insert(tk.END, f"Syntax Error:\nLine {e.lineno}: {e.text.strip()}\nProblem: {e.msg}")
    except Exception as e:
        error_text.insert(tk.END, f"Error:\n{e}")

    error_text.config(state=tk.DISABLED)

# --- Logic Handlers ---

def start_repo_scan_thread():
    repo_url = repo_url_entry.get().strip()
    if not repo_url:
        messagebox.showerror("Input Error", "Please enter a GitHub repository URL.")
        return
    repo_results_text.config(state=tk.NORMAL)
    repo_results_text.delete("1.0", tk.END)
    repo_results_text.config(state=tk.DISABLED)

    thread = threading.Thread(
        target=_perform_repo_scan,
        args=(repo_url, repo_results_text, scan_repo_button, root),
        daemon=True
    )
    thread.start()

def _perform_repo_scan(repo_url, results_widget, scan_button, root_window):
    temp_dir = None
    try:
        root_window.after(0, update_text_widget, results_widget, "Cloning repository...")
        root_window.after(0, set_widget_state, scan_button, tk.DISABLED)

        temp_dir = tempfile.mkdtemp(prefix="repo_scan_")
        repo_dir = os.path.join(temp_dir, "repo")

        timeout_seconds = 120
        clone_cmd = ["git", "clone", "--depth", "1", repo_url, repo_dir]
        try:
            result = subprocess.run(
                clone_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                timeout=timeout_seconds,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            root_window.after(0, update_text_widget, results_widget, "Repository cloned successfully.")
        except Exception as e:
            root_window.after(0, messagebox.showerror, "Clone Error", str(e))
            return

        def progress_callback(message):
            root_window.after(0, update_text_widget, results_widget, f"Progress: {message}")

        findings = scan_repository(repo_dir, progress_callback)

        root_window.after(0, update_text_widget, results_widget, "\n--- Scan Results ---")
        if findings:
            root_window.after(0, update_text_widget, results_widget, "\n".join(findings))
        else:
            root_window.after(0, update_text_widget, results_widget, "No suspicious patterns found.")
        root_window.after(0, update_text_widget, results_widget, "Scan complete.")

    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        root_window.after(0, set_widget_state, scan_button, tk.NORMAL)

def scan_pasted_code():
    code = code_text.get("1.0", tk.END)
    if not code.strip():
        messagebox.showwarning("Input Needed", "Please paste some code first.")
        return

    set_widget_state(scan_code_button, tk.DISABLED)
    set_widget_state(paste_button, tk.DISABLED)

    code_results_text.config(state=tk.NORMAL)
    code_results_text.delete("1.0", tk.END)

    try:
        findings = scan_code_content(code, source_name="Pasted Code")
        if findings:
            code_results_text.insert(tk.END, "--- Scan Results ---\n")
            code_results_text.insert(tk.END, "\n".join(findings))
        else:
            code_results_text.insert(tk.END, "No suspicious patterns detected.")
    except Exception as e:
        code_results_text.insert(tk.END, f"\n--- An Error Occurred ---\n{e}")
        messagebox.showerror("Scan Error", str(e))
    finally:
        code_results_text.config(state=tk.DISABLED)
        set_widget_state(scan_code_button, tk.NORMAL)
        set_widget_state(paste_button, tk.NORMAL)

def paste_from_clipboard():
    try:
        clipboard_content = root.clipboard_get()
        code_text.insert(tk.END, clipboard_content)
        code_text.see(tk.END)
    except tk.TclError:
        messagebox.showwarning("Paste Error", "Clipboard is empty or unavailable.")

def load_tulsi_code():
    try:
        script_path = os.path.abspath(__file__)
        with open(script_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
        view_code_text.delete("1.0", tk.END)
        view_code_text.insert(tk.END, code_content)
    except Exception as e:
        messagebox.showerror("Load Error", f"Could not load code: {e}")

def open_blind_mode_from_viewer():
    code = view_code_text.get("1.0", tk.END)
    open_tulsi_blind_mode(code)

# --- Final Event Bindings ---
scan_repo_button.config(command=start_repo_scan_thread)
scan_code_button.config(command=scan_pasted_code)
paste_button.config(command=paste_from_clipboard)
load_code_button.config(command=load_tulsi_code)
open_blind_mode_button.config(command=open_blind_mode_from_viewer)

# --- Launch Application ---
root.mainloop()
