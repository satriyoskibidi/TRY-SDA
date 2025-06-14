import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import csv
import os
import time

class KataScoringApp(tk.Frame):
    def __init__(self, master, parent=None):
        super().__init__(master)
        self.master = master
        self.parent = parent

        self.ao_score = 0
        self.aka_score = 0
        self.ao_time = 0
        self.aka_time = 0
        self.ao_running = False
        self.aka_running = False
        self.ao_start_time = None
        self.aka_start_time = None
        self.stopwatch_visible = True
        self.ao_started = False
        self.aka_started = False

        self.setup_ui()
        self.update_timers()

    def setup_ui(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(current_dir, "assets", "gradasi.jpg")
        bg_image = Image.open(bg_path).resize((360, 640))
        self.bg_photo = ImageTk.PhotoImage(bg_image)

        self.canvas = tk.Canvas(self, width=360, height=640)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

        self.canvas.create_rectangle(10, 150, 175, 450, fill="blue", outline="")
        self.canvas.create_rectangle(185, 150, 350, 450, fill="red", outline="")

        self.canvas.create_text(20, 120, text="Division:", fill="white", font=("Inter", 10, "bold"), anchor="w")
        self.canvas.create_text(250, 120, text="Judges:", fill="white", font=("Inter", 10, "bold"), anchor="w")
        self.division_entry = self._create_entry(145, 120, 22)
        self.judges_entry = self._create_entry(318, 120, 5)

        # AO & AKA dropdown for kata selection
        self.canvas.create_text(30, 180, text="Ao:", fill="white", font=("Inter", 10, "bold"), anchor="w")
        self.ao_kata = ttk.Combobox(self.master, values=[
            "Kanku Sho", "Kanku Dai", "Bassai Dai", "Bassai Sho", 
            "Jion", "Empi", "Hangetsu", "Gankaku", 
            "Tekki Shodan", "Tekki Nidan", "Tekki Sandan"
        ], width=10, state="readonly")
        self.ao_kata.set("Pilih Kata")
        self.canvas.create_window(100, 180, window=self.ao_kata)
        
        self.canvas.create_text(210, 180, text="Aka:", fill="white", font=("Inter", 10, "bold"), anchor="w")
        self.aka_kata = ttk.Combobox(self.master, values=[
            "Kanku Sho", "Kanku Dai", "Bassai Dai", "Bassai Sho", 
            "Jion", "Empi", "Hangetsu", "Gankaku", 
            "Tekki Shodan", "Tekki Nidan", "Tekki Sandan"
        ], width=10, state="readonly")
        self.aka_kata.set("Pilih Kata")
        self.canvas.create_window(287, 180, window=self.aka_kata)

        self.ao_score_label = self._create_label("0", 125, 233, size=36, color="white", bg="blue")
        self.aka_score_label = self._create_label("0", 300, 233, size=36, color="white", bg="red")

        self.ao_timer_label = tk.Label(self.master, text="0:00", font=("Inter", 12, "bold"), fg="white", bg="navy")
        self.ao_timer_label_id = self.canvas.create_window(90, 335, window=self.ao_timer_label)
        self.aka_timer_label = tk.Label(self.master, text="0:00", font=("Inter", 12, "bold"), fg="white", bg="darkred")
        self.aka_timer_label_id = self.canvas.create_window(265, 335, window=self.aka_timer_label)

        self._create_button("-1", lambda: self.change_score("ao", -1), 60, 295)
        self._create_button("+1", lambda: self.change_score("ao", 1), 120, 295)
        self._create_button("-1", lambda: self.change_score("aka", -1), 232, 295)
        self._create_button("+1", lambda: self.change_score("aka", 1), 300, 295)

        self._create_button("Shikkaku", lambda: self.disqualify("ao"), 55, 375, width=7, bg="midnightblue", fg="white")
        self._create_button("Kiken", lambda: self.retire("ao"), 130, 375, width=7, bg="midnightblue", fg="white")
        self._create_button("Shikkaku", lambda: self.disqualify("aka"), 228, 375, width=7, bg="darkred", fg="white")
        self._create_button("Kiken", lambda: self.retire("aka"), 300, 375, width=7, bg="darkred", fg="white")

        self.ao_start_btn = self._create_button("START", self.start_ao_timer, 90, 420, bg="limegreen")
        self.aka_start_btn = self._create_button("START", self.start_aka_timer, 270, 420, bg="limegreen")

        self.toggle_btn = self._create_button("SHOW/HIDE STOPWATCH", self.toggle_stopwatch, 180, 490, width=20, bg="limegreen")

        self.done_btn = self._create_button("DONE", self.save_scores, 100, 520, bg="limegreen")
        self.reset_btn = self._create_button("RESET", self.reset_all, 250, 520, bg="limegreen")

        self.back_btn = self._create_button("BACK", self.go_back, 180, 540, bg="navy", fg="white")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        biru_img_path = os.path.join(current_dir, "assets", "BLUE.png")
        merah_img_path = os.path.join(current_dir, "assets", "RED.png")

        self.biru_photo = ImageTk.PhotoImage(Image.open(biru_img_path))
        self.merah_photo = ImageTk.PhotoImage(Image.open(merah_img_path))

        self.canvas.create_image(65, 233, image=self.biru_photo, anchor="center")
        self.canvas.create_image(240, 233, image=self.merah_photo, anchor="center")

    def _create_entry(self, x, y, width):
        entry = tk.Entry(self.master, width=width)
        self.canvas.create_window(x, y, window=entry)
        return entry

    def _create_label(self, text, x, y, size=12, color="black", bg=None):
        label = tk.Label(self.master, text=text, font=("Inter", size, "bold"), fg=color, bg=bg)
        self.canvas.create_window(x, y, window=label)
        return label

    def _create_button(self, text, command, x, y, width=5, bg="white", fg="black"):
        button = tk.Button(self.master, text=text, command=command, width=width, bg=bg, fg=fg, cursor="hand2")
        self.canvas.create_window(x, y, window=button)
        return button

    def change_score(self, side, amount):
        if side == "ao":
            self.ao_score += amount
            self.ao_score_label.config(text=str(self.ao_score))
        else:
            self.aka_score += amount
            self.aka_score_label.config(text=str(self.aka_score))

    def disqualify(self, side):
        messagebox.showinfo("Diskualifikasi", f"Pemain {side.upper()} terdiskualifikasi")

    def retire(self, side):
        messagebox.showinfo("Kiken", f"Pemain {side.upper()} telah mengundurkan diri")

    def start_ao_timer(self):
        if self.ao_kata.get() == "Pilih Kata":
            messagebox.showwarning("Peringatan", "Silakan pilih kata untuk Ao terlebih dahulu")
            return
        self.ao_started = True
        self.aka_running = False
        self.ao_running = True
        self.ao_start_time = time.time() - self.ao_time

    def start_aka_timer(self):
        if self.aka_kata.get() == "Pilih Kata":
            messagebox.showwarning("Peringatan", "Silakan pilih kata untuk Aka terlebih dahulu")
            return
        self.aka_started = True
        self.ao_running = False
        self.aka_running = True
        self.aka_start_time = time.time() - self.aka_time

    def update_timers(self):
        if self.ao_running:
            self.ao_time = time.time() - self.ao_start_time
            mins, secs = divmod(int(self.ao_time), 60)
            self.ao_timer_label.config(text=f"{mins}:{secs:02}")
        if self.aka_running:
            self.aka_time = time.time() - self.aka_start_time
            mins, secs = divmod(int(self.aka_time), 60)
            self.aka_timer_label.config(text=f"{mins}:{secs:02}")

        self.master.after(1000, self.update_timers)

    def toggle_stopwatch(self):
        self.stopwatch_visible = not self.stopwatch_visible
        state = "normal" if self.stopwatch_visible else "hidden"
        self.canvas.itemconfigure(self.ao_timer_label_id, state=state)
        self.canvas.itemconfigure(self.aka_timer_label_id, state=state)

    def save_scores(self):
        self.ao_running = False
        self.aka_running = False

        division = self.division_entry.get()
        file_path = os.path.join(os.path.dirname(__file__), "scores.csv")
        file_exists = os.path.isfile(file_path)

        rows = []
        if self.ao_started and not self.aka_started:
            rows.append([division, "AO", self.ao_kata.get(), self.ao_score, int(self.ao_time)])
        elif self.aka_started and not self.ao_started:
            rows.append([division, "AKA", self.aka_kata.get(), self.aka_score, int(self.aka_time)])
        elif self.ao_started and self.aka_started:
            rows.append([division, "AO", self.ao_kata.get(), self.ao_score, int(self.ao_time)])
            rows.append([division, "AKA", self.aka_kata.get(), self.aka_score, int(self.aka_time)])
        else:
            messagebox.showwarning("Peringatan", "Belum ada pertandingan yang dimulai.")
            return

        with open(file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Division", "Side", "Kata", "Score", "Time"])
            for row in rows:
                writer.writerow(row)
        messagebox.showinfo("Simpan", "Data telah disimpan.")

    def reset_all(self):
        self.ao_score = 0
        self.aka_score = 0
        self.ao_time = 0
        self.aka_time = 0
        self.ao_running = False
        self.aka_running = False
        self.ao_started = False
        self.aka_started = False
        self.ao_score_label.config(text="0")
        self.aka_score_label.config(text="0")
        self.ao_timer_label.config(text="0:00")
        self.aka_timer_label.config(text="0:00")
        self.ao_kata.set("Pilih Kata")
        self.aka_kata.set("Pilih Kata")

    def go_back(self):
        self.master.destroy()
        from page_second import open_second_page
        open_second_page(parent=self.parent)

def open_third_page(parent=None):
    window = tk.Toplevel(parent) if parent else tk.Tk()
    window.title("Project - Kata Scoring")
    app = KataScoringApp(window, parent=parent)
    app.pack(fill="both", expand=True)
    window.geometry("360x640")
    window.resizable(False, False)
    window.mainloop()

if __name__ == "__main__":
    open_third_page()
