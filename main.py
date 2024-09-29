import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import keyboard
import pyautogui
import time
import pygetwindow as gw
import pyperclip

class AutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automation Script")

        # State to stop the automation
        self.running = False

        # Step 1: Email Fields
        self.email1_label = tk.Label(root, text="Email:")
        self.email1_label.grid(row=0, column=0)
        self.email1_entry = tk.Entry(root, width=40)
        self.email1_entry.grid(row=0, column=1)

        self.email2_label = tk.Label(root, text="Confirm Email:")
        self.email2_label.grid(row=1, column=0)
        self.email2_entry = tk.Entry(root, width=40)
        self.email2_entry.grid(row=1, column=1)

        # Step 2: Identity Fields
        self.identity_labels = ["First Name", "Last Name", "ID Series", "ID Number", "Valid From", "Valid Until",
                                "CNP", "Address", "Phone Number"]
        self.identity_entries = []
        for i, label_text in enumerate(self.identity_labels):
            label = tk.Label(root, text=label_text + ":")
            label.grid(row=i + 2, column=0)
            entry = tk.Entry(root, width=40)
            entry.grid(row=i + 2, column=1)
            self.identity_entries.append(entry)

        # Step 3: File Paths for Uploads
        self.file_labels = ["File 1", "File 2", "File 3", "File 4", "File 5 (Same as File 4)"]
        self.file_entries = []
        for i, label_text in enumerate(self.file_labels):
            label = tk.Label(root, text=label_text + ":")
            label.grid(row=i + 11, column=0)
            entry = tk.Entry(root, width=40)
            entry.grid(row=i + 11, column=1)
            self.file_entries.append(entry)
            button = tk.Button(root, text="Browse", command=lambda e=entry: self.browse_file(e))
            button.grid(row=i + 11, column=2)

        # Buttons for automation control
        self.run_button = tk.Button(root, text="Run Automation", command=self.start_listening)
        self.run_button.grid(row=17, column=0, columnspan=2)

        self.stop_button = tk.Button(root, text="Stop Automation", command=self.stop_automation)
        self.stop_button.grid(row=17, column=2)

        # Button to load from a .txt file
        self.load_txt_button = tk.Button(root, text="Load from .txt", command=self.load_from_txt)
        self.load_txt_button.grid(row=18, column=0, columnspan=3)

        # Status Label
        self.status_label = tk.Label(root, text="Status: Idle", fg="green")
        self.status_label.grid(row=19, column=0, columnspan=3)

    def browse_file(self, entry):
        file_path = filedialog.askopenfilename()
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)

    def start_listening(self):
        self.status_label.config(text="Status: Listening for Keys...", fg="blue")
        self.running = True

        # Start listening for key presses in a new thread
        self.listen_thread = threading.Thread(target=self.listen_for_keys)
        self.listen_thread.start()

    def stop_automation(self):
        self.running = False
        self.status_label.config(text="Status: Stopped", fg="red")

        # Unbind the hotkeys to prevent unintended behavior on subsequent runs
        keyboard.unhook_all_hotkeys()

    def listen_for_keys(self):
        try:
            # Listen for specific keys (left and right arrows)
            keyboard.add_hotkey('left', self.run_step_1)
            keyboard.add_hotkey('right', self.run_step_2)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_label.config(text="Status: Error", fg="red")

    def run_step_1(self):
        if not self.running:
            return
        email_1 = self.email1_entry.get()
        email_2 = self.email2_entry.get()
        self.fill_email_fields(email_1, email_2)

    def run_step_2(self):
        if not self.running:
            return
        identity_data = [entry.get() for entry in self.identity_entries]
        self.fill_identity_fields(identity_data)
        file_paths = [entry.get() for entry in self.file_entries]
        threading.Thread(target=self.upload_files_in_order, args=(file_paths,)).start()

    def fill_email_fields(self, email_1, email_2):
        if not self.running:
            return
        print("Filling out Step 1: Email Fields...")
        pyautogui.write(email_1, interval=0.01)
        pyautogui.press('tab')
        pyautogui.write(email_2, interval=0.01)
        pyautogui.press('tab')
        print("Step 1 completed.")

    def fill_identity_fields(self, identity_data):
        if not self.running:
            return
        print("Filling out Step 2: Identity Details...")
        for field in identity_data[:8]:  # Skip "Judet"
            pyautogui.write(field, interval=0.01)
            pyautogui.press('tab')

        pyautogui.press('tab')  # Skip the 'Judet' field
        pyautogui.write(identity_data[-1], interval=0.01)
        pyautogui.press('tab')
        print("Step 2 completed.")

    def upload_files_in_order(self, file_paths):
        self.status_label.config(text="Status: Uploading Files...", fg="blue")
        for file_path in file_paths:
            if not self.running:
                return
            print(f"Waiting for file dialog to open for: {file_path}")
            while True:
                if not self.running:
                    return
                windows = gw.getWindowsWithTitle('Open')
                if windows:
                    print(f"File explorer detected. Uploading {file_path}")
                    pyperclip.copy(file_path)
                    pyautogui.hotkey('ctrl', 'v')
                    pyautogui.press('enter')
                    break
            time.sleep(0.5)
        self.status_label.config(text="Status: Finished", fg="green")

    def load_from_txt(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                # Open the file with UTF-8 encoding
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                if len(lines) < 12:
                    raise ValueError("The .txt file does not contain enough data.")
                # Fill the entries with the data from the file
                self.email1_entry.delete(0, tk.END)
                self.email1_entry.insert(0, lines[0])
                self.email2_entry.delete(0, tk.END)
                self.email2_entry.insert(0, lines[1])
                for i, entry in enumerate(self.identity_entries):
                    entry.delete(0, tk.END)
                    entry.insert(0, lines[i + 2])
                for i, entry in enumerate(self.file_entries):
                    entry.delete(0, tk.END)
                    entry.insert(0, lines[i + 11])
                self.status_label.config(text="Data loaded from .txt", fg="green")
            except Exception as e:
                messagebox.showerror("Error", str(e))

# Create the application window
root = tk.Tk()
app = AutomationApp(root)

# Start the GUI event loop
root.mainloop()
