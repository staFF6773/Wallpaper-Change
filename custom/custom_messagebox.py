import tkinter as tk
from tkinter import ttk
import sv_ttk

class CustomMessageBox:
    _current_instance = None  # Class variable to track the current instance

    def __init__(self, parent, title, message):
        # Check if there is an existing instance and close it
        if CustomMessageBox._current_instance:
            CustomMessageBox._current_instance.close()

        self.parent = parent
        self.top = tk.Toplevel(parent)
        self.top.title(title)

        # Calculate the position of the parent widget
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() // 2)
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() // 2)

        # Center the dialog on the parent widget
        self.top.geometry(f"300x150+{x-150}+{y-75}")
        self.top.transient(parent)  # Make this dialog transient to parent
        self.top.grab_set()  # Make this dialog modal

        # Apply sv_ttk theme
        sv_ttk.set_theme("dark")

        # Create a frame for the content
        frame = ttk.Frame(self.top, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Message label
        self.message_label = ttk.Label(frame, text=message, wraplength=250)
        self.message_label.pack(pady=10)

        # Button frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)

        # OK button
        self.ok_button = ttk.Button(button_frame, text="OK", command=self.close)
        self.ok_button.pack(side=tk.RIGHT, padx=5)

        # Update the class variable to the current instance
        CustomMessageBox._current_instance = self

    def set_window_icon(self, icon_path):
        try:
            icon = tk.PhotoImage(file=icon_path)
            self.top.iconphoto(False, icon)
        except Exception as e:
            print(f"Error loading window icon: {e}")

    def close(self):
        self.top.destroy()
        CustomMessageBox._current_instance = None

def show_custom_messagebox(parent, title, message):
    return CustomMessageBox(parent, title, message)
