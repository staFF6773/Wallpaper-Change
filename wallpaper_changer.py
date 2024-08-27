import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import ctypes
import os
import time
import threading
from plyer import notification
from PIL import Image, ImageTk
import pystray

class WallpaperChangerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wallpaper Changer")
        self.root.geometry("500x400")
        self.root.configure(bg="#f0f0f0")  # Background color

        # Prevent resizing and maximize
        self.root.resizable(False, False)

        # Estilo de ttk
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 10), padding=6)
        self.style.configure("TLabel", font=("Helvetica", 10), background="#f0f0f0")
        self.style.configure("TFrame", background="#f0f0f0")

        self.window_icon_path = os.path.join(os.path.dirname(__file__), 'data', 'img', '0497a1a7d154bd672e4fb7e1b6aabdff.png')  # Window icon
        self.notification_icon_path = os.path.join(os.path.dirname(__file__), 'data', 'img', '0497a1a7d154bd672e4fb7e1b6aabdff.ico')  # Notification icon
        self.set_window_icon(self.window_icon_path)

        self.day_wallpaper = ""
        self.night_wallpaper = ""
        
        self.day_time = "06:00"
        self.night_time = "18:00"

        self.current_wallpaper = None

        # Frame principal para contenido
        self.content_frame = ttk.Frame(root, padding=(20, 10, 20, 0))  # Added top padding
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Imagen de encabezado
        self.header_image = Image.open(self.window_icon_path)
        self.header_image = self.header_image.resize((50, 50), Image.LANCZOS)
        self.header_photo = ImageTk.PhotoImage(self.header_image)
        self.header_label = ttk.Label(self.content_frame, image=self.header_photo, text="  Wallpaper Changer", compound=tk.LEFT, font=("Helvetica", 16, "bold"))
        self.header_label.pack(pady=10)

        ttk.Button(self.content_frame, text="Select Day Wallpaper", command=self.select_day_wallpaper).pack(pady=10)
        ttk.Button(self.content_frame, text="Select Night Wallpaper", command=self.select_night_wallpaper).pack(pady=10)
        
        ttk.Label(self.content_frame, text="Day wallpaper change time (HH:MM):").pack()
        self.day_time_entry = ttk.Entry(self.content_frame)
        self.day_time_entry.insert(0, self.day_time)
        self.day_time_entry.pack(pady=5)
        
        ttk.Label(self.content_frame, text="Night wallpaper change time (HH:MM):").pack()
        self.night_time_entry = ttk.Entry(self.content_frame)
        self.night_time_entry.insert(0, self.night_time)
        self.night_time_entry.pack(pady=5)
        
        ttk.Button(self.content_frame, text="Save Settings", command=self.save_settings).pack(pady=10)

        self.footer_frame = ttk.Frame(root, padding=10, style="TFrame")
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.footer_label = ttk.Label(self.footer_frame, text="Version 1.1.0 | Created by staFF6773", anchor=tk.CENTER)
        self.footer_label.pack()

        self.load_settings()

        self.apply_initial_wallpaper()

        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

        self.create_tray_icon()

    def set_window_icon(self, icon_path):
        try:
            icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(False, icon)
        except Exception as e:
            print(f"Error loading window icon: {e}")

    def select_day_wallpaper(self):
        self.day_wallpaper = filedialog.askopenfilename(title="Select Day Wallpaper")
    
    def select_night_wallpaper(self):
        self.night_wallpaper = filedialog.askopenfilename(title="Select Night Wallpaper")
    
    def save_settings(self):
        new_day_time = self.day_time_entry.get()
        new_night_time = self.night_time_entry.get()
        new_day_wallpaper = self.day_wallpaper
        new_night_wallpaper = self.night_wallpaper

        # Validate time format
        try:
            datetime.strptime(new_day_time, "%H:%M")
            datetime.strptime(new_night_time, "%H:%M")
        except ValueError:
            messagebox.showerror("Invalid Time Format", "Please enter valid time in HH:MM format.")
            return

        # Check if there are changes
        if (self.day_time != new_day_time or
            self.night_time != new_night_time or
            self.day_wallpaper != new_day_wallpaper or
            self.night_wallpaper != new_night_wallpaper):
            
            settings = {
                "day_wallpaper": new_day_wallpaper,
                "night_wallpaper": new_night_wallpaper,
                "day_time": new_day_time,
                "night_time": new_night_time
            }

            with open("settings.txt", "w") as f:
                for key, value in settings.items():
                    f.write(f"{key}:{value}\n")
            
            messagebox.showinfo("Settings Saved", "Settings saved successfully.")
            # Update instance variables with new settings
            self.day_time = new_day_time
            self.night_time = new_night_time
            self.day_wallpaper = new_day_wallpaper
            self.night_wallpaper = new_night_wallpaper
        else:
            messagebox.showerror("No Changes", "No changes detected. Please modify settings before saving.")

    def load_settings(self):
        if os.path.exists("settings.txt"):
            with open("settings.txt", "r") as f:
                for line in f:
                    parts = line.strip().split(":", 1)
                    if len(parts) == 2:
                        key, value = parts
                        if key == "day_wallpaper":
                            self.day_wallpaper = value
                        elif key == "night_wallpaper":
                            self.night_wallpaper = value
                        elif key == "day_time":
                            self.day_time_entry.delete(0, tk.END)
                            self.day_time_entry.insert(0, value)
                        elif key == "night_time":
                            self.night_time_entry.delete(0, tk.END)
                            self.night_time_entry.insert(0, value)

    def apply_initial_wallpaper(self):
        current_time = datetime.now().strftime("%H:%M")
        day_time = datetime.strptime(self.day_time, "%H:%M").time()
        night_time = datetime.strptime(self.night_time, "%H:%M").time()
        now = datetime.now().time()

        if day_time <= now < night_time:
            self.change_wallpaper(self.day_wallpaper)
        else:
            self.change_wallpaper(self.night_wallpaper)

    def run(self):
        while self.running:
            current_time = datetime.now().strftime("%H:%M")
            day_time = datetime.strptime(self.day_time, "%H:%M").time()
            night_time = datetime.strptime(self.night_time, "%H:%M").time()
            now = datetime.now().time()

            if day_time <= now < night_time and current_time == self.day_time:
                self.change_wallpaper(self.day_wallpaper)
            elif now >= night_time or now < day_time:
                self.change_wallpaper(self.night_wallpaper)

            time.sleep(60)
    
    def change_wallpaper(self, wallpaper_path):
        if wallpaper_path and os.path.exists(wallpaper_path) and wallpaper_path != self.current_wallpaper:
            try:
                ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 0x01 | 0x02)
                app_icon = self.notification_icon_path if os.path.exists(self.notification_icon_path) else None
                
                notification.notify(
                    title="Wallpaper Change",
                    message=f"The wallpaper has been changed to: {os.path.basename(wallpaper_path)}",
                    timeout=5,
                    app_icon=app_icon
                )
                self.current_wallpaper = wallpaper_path
            except Exception as e:
                print(f"Error changing wallpaper or showing notification: {e}")
        else:
            print(f"Invalid wallpaper path: {wallpaper_path}")

    
    def stop(self):
        self.running = False
        self.icon.stop()
        self.root.quit()

    def minimize_to_tray(self):
        self.root.withdraw()

    def on_tray_icon_click(self, icon, item):
        self.root.deiconify()

    def create_tray_icon(self):
        try:
            image = Image.open(self.window_icon_path)
            self.icon = pystray.Icon("WallpaperChanger", image, "Wallpaper Changer", menu=pystray.Menu(
                pystray.MenuItem("Open", self.on_tray_icon_click),
                pystray.MenuItem("Exit", self.stop)
            ))
            self.icon.run_detached()
        except Exception as e:
            print(f"Error loading tray icon: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WallpaperChangerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.minimize_to_tray)
    root.mainloop()
