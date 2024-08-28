import os
import shutil
import json
import customtkinter as ctk
from collections import defaultdict
from tkinter import filedialog, messagebox
from customtkinter import CTkImage
from PIL import Image

def merge_json(file1, file2):
    with open(file1, 'r') as f:
        data1 = json.load(f)
    with open(file2, 'r') as f:
        data2 = json.load(f)

    if isinstance(data1, list) and isinstance(data2, list):
        return data1 + data2
    elif isinstance(data1, dict) and isinstance(data2, dict):
        merged = data1.copy()
        for key, value in data2.items():
            if key in merged:
                if isinstance(merged[key], list) and isinstance(value, list):
                    merged[key] = merged[key] + value
                elif isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key].update(value)
                else:
                    merged[key] = value
            else:
                merged[key] = value
        return merged
    else:
        return data2
def merging_log(self, log: str):
    self.result_text.insert(ctk.END, f"{log}\n")
def merge_datapacks(input_dir, output_dir, datapack_name, pack_format, description, selected_pack_png, self):
    merging_log(self, f"Merging datapacks from {input_dir}")
    merged_datapack_dir = os.path.join(output_dir, datapack_name)
    os.makedirs(merged_datapack_dir, exist_ok=True)
    merged_data_dir = os.path.join(merged_datapack_dir, 'data')
    os.makedirs(merged_data_dir, exist_ok=True)

    namespace_files = defaultdict(lambda: defaultdict(list))

    for datapack_dir in os.listdir(input_dir):
        merging_log(self, f"Merging '{datapack_dir}'")
        datapack_path = os.path.join(input_dir, datapack_dir)
        if os.path.isdir(datapack_path) and os.path.exists(os.path.join(datapack_path, 'pack.mcmeta')):
            data_dir = os.path.join(datapack_path, 'data')
            if os.path.exists(data_dir):
                for namespace in os.listdir(data_dir):
                    namespace_path = os.path.join(data_dir, namespace)
                    for root, _, files in os.walk(namespace_path):
                        for file in files:
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(full_path, namespace_path)
                            namespace_files[namespace][rel_path].append(full_path)

    for namespace, files in namespace_files.items():
        for rel_path, file_versions in files.items():
            dst_dir = os.path.join(merged_data_dir, namespace, os.path.dirname(rel_path))
            os.makedirs(dst_dir, exist_ok=True)
            dst_file = os.path.join(dst_dir, os.path.basename(rel_path))

            if len(file_versions) == 1:
                shutil.copy2(file_versions[0], dst_file)
            else:
                if rel_path.endswith('.json'):
                    merged_data = {}
                    for file in file_versions:
                        merged_data = merge_json(file, dst_file) if os.path.exists(dst_file) else json.load(open(file))
                        with open(dst_file, 'w') as f:
                            json.dump(merged_data, f, indent=2)
                else:
                    shutil.copy2(file_versions[-1], dst_file)

    pack_mcmeta = {
        "pack": {
            "pack_format": pack_format,
            "description": description
        }
    }
    
    with open(os.path.join(merged_datapack_dir, 'pack.mcmeta'), 'w') as f:
        json.dump(pack_mcmeta, f, indent=4)

    if selected_pack_png:
        shutil.copy2(selected_pack_png, os.path.join(merged_datapack_dir, 'pack.png'))

    return f"'{datapack_name}' successfully merged in {output_dir}!"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Datapack Merger")
        self.geometry("800x600")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(8, weight=1)

        self.input_dir = ctk.StringVar()
        self.output_dir = ctk.StringVar()
        self.datapack_name = ctk.StringVar(value="Merged Datapack")
        self.pack_format = ctk.IntVar(value=48)
        self.description = ctk.StringVar(value="blah blah blah")
        self.pack_png_options = []
        self.selected_pack_png = ctk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        padding = {'padx': (10, 5), 'pady': 5}
        ctk.CTkLabel(self, text="Made by RealVaprant.").grid(row=8, column=0, sticky="w", **padding)
        ctk.CTkLabel(self, text="Input Directory:").grid(row=0, column=0, sticky="w", **padding)
        ctk.CTkEntry(self, textvariable=self.input_dir).grid(row=0, column=1, sticky="ew", **padding)
        ctk.CTkButton(self, text="Browse", command=self.browse_input).grid(row=0, column=2, **padding)

        ctk.CTkLabel(self, text="Output Directory:").grid(row=1, column=0, sticky="w", **padding)
        ctk.CTkEntry(self, textvariable=self.output_dir).grid(row=1, column=1, sticky="ew", **padding)
        ctk.CTkButton(self, text="Browse", command=self.browse_output).grid(row=1, column=2, **padding)

        ctk.CTkLabel(self, text="Datapack Name:").grid(row=2, column=0, sticky="w", **padding)
        ctk.CTkEntry(self, textvariable=self.datapack_name).grid(row=2, column=1, columnspan=2, sticky="ew", **padding)

        ctk.CTkLabel(self, text="Pack Format:").grid(row=3, column=0, sticky="w", **padding)
        ctk.CTkEntry(self, textvariable=self.pack_format).grid(row=3, column=1, columnspan=2, sticky="ew", **padding)

        ctk.CTkLabel(self, text="Description:").grid(row=4, column=0, sticky="w", **padding)
        ctk.CTkEntry(self, textvariable=self.description).grid(row=4, column=1, columnspan=2, sticky="ew", **padding)

        ctk.CTkLabel(self, text="Pack Image:").grid(row=5, column=0, sticky="w", **padding)
        self.pack_image_frame = ctk.CTkScrollableFrame(self, height=200)
        self.pack_image_frame.grid(row=5, column=0, columnspan=3, sticky="ew", **padding)

        ctk.CTkButton(self, text="Merge Datapacks", command=self.merge).grid(row=6, column=0, columnspan=3, sticky="ew", **padding)

        self.result_text = ctk.CTkTextbox(self, height=100)
        self.result_text.grid(row=7, column=0, columnspan=3, sticky="nsew", **padding)

    def browse_input(self):
        self.input_dir.set(filedialog.askdirectory())
        self.update_pack_png_options()

    def browse_output(self):
        self.output_dir.set(filedialog.askdirectory())

    def update_pack_png_options(self):
        for widget in self.pack_image_frame.winfo_children():
            widget.destroy()

        self.pack_png_options = ["None"]
        input_dir = self.input_dir.get()
        if input_dir:
            for datapack_dir in os.listdir(input_dir):
                datapack_path = os.path.join(input_dir, datapack_dir)
                pack_png_path = os.path.join(datapack_path, 'pack.png')
                if os.path.isfile(pack_png_path):
                    self.pack_png_options.append(pack_png_path)

        self.create_image_grid()

    def create_image_grid(self):
        thumbnail_size = (100, 100)  # Set your desired thumbnail size here

        for i, pack_png in enumerate(self.pack_png_options):
            frame = ctk.CTkFrame(self.pack_image_frame)
            frame.grid(row=i // 7, column=i % 7, padx=5, pady=5)

            if pack_png == "None":
                label = ctk.CTkLabel(frame, text="No Image", width=thumbnail_size[0], height=thumbnail_size[1])
                label.pack()
            else:
                image = Image.open(pack_png)
                image.thumbnail(thumbnail_size)  # This resizes the image in place
                ctk_image = CTkImage(image, size=thumbnail_size)  # Pass the size explicitly to CTkImage
                label = ctk.CTkLabel(frame, image=ctk_image, text="", width=thumbnail_size[0], height=thumbnail_size[1])
                label.image = ctk_image  # Keep a reference to avoid garbage collection
                label.pack()

            button_text = "Selected" if pack_png == self.selected_pack_png.get() else "Select"
            button = ctk.CTkButton(frame, text=button_text,
                                command=lambda png=pack_png: self.select_pack_png(png),
                                width=60)
            button.pack(pady=2)

            if pack_png == self.selected_pack_png.get():
                frame.configure(border_color="teal", border_width=10)



    def select_pack_png(self, pack_png):
        self.selected_pack_png.set(pack_png)
        self.update_pack_png_options()


    def merge(self):
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()
        datapack_name = self.datapack_name.get()
        pack_format = self.pack_format.get()
        description = self.description.get()
        selected_pack_png = self.selected_pack_png.get()

        if not input_dir or not output_dir or not datapack_name:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        selected_pack_png = None if selected_pack_png == "None" else selected_pack_png

        try:
            result = merge_datapacks(input_dir, output_dir, datapack_name, pack_format, description, selected_pack_png, self)
            self.result_text.insert(ctk.END, result)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
