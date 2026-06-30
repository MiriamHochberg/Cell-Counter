"""
cell_main.py - the Cell Counter app. THIS is the file you run.

Run this file and a window opens:
  Home screen  -> click the white box to pick a .jpg of cells
  Results      -> the image with red circles on every cell, and a count
                  - click a red circle to REMOVE it (count goes down)
                  - click empty space to ADD one (count goes up)
                  - Save  -> writes the count + the circled image to results/
                  - Upload another image -> back to the home screen

The actual cell-finding lives in cell_detect.py, which this imports.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw

import cell_detect

# ---- Colors (navy window, orange border) ----
NAVY = "#0a1f44"
ORANGE = "#d97757"
WHITE = "#ffffff"
RED = "#ff0000"

BORDER = 14              # thickness of the orange border
DISPLAY_MAX = (1000, 700)  # biggest the image is shown on screen
CIRCLE_RADIUS = 7        # red circle size, in original-image pixels
CLICK_TOLERANCE = 13     # how close (screen pixels) a click must be to remove


class CellCounterApp:
    def __init__(self, root):
        self.root = root
        root.title("Cell Counter")
        root.configure(bg=ORANGE)            # orange shows through as the border

        # Navy area inside the orange border.
        self.container = tk.Frame(root, bg=NAVY)
        self.container.pack(fill="both", expand=True, padx=BORDER, pady=BORDER)

        self.image_path = None
        self.pil_image = None     # full-resolution PIL image
        self.scale = 1.0          # screen size = image size * scale
        self.cells = []           # (x, y) points in ORIGINAL image coordinates
        self.tk_image = None      # keep a reference so it is not garbage-collected

        self.show_home()

    # ---- small helper: a colored, clickable "button" (a Label, so the
    #      colors actually show on macOS) ----
    def _button(self, parent, text, command, bg, fg):
        b = tk.Label(parent, text=text, bg=bg, fg=fg,
                     font=("Helvetica", 14, "bold"),
                     padx=16, pady=8, cursor="hand2")
        b.bind("<Button-1>", lambda e: command())
        return b

    def _clear(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ---- Home screen ----
    def show_home(self):
        self._clear()
        self.cells = []
        center = tk.Frame(self.container, bg=NAVY)
        center.place(relx=0.5, rely=0.5, anchor="center")
        box = tk.Label(center, text="Click Here to Upload\nImage of Cells",
                       bg=WHITE, fg=NAVY, font=("Helvetica", 24, "bold"),
                       padx=50, pady=50, cursor="hand2")
        box.pack()
        box.bind("<Button-1>", lambda e: self.upload())

    # ---- Pick a file and run detection ----
    def upload(self):
        path = filedialog.askopenfilename(
            title="Choose a cell image",
            filetypes=[("JPEG images", "*.jpg *.jpeg"), ("All files", "*.*")])
        if not path:
            return
        self.image_path = path
        self.pil_image = Image.open(path).convert("RGB")
        try:
            self.cells = cell_detect.find_cells(path)
        except Exception as exc:
            messagebox.showerror("Detection error", str(exc))
            return
        self.show_results()

    # ---- Results screen ----
    def show_results(self):
        self._clear()

        w0, h0 = self.pil_image.size
        max_w, max_h = DISPLAY_MAX
        self.scale = min(max_w / w0, max_h / h0, 1.0)
        disp_w, disp_h = int(w0 * self.scale), int(h0 * self.scale)

        bar = tk.Frame(self.container, bg=NAVY)
        bar.pack(fill="x", pady=(6, 4), padx=6)

        self.count_var = tk.StringVar()
        self._update_count()
        tk.Label(bar, textvariable=self.count_var, bg=NAVY, fg=WHITE,
                 font=("Helvetica", 20, "bold")).pack(side="left", padx=6)
        self._button(bar, "Upload another image", self.show_home,
                     WHITE, NAVY).pack(side="right", padx=4)
        self._button(bar, "Save", self.save, ORANGE, WHITE).pack(side="right", padx=4)

        hint = tk.Label(self.container,
                        text="Click a circle to remove it  -  click empty space to add one",
                        bg=NAVY, fg=WHITE, font=("Helvetica", 12))
        hint.pack(pady=(0, 4))

        display = self.pil_image.resize((disp_w, disp_h))
        self.tk_image = ImageTk.PhotoImage(display)
        self.canvas = tk.Canvas(self.container, width=disp_w, height=disp_h,
                                highlightthickness=0, bg="black")
        self.canvas.pack(padx=6, pady=6)
        self.canvas.bind("<Button-1>", self.on_click)
        self._redraw()

    def _redraw(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        r = max(CIRCLE_RADIUS * self.scale, 5)
        for (x, y) in self.cells:
            cx, cy = x * self.scale, y * self.scale
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                    outline=RED, width=2)

    def _update_count(self):
        self.count_var.set(f"Found {len(self.cells)} cells")

    # ---- Click to add / remove ----
    def on_click(self, event):
        # Is the click on (near) an existing circle? Remove the closest one.
        nearest = None
        nearest_dist = CLICK_TOLERANCE
        for i, (x, y) in enumerate(self.cells):
            dx = event.x - x * self.scale
            dy = event.y - y * self.scale
            dist = (dx * dx + dy * dy) ** 0.5
            if dist <= nearest_dist:
                nearest_dist = dist
                nearest = i
        if nearest is not None:
            self.cells.pop(nearest)
        else:
            # Otherwise add a circle where they clicked (no checking - generous).
            self.cells.append((int(event.x / self.scale), int(event.y / self.scale)))
        self._update_count()
        self._redraw()

    # ---- Save: a .txt with the total, and the circled image, into results/ ----
    def save(self):
        project_dir = os.path.dirname(os.path.abspath(__file__))
        results_dir = os.path.join(project_dir, "results")
        os.makedirs(results_dir, exist_ok=True)

        base = os.path.splitext(os.path.basename(self.image_path))[0]

        out_img = self.pil_image.copy()
        draw = ImageDraw.Draw(out_img)
        r = CIRCLE_RADIUS
        for (x, y) in self.cells:
            draw.ellipse([x - r, y - r, x + r, y + r], outline=(255, 0, 0), width=2)
        img_out = os.path.join(results_dir, f"{base}_counted.jpg")
        out_img.save(img_out)

        txt_out = os.path.join(results_dir, f"{base}_counted.txt")
        with open(txt_out, "w") as f:
            f.write(f"Cell count: {len(self.cells)}\n")

        messagebox.showinfo(
            "Saved",
            f"Saved to the results folder:\n\n{base}_counted.jpg\n{base}_counted.txt")


def main():
    root = tk.Tk()
    root.geometry("1060x820")
    CellCounterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
