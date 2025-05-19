import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os


class ImageCropperApp:
    def __init__(self, master):
        self.master = master
        master.title("Cropper")

        self.input_folder_path = ""
        self.output_folder_path = ""
        self.image_files = []
        self.current_image_index = -1
        self.original_image = None
        self.tk_image = None
        self.display_image_width = 0
        self.display_image_height = 0
        self.display_image_offset_x = 0
        self.display_image_offset_y = 0

        self.crop_rect_id = None
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_end_x = None
        self.crop_end_y = None
        self.current_crop_box_normalized = None 

        folder_frame = tk.Frame(master)
        folder_frame.pack(pady=10)

        self.btn_input_folder = tk.Button(folder_frame, text="Select Input Folder", command=self.select_input_folder)
        self.btn_input_folder.pack(side=tk.LEFT, padx=5)
        self.lbl_input_folder = tk.Label(folder_frame, text="No input folder selected")
        self.lbl_input_folder.pack(side=tk.LEFT, padx=5)

        self.btn_output_folder = tk.Button(folder_frame, text="Select Output Folder", command=self.select_output_folder)
        self.btn_output_folder.pack(side=tk.LEFT, padx=5)
        self.lbl_output_folder = tk.Label(folder_frame, text="No output folder selected")
        self.lbl_output_folder.pack(side=tk.LEFT, padx=5)

        self.canvas_width = 800
        self.canvas_height = 600
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height, bg="gray", relief=tk.SUNKEN, borderwidth=1)
        self.canvas.pack(pady=10, padx=10)
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        nav_frame = tk.Frame(master)
        nav_frame.pack(pady=10)

        self.btn_prev = tk.Button(nav_frame, text="<< Previous", command=self.prev_image, state=tk.DISABLED)
        self.btn_prev.pack(side=tk.LEFT, padx=5)

        self.btn_crop = tk.Button(nav_frame, text="Crop and Save", command=self.crop_and_save_image, state=tk.DISABLED)
        self.btn_crop.pack(side=tk.LEFT, padx=20)

        self.btn_next = tk.Button(nav_frame, text="Next >>", command=self.next_image, state=tk.DISABLED)
        self.btn_next.pack(side=tk.LEFT, padx=5)
        
        self.lbl_image_info = tk.Label(master, text="Load an image to start.")
        self.lbl_image_info.pack(pady=5)


    def select_input_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.input_folder_path = folder_selected
            self.lbl_input_folder.config(text=os.path.basename(folder_selected))
            self.load_image_list()
            self.update_navigation_buttons()
            if self.image_files:
                self.current_image_index = 0
                self.load_image_on_canvas()
                self.btn_crop.config(state=tk.NORMAL)
            else:
                self.lbl_image_info.config(text="No images found in the selected folder.")
                self.btn_crop.config(state=tk.DISABLED)
                if self.tk_image:
                    self.canvas.delete("all")
                    self.tk_image = None
                    self.original_image = None


    def select_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder_path = folder_selected
            self.lbl_output_folder.config(text=os.path.basename(folder_selected))


    def load_image_list(self):
        self.image_files = []
        if self.input_folder_path:
            valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp")
            for f_name in sorted(os.listdir(self.input_folder_path)):
                if f_name.lower().endswith(valid_extensions):
                    self.image_files.append(os.path.join(self.input_folder_path, f_name))
        self.current_image_index = -1


    def load_image_on_canvas(self):
        if not self.image_files or not (0 <= self.current_image_index < len(self.image_files)):
            self.lbl_image_info.config(text="No image to display or end of list.")
            self.original_image = None
            if self.tk_image:
                 self.canvas.delete("all")
                 self.tk_image = None
            self.btn_crop.config(state=tk.DISABLED)
            return

        image_path = self.image_files[self.current_image_index]
        try:
            self.original_image = Image.open(image_path)
            img_w, img_h = self.original_image.size

            ratio_w = self.canvas_width / img_w
            ratio_h = self.canvas_height / img_h
            scale_factor = min(ratio_w, ratio_h)

            self.display_image_width = int(img_w * scale_factor)
            self.display_image_height = int(img_h * scale_factor)
            
            self.display_image_offset_x = (self.canvas_width - self.display_image_width) // 2
            self.display_image_offset_y = (self.canvas_height - self.display_image_height) // 2

            resized_image = self.original_image.resize((self.display_image_width, self.display_image_height), Image.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(resized_image)

            self.canvas.delete("all")
            self.canvas.create_image(self.display_image_offset_x, self.display_image_offset_y, anchor=tk.NW, image=self.tk_image)
            self.lbl_image_info.config(text=f"Image: {os.path.basename(image_path)} ({self.current_image_index + 1}/{len(self.image_files)})")
            self.crop_rect_id = None
            self.current_crop_box_normalized = None
            self.btn_crop.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image {image_path}: {e}")
            self.original_image = None
            self.tk_image = None
            self.canvas.delete("all")
            if len(self.image_files) > 0:
                self.image_files.pop(self.current_image_index)
                if self.current_image_index >= len(self.image_files) and len(self.image_files) > 0:
                    self.current_image_index = len(self.image_files) -1
                
                if len(self.image_files) == 0:
                    self.current_image_index = -1 
                    self.lbl_image_info.config(text="No valid images left.")
                    self.btn_crop.config(state=tk.DISABLED)
                    self.update_navigation_buttons()
                    return
                self.load_image_on_canvas()
            else:
                 self.lbl_image_info.config(text="No images found or all failed to load.")
                 self.btn_crop.config(state=tk.DISABLED)
            self.update_navigation_buttons()


    def update_navigation_buttons(self):
        if not self.image_files or len(self.image_files) == 0:
            self.btn_prev.config(state=tk.DISABLED)
            self.btn_next.config(state=tk.DISABLED)
            if not self.original_image:
                self.btn_crop.config(state=tk.DISABLED)
            return

        if self.current_image_index <= 0:
            self.btn_prev.config(state=tk.DISABLED)
        else:
            self.btn_prev.config(state=tk.NORMAL)

        if self.current_image_index >= len(self.image_files) - 1:
            self.btn_next.config(state=tk.DISABLED)
        else:
            self.btn_next.config(state=tk.NORMAL)
        
        if self.original_image:
             self.btn_crop.config(state=tk.NORMAL)
        else:
             self.btn_crop.config(state=tk.DISABLED)


    def prev_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_image_on_canvas()
        self.update_navigation_buttons()


    def next_image(self):
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.load_image_on_canvas()
        elif self.current_image_index == len(self.image_files) -1:
            self.load_image_on_canvas()
            self.lbl_image_info.config(text=f"End of list. Image: {os.path.basename(self.image_files[self.current_image_index])} ({self.current_image_index + 1}/{len(self.image_files)})")
        self.update_navigation_buttons()


    def on_canvas_press(self, event):
        if not self.original_image: return

        self.crop_start_x = max(0, min(event.x - self.display_image_offset_x, self.display_image_width))
        self.crop_start_y = max(0, min(event.y - self.display_image_offset_y, self.display_image_height))
        
        if event.x < self.display_image_offset_x or \
           event.x > self.display_image_offset_x + self.display_image_width or \
           event.y < self.display_image_offset_y or \
           event.y > self.display_image_offset_y + self.display_image_height:
            self.crop_start_x = None
            self.crop_start_y = None
            if self.crop_rect_id:
                self.canvas.delete(self.crop_rect_id)
                self.crop_rect_id = None
            self.current_crop_box_normalized = None
            return


        if self.crop_rect_id:
            self.canvas.delete(self.crop_rect_id)
        self.crop_rect_id = self.canvas.create_rectangle(
            self.crop_start_x + self.display_image_offset_x,
            self.crop_start_y + self.display_image_offset_y,
            self.crop_start_x + self.display_image_offset_x,
            self.crop_start_y + self.display_image_offset_y,
            outline="red", width=2
        )


    def on_canvas_drag(self, event):
        if self.crop_rect_id and self.crop_start_x is not None:
            cur_x = max(0, min(event.x - self.display_image_offset_x, self.display_image_width))
            cur_y = max(0, min(event.y - self.display_image_offset_y, self.display_image_height))
            
            self.canvas.coords(self.crop_rect_id,
                               self.crop_start_x + self.display_image_offset_x,
                               self.crop_start_y + self.display_image_offset_y,
                               cur_x + self.display_image_offset_x,
                               cur_y + self.display_image_offset_y)


    def on_canvas_release(self, event):
        if self.crop_rect_id and self.crop_start_x is not None:
            raw_end_x = event.x - self.display_image_offset_x
            raw_end_y = event.y - self.display_image_offset_y

            self.crop_end_x = max(0, min(raw_end_x, self.display_image_width))
            self.crop_end_y = max(0, min(raw_end_y, self.display_image_height))

            norm_x1 = min(self.crop_start_x, self.crop_end_x)
            norm_y1 = min(self.crop_start_y, self.crop_end_y)
            norm_x2 = max(self.crop_start_x, self.crop_end_x)
            norm_y2 = max(self.crop_start_y, self.crop_end_y)

            if norm_x1 == norm_x2 or norm_y1 == norm_y2:
                self.canvas.delete(self.crop_rect_id)
                self.crop_rect_id = None
                self.current_crop_box_normalized = None
                self.crop_start_x = None
                return

            self.current_crop_box_normalized = (norm_x1, norm_y1, norm_x2, norm_y2)
            self.canvas.coords(self.crop_rect_id,
                               norm_x1 + self.display_image_offset_x,
                               norm_y1 + self.display_image_offset_y,
                               norm_x2 + self.display_image_offset_x,
                               norm_y2 + self.display_image_offset_y)


    def crop_and_save_image(self):
        if not self.original_image:
            messagebox.showerror("Error", "No image loaded to crop.")
            return
        if not self.current_crop_box_normalized:
            messagebox.showerror("Error", "No crop area selected. Drag on the image to select.")
            return
        if not self.output_folder_path:
            messagebox.showerror("Error", "Select an output folder first.")
            return

        try:
            orig_w, orig_h = self.original_image.size
            
            disp_x1, disp_y1, disp_x2, disp_y2 = self.current_crop_box_normalized

            actual_crop_x1 = int((disp_x1 / self.display_image_width) * orig_w)
            actual_crop_y1 = int((disp_y1 / self.display_image_height) * orig_h)
            actual_crop_x2 = int((disp_x2 / self.display_image_width) * orig_w)
            actual_crop_y2 = int((disp_y2 / self.display_image_height) * orig_h)

            actual_crop_x1 = max(0, actual_crop_x1)
            actual_crop_y1 = max(0, actual_crop_y1)
            actual_crop_x2 = min(orig_w, actual_crop_x2)
            actual_crop_y2 = min(orig_h, actual_crop_y2)

            if actual_crop_x1 >= actual_crop_x2 or actual_crop_y1 >= actual_crop_y2:
                messagebox.showerror("Error", "Crop dimensions are invalid.")
                return

            cropped_pil_image = self.original_image.crop((actual_crop_x1, actual_crop_y1, actual_crop_x2, actual_crop_y2))

            base, ext = os.path.splitext(os.path.basename(self.image_files[self.current_image_index]))
            output_filename = f"{base}_face{ext}"
            output_path = os.path.join(self.output_folder_path, output_filename)

            cropped_pil_image.save(output_path)

            if self.crop_rect_id:
                self.canvas.delete(self.crop_rect_id)
                self.crop_rect_id = None
            self.current_crop_box_normalized = None
            self.crop_start_x = None

            self.next_image()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to crop or save image: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCropperApp(root)
    root.mainloop()