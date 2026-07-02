import time
from PIL import Image, ImageOps, ImageTk
import tkinter as tk

root = tk.Tk()
root.withdraw()

max_size = (root.winfo_screenwidth(), root.winfo_screenmmheight())

images = [r"C:\Users\Nils\Desktop\pic_select\sample\IMG_0087.png",
          r"C:\Users\Nils\Desktop\pic_select\sample\IMG_0088.png",
          r"C:\Users\Nils\Desktop\pic_select\sample\IMG_0089.png",
          r"C:\Users\Nils\Desktop\pic_select\sample\IMG_0090.png",
          r"C:\Users\Nils\Desktop\pic_select\sample\IMG_0091.png",
          r"C:\Users\Nils\Desktop\pic_select\sample\IMG_0092.png",
          r"C:\Users\Nils\Desktop\pic_select\sample\IMG_0094.png",
          r"C:\Users\Nils\Desktop\pic_select\sample\IMG_0096.png",
          r"C:\Users\Nils\Desktop\pic_select\sample\IMG_0097.png",
          r"C:\Users\Nils\Desktop\pic_select\sample\IMG_0098.png",
          r"C:\Users\Nils\Desktop\pic_select\sample\IMG_0100.png"]


start = time.perf_counter()
image = Image.open(images[0])
end = time.perf_counter()
print(f"loading PIL image: {(end-start)*1000}ms")

start = time.perf_counter()
image.thumbnail(size=max_size, resample = Image.Resampling.LANCZOS)
end = time.perf_counter()
print(f"thubnail PIL image: {(end-start)*1000}ms")

start = time.perf_counter()
transposed_image: Image.Image = ImageOps.exif_transpose(image=image)
end = time.perf_counter()
print(f"transposing PIL image: {(end-start)*1000}ms")

start = time.perf_counter()
tk_image = ImageTk.PhotoImage(image=transposed_image)
end = time.perf_counter()
print(f"creating tk image: {(end-start)*1000}ms")

start = time.perf_counter()
image_label = tk.Label(master=root, image=tk_image)
end = time.perf_counter()
print(f"creating tk label: {(end-start)*1000}ms")

root.destroy()

"""
def exif_transpose(image):
    
    If an image has an EXIF Orientation tag, other than 1, return a new image
    that is transposed accordingly. The new image will have the orientation
    data removed.

    Otherwise, return a copy of the image.

    :param image: The image to transpose.
    :return: An image.
    
    exif = image.getexif()
    orientation = exif.get(0x0112)
    method = {
        2: Image.Transpose.FLIP_LEFT_RIGHT,
        3: Image.Transpose.ROTATE_180,
        4: Image.Transpose.FLIP_TOP_BOTTOM,
        5: Image.Transpose.TRANSPOSE,
        6: Image.Transpose.ROTATE_270,
        7: Image.Transpose.TRANSVERSE,
        8: Image.Transpose.ROTATE_90,
    }.get(orientation)
    if method is not None:
        transposed_image = image.transpose(method)
        transposed_exif = transposed_image.getexif()
        if 0x0112 in transposed_exif:
            del transposed_exif[0x0112]
            if "exif" in transposed_image.info:
                transposed_image.info["exif"] = transposed_exif.tobytes()
            elif "Raw profile type exif" in transposed_image.info:
                transposed_image.info[
                    "Raw profile type exif"
                ] = transposed_exif.tobytes().hex()
            elif "XML:com.adobe.xmp" in transposed_image.info:
                for pattern in (
                    r'tiff:Orientation="([0-9])"',
                    r"<tiff:Orientation>([0-9])</tiff:Orientation>",
                ):
                    transposed_image.info["XML:com.adobe.xmp"] = re.sub(
                        pattern, "", transposed_image.info["XML:com.adobe.xmp"]
                    )
        return transposed_image
    return image.copy()
"""