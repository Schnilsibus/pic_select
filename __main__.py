from .pic_select import start

# TODO: make resizable
# TODO: add window in which nothing will be loaded i.e.: -6 | -3 | current | 3 | 6 loaded till +/-6 but only once image +/-4 is reached will 3 new pictures be (un)loaded
# TODO: PROBLEM: reqesting new image during initial load seems to make the app stuck
# TODO: PROBLEM: sometimes code gets "stuck": rapid clicks will cause that you can only click from one to another load frame while the loader is executing a lot of consecutive BACK - FOR - BACK - FOR requests 


def main():
    start()

if __name__ == "__main__":
    main()



"""
def resize_image(self, event):
        # Extract new dimensions directly from the trigger event
        new_width = event.width
        new_height = event.height

        # Resize the pristine original image to current dimensions
        resized_img = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert into Tkinter-compatible PhotoImage format
        self.tk_image = ImageTk.PhotoImage(resized_img)

        # Update the existing canvas asset instead of drawing a new one
        self.canvas.itemconfigure(self.canvas_image_id, image=self.tk_image)
"""