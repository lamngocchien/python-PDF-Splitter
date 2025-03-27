
import fitz  # PyMuPDF
import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PDFSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Splitter PCN V2.0 - 0 files selected")
        self.root.state("zoomed")

        # Multi-file data structures
        self.pdf_docs = {}         # filename -> fitz.Document
        self.page_images = {}      # filename -> list[Image]
        self.tk_images = {}        # filename -> list[CTkImage]
        self.page_buttons = {}     # filename -> list[Button]
        self.split_positions = {}  # filename -> set[int]
        self.pdf_paths = []        # list of file paths
        self.split_folder = None

        # UI components
        top_frame = ctk.CTkFrame(root)
        top_frame.pack(pady=10, fill="x", padx=10)

        self.btn_open = ctk.CTkButton(top_frame, text="Open PDFs", command=self.load_pdfs)
        self.btn_open.pack(side="left", padx=10)

        self.file_path_label = ctk.CTkLabel(top_frame, text="No file selected", anchor="w")
        self.file_path_label.pack(side="left", expand=True, fill="x", padx=10)

        self.btn_save = ctk.CTkButton(top_frame, text="Save Split PDFs", command=self.split_all_pdfs)
        self.btn_save.pack(side="right", padx=10)

        self.split_folder_frame = ctk.CTkFrame(root)
        self.split_folder_frame.pack(pady=5, fill="x", padx=10)
        self.split_folder_frame.pack_forget()

        self.btn_open_folder = ctk.CTkButton(self.split_folder_frame, text="Open Split Folder", command=self.open_split_folder)
        self.btn_open_folder.pack(side="left", padx=10)

        self.split_folder_label = ctk.CTkLabel(self.split_folder_frame, text="", anchor="w")
        self.split_folder_label.pack(side="left", expand=True, fill="x")

        self.scrollable_frame = ctk.CTkScrollableFrame(root)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def load_pdfs(self):
        self.pdf_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if not self.pdf_paths:
            return

        # Reset trạng thái
        self.pdf_docs.clear()
        self.page_images.clear()
        self.tk_images.clear()
        self.page_buttons.clear()
        self.split_positions.clear()

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for file_index, path in enumerate(self.pdf_paths):
            doc = fitz.open(path)
            filename = os.path.basename(path)

            self.pdf_docs[filename] = doc
            self.page_images[filename] = [self.render_page(doc, i) for i in range(len(doc))]
            self.tk_images[filename] = []
            self.page_buttons[filename] = []
            self.split_positions[filename] = set()

            # Gán label cho mỗi file
            label = ctk.CTkLabel(self.scrollable_frame, text=f"📄 {filename}", anchor="w", font=("Arial", 16, "bold"))
            label.grid(column=0, row=file_index * 1000, sticky="w", padx=10, pady=(10, 0), columnspan=6)

            for i, img in enumerate(self.page_images[filename]):
                img_with_line = self.add_split_marker(img, filename, i)
                ctk_image = ctk.CTkImage(light_image=img_with_line, dark_image=img_with_line, size=(280, 380))
                self.tk_images[filename].append(ctk_image)

                frame = ctk.CTkFrame(self.scrollable_frame)
                frame.grid(row=(i // 6 + 1) + file_index * 1000, column=i % 6, padx=5, pady=5)

                btn_img = ctk.CTkButton(frame, image=ctk_image, text="",
                                        command=lambda f=filename, i=i: self.toggle_split_marker(f, i))
                btn_img.pack()

                btn_page = ctk.CTkButton(frame, text=f"Page {i + 1}/{len(doc)}",
                                         command=lambda f=filename, i=i: self.show_full_page(f, i))
                btn_page.pack(pady=5)

                self.page_buttons[filename].append(btn_img)

        self.file_path_label.configure(text=f"{len(self.pdf_paths)} file(s) loaded.")
        self.update_window_title()

    def render_page(self, doc, page_index):
        pix = doc[page_index].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return img.resize((280, 380), Image.LANCZOS)

    def add_split_marker(self, img, filename, page_index):
        img_copy = img.copy()
        draw = ImageDraw.Draw(img_copy)
        if page_index in self.split_positions[filename]:
            draw.line([(img_copy.width - 5, 0), (img_copy.width - 5, img_copy.height)], fill="red", width=3)
        return img_copy

    def toggle_split_marker(self, filename, page_index):
        last_page_index = len(self.page_images[filename]) - 1

        if page_index in self.split_positions[filename]:
            self.split_positions[filename].remove(page_index)
        else:
            self.split_positions[filename].add(page_index)

        self.split_positions[filename].add(last_page_index)

        for i in {page_index, last_page_index}:
            img = self.render_page(self.pdf_docs[filename], i)
            img_with_line = self.add_split_marker(img, filename, i)
            ctk_image = ctk.CTkImage(light_image=img_with_line, dark_image=img_with_line, size=(280, 380))
            self.tk_images[filename][i] = ctk_image
            self.page_buttons[filename][i].configure(image=ctk_image)

        self.update_window_title()

    def show_full_page(self, filename, page_index):
        doc = self.pdf_docs[filename]

        full_window = ctk.CTkToplevel(self.root)
        full_window.title(f"{filename} - Page {page_index + 1}")
        full_window.geometry("880x1000")
        full_window.attributes('-topmost', True)

        pix = doc[page_index].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img = img.resize((660, 880), Image.LANCZOS)

        rotation_count = [0]

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

        btn_frame = ctk.CTkFrame(full_window)
        btn_frame.pack(pady=5)

        btn_rotate_left = ctk.CTkButton(btn_frame, text="⟲ Rotate Left", command=lambda: [rotate_image(90), rotation_count.__setitem__(0, rotation_count[0] - 1)])
        btn_rotate_left.pack(side="left", padx=5)

        btn_rotate_right = ctk.CTkButton(btn_frame, text="Rotate Right ⟳", command=lambda: [rotate_image(-90), rotation_count.__setitem__(0, rotation_count[0] + 1)])
        btn_rotate_right.pack(side="left", padx=5)

        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(660, 880))
        label = ctk.CTkLabel(full_window, image=ctk_img, text="")
        label.image = ctk_img
        label.pack()

    def split_all_pdfs(self):
        if not any(self.split_positions.values()):
            messagebox.showwarning("Warning", "No split points selected for any file!")
            return

        self.split_folder = filedialog.askdirectory(title="Select Folder to Save Split PDFs")
        if not self.split_folder:
            return

        for filename, doc in self.pdf_docs.items():
            positions = sorted(self.split_positions[filename])
            if not positions:
                continue

            original_name = os.path.splitext(filename)[0]
            total_pages = len(doc)
            start = 0

            for i, pos in enumerate(positions):
                from_page = start
                to_page = min(pos, total_pages - 1)

                # Tên file phản ánh đúng số trang (1-based)
                output_name = f"{original_name}_part{i + 1}_pages_{from_page + 1}-{to_page + 1}.pdf"
                output_path = os.path.join(self.split_folder, output_name)

                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=from_page, to_page=to_page)
                new_doc.save(output_path)
                new_doc.close()

                start = pos + 1

        messagebox.showinfo("Success", "All selected PDFs have been split!")
        self.split_folder_label.configure(text=self.split_folder)
        self.split_folder_frame.pack()

    def open_split_folder(self):
        if self.split_folder and os.path.exists(self.split_folder):
            os.startfile(self.split_folder)

    def update_window_title(self):
        total_splits = sum(len(s) for s in self.split_positions.values())
        self.root.title(f"PDF Splitter - {len(self.pdf_paths)} file(s), {total_splits} split points selected")

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1000x900")
    app = PDFSplitterApp(root)
    root.mainloop()
