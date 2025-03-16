# pyinstaller --onefile --noconsole --hidden-import fitz --hidden-import PIL --hidden-import customtkinter smart_pdf.py --name "PDF-Splitter_1.0.exe"
import fitz  # PyMuPDF for PDF processing
import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw

ctk.set_appearance_mode("dark")  # Set dark mode
ctk.set_default_color_theme("blue")

class PDFSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Splitter PCN v1.0 - 0 files to be split")
        self.root.state("zoomed")  # Maximized window at start

        self.pdf_path = None
        self.doc = None
        self.page_images = []
        self.tk_images = []
        self.page_buttons = []
        self.split_positions = set()
        self.split_folder = None

        # Top frame
        top_frame = ctk.CTkFrame(root)
        top_frame.pack(pady=10, fill="x", padx=10)

        self.btn_open = ctk.CTkButton(top_frame, text="Open PDF", command=self.load_pdf)
        self.btn_open.pack(side="left", padx=10)

        self.file_path_label = ctk.CTkLabel(top_frame, text="No file selected", anchor="w")
        self.file_path_label.pack(side="left", expand=True, fill="x", padx=10)

        self.btn_save = ctk.CTkButton(top_frame, text="Save Split PDFs", command=self.split_pdf)
        self.btn_save.pack(side="right", padx=10)

        # Split folder frame
        self.split_folder_frame = ctk.CTkFrame(root)
        self.split_folder_frame.pack(pady=5, fill="x", padx=10)
        self.split_folder_frame.pack_forget()

        self.btn_open_folder = ctk.CTkButton(self.split_folder_frame, text="Open Split Folder", command=self.open_split_folder)
        self.btn_open_folder.pack(side="left", padx=10)

        self.split_folder_label = ctk.CTkLabel(self.split_folder_frame, text="", anchor="w")
        self.split_folder_label.pack(side="left", expand=True, fill="x")

        # Scrollable thumbnails
        self.scrollable_frame = ctk.CTkScrollableFrame(root)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def load_pdf(self):
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not self.pdf_path:
            return

        self.doc = fitz.open(self.pdf_path)
        total_pages = len(self.doc)

        self.file_path_label.configure(text=f"Selected: {self.pdf_path} (Total pages: {total_pages})")

        self.page_images = [self.render_page(i) for i in range(total_pages)]
        self.tk_images.clear()

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.page_buttons.clear()
        self.split_positions.clear()
        self.update_window_title()

        for i, img in enumerate(self.page_images):
            img_with_line = self.add_split_marker(img, i)

            ctk_image = ctk.CTkImage(light_image=img_with_line, dark_image=img_with_line, size=(280, 380))

            self.tk_images.append(ctk_image)

            frame = ctk.CTkFrame(self.scrollable_frame)
            frame.grid(row=i // 6, column=i % 6, padx=5, pady=5)

            btn_img = ctk.CTkButton(frame, image=ctk_image, text="", command=lambda i=i: self.toggle_split_marker(i))
            btn_img.pack()

            btn_page = ctk.CTkButton(frame, text=f"Page {i+1}/{total_pages}", command=lambda i=i: self.show_full_page(i))
            btn_page.pack(pady=5)

            self.page_buttons.append(btn_img)

    def show_full_page(self, page_index):
        def rotate_image(angle):
            nonlocal img, ctk_img
            img = img.rotate(angle, expand=True)

            width, height = img.size
            if rotation_count[0] % 2 == 0:
                display_size = (880, 660)
                full_window.geometry("1000x880")
            else:
                display_size = (660, 880)
                full_window.geometry("880x1000")

            resized_img = img.resize(display_size, Image.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=resized_img, dark_image=resized_img, size=display_size)
            label.configure(image=ctk_img)
            label.image = ctk_img

        full_window = ctk.CTkToplevel(self.root)
        full_window.title(f"Page {page_index + 1}")
        full_window.geometry("880x1000")
        full_window.attributes('-topmost', True)

        pix = self.doc[page_index].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img = img.resize((660, 880), Image.LANCZOS)

        rotation_count = [0]

        btn_frame = ctk.CTkFrame(full_window)
        btn_frame.pack(pady=5)

        btn_rotate_left = ctk.CTkButton(btn_frame, text="⟲ Rotate Left", command=lambda: [rotate_image(90),
                                                                                          rotation_count.__setitem__(0,
                                                                                                                     rotation_count[
                                                                                                                         0] - 1)])
        btn_rotate_left.pack(side="left", padx=5)

        btn_rotate_right = ctk.CTkButton(btn_frame, text="Rotate Right ⟳", command=lambda: [rotate_image(-90),
                                                                                            rotation_count.__setitem__(
                                                                                                0,
                                                                                                rotation_count[0] + 1)])
        btn_rotate_right.pack(side="left", padx=5)

        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(660, 880))

        label = ctk.CTkLabel(full_window, image=ctk_img, text="")
        label.image = ctk_img
        label.pack()

    def show_full_page2(self, page_index):

        full_window = ctk.CTkToplevel(self.root)
        full_window.title(f"Page {page_index + 1}")
        full_window.geometry("800x1000")
        full_window.attributes('-topmost', True)

        pix = self.doc[page_index].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img = img.resize((660, 880), Image.LANCZOS)

        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(660, 880))

        label = ctk.CTkLabel(full_window, image=ctk_img, text="")
        label.image = ctk_img  # Prevent garbage collection
        label.pack()


    def render_page(self, page_index):
        pix = self.doc[page_index].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return img.resize((280, 380), Image.LANCZOS)

    def add_split_marker(self, img, page_index):
        img_copy = img.copy()
        draw = ImageDraw.Draw(img_copy)
        if page_index in self.split_positions:
            draw.line([(img_copy.width - 5, 0), (img_copy.width - 5, img_copy.height)], fill="red", width=3)
        return img_copy

    def toggle_split_marker(self, page_index):
        if page_index in self.split_positions:
            self.split_positions.remove(page_index)
        else:
            self.split_positions.add(page_index)

        img_with_line = self.add_split_marker(self.render_page(page_index), page_index)

        ctk_image = ctk.CTkImage(light_image=img_with_line, dark_image=img_with_line, size=(280, 380))

        self.tk_images[page_index] = ctk_image
        self.page_buttons[page_index].configure(image=ctk_image)

        self.update_window_title()



    def split_pdf(self):
        if not self.split_positions:
            messagebox.showwarning("Warning", "No split points selected!")
            return

        self.split_folder = filedialog.askdirectory(title="Select Folder to Save Split PDFs")
        if not self.split_folder:
            return

        sorted_positions = sorted(self.split_positions)
        start = 0
        original_name = os.path.splitext(os.path.basename(self.pdf_path))[0]

        for i, split_pos in enumerate(sorted_positions):
            output_filename = f"{original_name}_part{i+1}_pages_{start+1}-{split_pos+1}.pdf"
            output_path = os.path.join(self.split_folder, output_filename)

            new_doc = fitz.open()
            new_doc.insert_pdf(self.doc, from_page=start, to_page=split_pos)
            new_doc.save(output_path)
            new_doc.close()

            start = split_pos + 1

        messagebox.showinfo("Success", f"PDF split into {len(sorted_positions) + 1} parts!")
        self.split_folder_label.configure(text=self.split_folder)
        self.split_folder_frame.pack()

    def open_split_folder(self):
        if self.split_folder and os.path.exists(self.split_folder):
            os.startfile(self.split_folder)

    def update_window_title(self):
        num_splits = len(self.split_positions) + 1 if self.split_positions else 0
        self.root.title(f"PDF Splitter PNC- {num_splits} files to be split")

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1000x900")
    app = PDFSplitterApp(root)
    root.mainloop()
