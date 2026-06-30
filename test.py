import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from image_frame import ImageFrame

window_width, window_height = 400, 400
_GAP_SIZE = 3
_BORDER_SIZE = 3
_PADDING = 30

image = Image.open("C:\\Users\\Nils\\Desktop\\pic_select\\sample\\IMG_0095.png")

image_width, image_height = image.size

root = tk.Tk()
def close_app(event):
        root.destroy()
root.bind("<Escape>", close_app)
if True:
        root.attributes('-fullscreen', True)
        root.attributes("-topmost", True)

"""
border_frame = tk.Frame(root,
                        width=image_width + _GAP_SIZE + _BORDER_SIZE,
                        height=image_height + _GAP_SIZE + _BORDER_SIZE,
                        background="#074bb8")
gap_frame = tk.Frame(border_frame,
                        width=image_width + _GAP_SIZE,
                        height=image_height + _GAP_SIZE,
                        background="white")
tk_image = ImageTk.PhotoImage(image=image)
label = tk.Label(master=gap_frame, image=tk_image)

border_frame.pack_propagate(False)
gap_frame.pack_propagate(False)
label.pack_propagate(False)

label.pack(padx=_GAP_SIZE, pady=_GAP_SIZE)
gap_frame.pack(padx=_BORDER_SIZE, pady=_BORDER_SIZE)
border_frame.pack(side = "top", pady=50)
root.mainloop()

"""

image_frame = ImageFrame(master=root, image=image, max_image_size=(300, 300))
image_frame.place(relx=0.5, rely=0.5, anchor="center")

def on_space(event):
        image_frame.toggle_selected()

root.bind("<space>", on_space)

root.mainloop()