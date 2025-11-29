import tkinter as tk
from PIL import Image, ImageTk
import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from business.game_manager import GameManager
from presentation.camera_feed import CameraFeed

class GraphWindow:
    """ a seperate window for the win/loss/draw chart """
    def __init__(self, master, game_manager: GameManager):
        self.game = game_manager
        self.root = tk.Toplevel(master)
        self.root.title("Win/Loss/Draw Chart")
        self.figure = Figure(figsize=(4,4))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack()
        self.update_chart()

    def update_chart(self):
        self.ax.clear()
        self.ax.bar(
            ["Wins","Losses","Draws"],
            [self.game.wins, self.game.losses, self.game.draws],
            color=['green','red','gray']
        )
        self.ax.set_ylim(0, max(1, self.game.wins + self.game.losses + self.game.draws))
        self.canvas.draw()

class GameWindowTk:
    """ main tkinter window (temporary) with camera and history """
    def __init__(self, root):
        self.root = root
        self.root.title("RPS Prototype - Tkinter")
        self.root.geometry("900x500")
        self.root.configure(bg="black")

        self.game = GameManager()
        self.cam = CameraFeed()
        self.cam_size = 400

        # camera feed
        self.cam_label = tk.Label(root, bg="black")
        self.cam_label.place(x=50, y=50, width=self.cam_size, height=self.cam_size)

        # last 3 rounds (memory only, no db yet)
        self.last_rounds = []  # store last rounds in memory
        self.history_labels = []
        for i in range(3):
            lbl = tk.Label(root, text="---", fg="white", bg="black", font=("Arial", 16))
            lbl.place(x=500, y=50 + i*40)
            self.history_labels.append(lbl)

        # stats
        self.stats_var = tk.StringVar()
        self.stats_var.set("Wins: 0 *** Losses: 0 *** Draws: 0")
        self.stats_label = tk.Label(root, textvariable=self.stats_var, fg="white", bg="black", font=("Arial", 16))
        self.stats_label.place(x=500, y=200)

        # instrcutions
        self.instruction_var = tk.StringVar()
        self.instruction_var.set("Press R/P/S keys to play *** Press ESC to exit")
        self.instruction_label = tk.Label(root, textvariable=self.instruction_var, fg="white", bg="black", font=("Arial", 16))
        self.instruction_label.place(x=50, y=470)

        # graph window
        self.graph_window = GraphWindow(self.root, self.game)

        # bind keys
        self.root.bind("<Key>", self.key_pressed)
        self.root.bind("<Escape>", lambda e: self.on_close())  # esc to exit

        # camera loop
        self.update_camera()

    def update_camera(self):
        frame = self.cam.get_frame()
        if frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((self.cam_size, self.cam_size))
            imgtk = ImageTk.PhotoImage(image=img)
            self.cam_label.imgtk = imgtk
            self.cam_label.configure(image=imgtk)

        self.root.after(30, self.update_camera)

    def key_pressed(self, event):
        key = event.char.lower()
        if key not in ["r","p","s"]:
            return
        result = self.game.play_round(key)

        # update last 3 rounds in memory
        self.last_rounds.append(result)
        self.last_rounds = self.last_rounds[-3:]  # keep only last 3

        for i, r in enumerate(self.last_rounds):
            self.history_labels[i].config(
                text=f"You: {r['player_move']} *** Computer: {r['computer_move']} *** {r['result'].upper()}"
            )
        # fill any remaining labels if less than 3 rounds
        for i in range(len(self.last_rounds), 3):
            self.history_labels[i].config(text="---")

        # update stats
        self.stats_var.set(f"Wins: {self.game.wins} *** Losses: {self.game.losses} *** Draws: {self.game.draws}")
        # update graph
        self.graph_window.update_chart()

    def on_close(self):
        self.cam.release()
        self.root.destroy()

def launch_game_window_tk():
    root = tk.Tk()
    app = GameWindowTk(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()