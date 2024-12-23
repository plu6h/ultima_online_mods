# PSD TO PNG BATCH EXPORTER
# for each PSD name with a hexadecimal suffix, save a PNG copy named by HEX for GumpOverrides. example =
# Mod group visualization and export UI for selection by folder paths
import os  # folders filepaths
import tkinter as tk  # UI
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
from psd_tools import PSDImage  # exporting flattened PSD images
import re  # regex regular expression string parsing

# //==================================================================================================
DEFAULT_OUTPUT_PATH = "./GumpOverrides/"  # create a new local GumpOverrides folder for exporting to, to be copied into the Outlands Folder.

# Mod Group and Source Art (PSDs) filepath
GROUPS_LEFT = {
    "Magic Spells": {
        "image": ".././UI/UI_MagicSpells/ui_spell_00_comp_nospace_wide.png",
        "subgroups": {
            "Magic Spells": {"path": ".././UI/UI_MagicSpells", "thumbnail": "None", "default_state": True},
            "Magic Effect": {"path": ".././UI/UI_MagicSpells/SpellEffects_Color", "thumbnail": "None", "default_state": True}
        }
    },
    "Necromancy & Chivalry": {
        "image": ".././UI/UI_SpellsChivalry/ui_chiv_00_render_wide_combined.jpg",
        "subgroups": {
            "Chivalry": {"path": ".././UI/UI_SpellsChivalry", "thumbnail": "None", "default_state": True},
            "Necromancy": {"path": ".././UI/UI_SpellsNecromancy", "thumbnail": "None", "default_state": True}
        }
    },
    "Buffs": {
        "image": ".././UI/UI_Buffs/ui_buff_00_comp_names_wide.jpg",
        "subgroups": {
            "Buffs": {"path": ".././UI/UI_Buffs", "thumbnail": "None", "default_state": True}
        }
    },
    "Eldritch Spells": {
        "image": ".././UI/UI_MagicSpells_Eldritch/ui_spell_comp_eldritch_magic.jpg",
        "subgroups": {
            "Eldritch Magic": {"path": ".././UI/UI_MagicSpells_Eldritch", "thumbnail": "None", "default_state": False}
        }
    }
}

GROUPS_RIGHT = {
    "ArchStone & Backpack": {
        "image": ".././UI/UI_ArchStone/ui_archstone_backpack_comp.jpg",
        "subgroups": {
            "ArchStone": {"path": ".././UI/UI_ArchStone", "thumbnail": "None", "default_state": False},
            "Backpack": {"path": ".././UI/UI_BackPack", "thumbnail": "None", "default_state": True},
            "BackpackStrapless": {"path": ".././UI/UI_BackPackStrapless", "thumbnail": "None", "default_state": False}
        }
    },
    "Dark UI": {
        "image": ".././UI/UI_DarkScrolls/00_dark_scrolls_comp_wide.jpg",
        "subgroups": {
            "Dark Stats": {"path": ".././UI/UI_DarkStats", "thumbnail": "None", "default_state": True},
            "Dark Scrolls": {"path": ".././UI/UI_DarkScrolls", "thumbnail": "None", "default_state": True}
        }
    },
    "Light UI": {
        "image": ".././UI/UI_LightScrolls/00_dark_scrolls_comp_wide_light.jpg",
        "subgroups": {
            "Light Stats": {"path": ".././UI/UI_LightStats", "thumbnail": "None", "default_state": False},
            "Light Scrolls": {"path": ".././UI/UI_LightScrolls", "thumbnail": "None", "default_state": False}
        }
    },
    "Dark UI2": {
        "image": ".././UI/UI_DarkBook/00_ui_dark_book_comp.png",
        "subgroups": {
            "Dark Book": {"path": ".././UI/UI_DarkBook", "thumbnail": "None", "default_state": True}
        }
    },
    "Dark UI3": {
        "image": ".././UI/UI_DarkFrame/00_ui_dark_frame_comp.png",
        "subgroups": {
            "Dark UI": {"path": ".././UI/UI_DarkFrame", "thumbnail": "None", "default_state": True}
        }
    },
    "ArchStoneMulti ": {
        "image": ".././UI/UI_ArchStone_Multi/00_ui_archstone_multi_equipslots_comp.png",
        "subgroups": {
            "ArchStone Multi": {"path": ".././UI/UI_ArchStone_Multi", "thumbnail": "None", "default_state": True},
            "Equip Slots": {"path": ".././UI/UI_EquipSlots", "thumbnail": "None", "default_state": True}
        }
    },
    "Profession": {
        "image": ".././UI/UI_ProfessionCodex/00_ui_profession_codex_comp.png",
        "subgroups": {
            "Codex": {"path": ".././UI/UI_ProfessionCodex", "thumbnail": "None", "default_state": True}
        }
    }
}

# In development upscaled 512 images are auto-scaled back to 44 pixels on export (spell icon default size)
GROUPS_UPSCALE = {
    "Magic Spells Upscaled": {
        "image": "None",
        "subgroups": {
            "DEV Magic Spells": {"path": ".././UI/UI_MagicSpells/Upscale", "thumbnail": "None", "default_state": False},
            "DEV Magic Effect": {"path": ".././UI/UI_MagicSpells/Upscale/SpellEffects_Color", "thumbnail": "None", "default_state": False}
        }
    },
    "Necromancy & Chivalry": {
        "image": "None",
        "subgroups": {
            "DEV Chivalry": {"path": ".././UI/UI_SpellsChivalry/Upscale", "thumbnail": "None", "default_state": False},
            "DEV Necromancy": {"path": ".././UI/UI_SpellsNecromancy/Upscale", "thumbnail": "None", "default_state": False}
        }
    }
}

DESCALE_PIXEL_SIZE = 44  # 44-pixel spells icon, original
CHECKBOX_ON_IMAGE_PATH = "./images/checkbox_on_image.png"
CHECKBOX_OFF_IMAGE_PATH = "./images/checkbox_off_image.png"
REGEX_HEXIDECIMAL = re.compile(r'(0x[0-9A-Fa-f]+)\.psd$')  # find hexadecimal suffix on a PSD file, example = "ui_necro_spell_1_0x500E.psd" finds "0x500E"
UI_IMAGE_WIDTH = 660
UI_IMAGE_HEIGHT = 300

# //==================================================================================================
# // EXPORT from PSD folder to PNG then rename to hexadecimal suffix
def export_psd_to_PNG(folder_path, target_folder, override_existing_files, resize=None):

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    psd_files = [f for f in os.listdir(folder_path) if REGEX_HEXIDECIMAL.search(f)]

    for filename in psd_files:
        match = REGEX_HEXIDECIMAL.search(filename)
        if match:
            psd_path = os.path.join(folder_path, filename)
            PNG_filename = match.group(1) + ".png"
            PNG_path = os.path.join(target_folder, PNG_filename)

            if os.path.exists(PNG_path) and not override_existing_files:
                continue

            try:
                psd = PSDImage.open(psd_path)
                merged_image = psd.composite()
                if resize:
                    merged_image = merged_image.resize((resize, resize), Image.Resampling.LANCZOS)
                merged_image.save(PNG_path, format='PNG')
            except Exception as e:
                print(f"Error processing {psd_path}: {e}")

    print(f"Exported all PSD files from {folder_path} to PNG format.")

# //==================================================================================================
# // CHECKBOX image toggle
class ImageCheckbox(tk.Frame):
    def __init__(self, master, text, variable, on_image_path, off_image_path, **kwargs):
        super().__init__(master, bg='#3c3c3c', **kwargs)

        self.variable = variable
        self.on_image = ImageTk.PhotoImage(Image.open(on_image_path))
        self.off_image = ImageTk.PhotoImage(Image.open(off_image_path))

        self.checkbox_image = tk.Label(self, bg='#3c3c3c')
        self.checkbox_image.pack(side=tk.LEFT)
        self.checkbox_image.bind("<Button-1>", self.toggle)

        self.label = tk.Label(self, text=text, bg='#222222', fg='white')
        self.label.pack(side=tk.LEFT)
        self.label.bind("<Button-1>", self.toggle)

        self.variable.trace("w", self.update_image)
        self.update_image()

    def toggle(self, event=None):
        self.variable.set(not self.variable.get())

    def update_image(self, *args):
        if self.variable.get():
            self.checkbox_image.config(image=self.on_image)
        else:
            self.checkbox_image.config(image=self.off_image)

# //==================================================================================================
# // UI
class PSDtoPNGConverter:
    def __init__(self, master):
        self.master = master
        self.master.title("PSD to PNG Converter - Source Art to GumpOverrides")
        self.master.configure(bg='#111111')
        self.target_folder = DEFAULT_OUTPUT_PATH  # default is local gump overrides
        self.export_states = []  # group is currently checked on or off for export
        self.checkbox_states = {}  # the default setting on off for each group
        self.paths = []  # source art paths
        self.group_names = []  # group names
        self.setup_ui()

    def setup_ui(self):
        print("Setting up UI...")
        self.frame = ttk.Frame(self.master, style='TFrame')
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.export_all_button = ttk.Button(self.frame, text="Export All", command=self.export_all_groups, style='Large.TButton')
        self.export_all_button.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky='ew')

        self.export_all_to_same_folder = tk.BooleanVar(value=True)
        self.export_all_checkbox = ImageCheckbox(self.frame, text="Export all to target folder", variable=self.export_all_to_same_folder, on_image_path=CHECKBOX_ON_IMAGE_PATH, off_image_path=CHECKBOX_OFF_IMAGE_PATH)
        self.export_all_checkbox.grid(row=1, column=0, pady=(0, 10), sticky='e')

        self.target_folder_entry = ttk.Entry(self.frame, width=30, style='Large.TEntry')
        self.target_folder_entry.insert(0, self.target_folder)
        self.target_folder_entry.grid(row=1, column=1, pady=(0, 10))

        self.override_existing_files = tk.BooleanVar(value=True)
        self.override_checkbox = ImageCheckbox(self.frame, text="Override existing PNG files", variable=self.override_existing_files, on_image_path=CHECKBOX_ON_IMAGE_PATH, off_image_path=CHECKBOX_OFF_IMAGE_PATH)
        self.override_checkbox.grid(row=1, column=2, pady=(0, 10), sticky='w')

        # Create a Canvas for scrollable area
        self.canvas = tk.Canvas(self.frame, bg='#111111')
        self.canvas.grid(row=2, column=0, columnspan=3, sticky='nsew', pady=(10, 0))

        # Add a vertical scrollbar to the canvas
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=2, column=3, sticky='ns', pady=(10, 0))

        # Configure the canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas
        self.groups_frame = ttk.Frame(self.canvas, style='TFrame')
        self.canvas.create_window((0, 0), window=self.groups_frame, anchor='nw')

        # Bind the frame's size to the canvas scroll region
        self.groups_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Now create the left_area and right_area inside self.groups_frame
        self.left_area = ttk.Frame(self.groups_frame, style='TFrame')
        self.right_area = ttk.Frame(self.groups_frame, style='TFrame')

        self.left_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.right_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.load_groups(self.left_area, GROUPS_LEFT)
        self.load_groups(self.right_area, GROUPS_RIGHT)
        #self.load_groups(self.groups_frame, GROUPS_UPSCALE)
        # self.load_groups(self.groups_frame, GROUPS_DEV)  # Uncomment if GROUPS_DEV exists
        print("Groups loaded.")

        # The add_path_area may remain outside the scrollable area if desired
        self.add_path_area = ttk.Frame(self.frame, style='TFrame', borderwidth=2, relief="groove")
        self.add_path_area.grid(row=3, column=0, columnspan=3, sticky='ew', pady=(10, 0))

        self.add_path_button = ttk.Button(self.add_path_area, text="Add Path", command=self.add_path, style='Large.TButton')
        self.add_path_button.pack(pady=(10, 10), fill=tk.X)

    def load_groups(self, parent, groups):
        print(f"Loading groups into {parent}...")
        for group_name, group_info in groups.items():
            print(f"Adding group section: {group_name}")
            self.add_group_section(parent, group_name, group_info)

    def add_group_section(self, parent, group_name, group_info):
        print(f"Adding group section for {group_name}...")
        section_frame = ttk.Frame(parent, style='TFrame', borderwidth=2, relief="groove")
        section_frame.pack(fill=tk.X, padx=5, pady=5)

        image_path = group_info["image"]
        if image_path and os.path.exists(image_path):
            print(f"Loading image for {group_name}: {image_path}")
            img = Image.open(image_path)
            img.thumbnail((UI_IMAGE_WIDTH, UI_IMAGE_HEIGHT), Image.Resampling.LANCZOS)
            section_image = ImageTk.PhotoImage(img)
            image_label = ttk.Label(section_frame, image=section_image)
            image_label.image = section_image
            image_label.pack()

        subgroups_frame = ttk.Frame(section_frame, style='TFrame')
        subgroups_frame.pack()

        for subgroup_name, subgroup_info in group_info["subgroups"].items():
            self.add_subgroup_entry(subgroups_frame, subgroup_name, subgroup_info)

    def add_subgroup_entry(self, parent, subgroup_name, subgroup_info):
        print(f"Adding subgroup entry for {subgroup_name}...")
        subgroup_frame = ttk.Frame(parent, style='TFrame')
        subgroup_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        default_state = subgroup_info.get("default_state", True)
        state = tk.BooleanVar(value=default_state)
        self.export_states.append(state)
        self.checkbox_states[(subgroup_info["path"])] = state

        export_check = ImageCheckbox(subgroup_frame, text="", variable=state, on_image_path=CHECKBOX_ON_IMAGE_PATH, off_image_path=CHECKBOX_OFF_IMAGE_PATH)
        export_check.grid(row=0, column=0, padx=(0, 10))

        subgroup_label = ttk.Label(subgroup_frame, text=subgroup_name, style='TLabel')
        subgroup_label.grid(row=0, column=1, padx=(0, 10))

        export_button = ttk.Button(subgroup_frame, text="Export", command=lambda p=subgroup_info["path"], s=state, r=DESCALE_PIXEL_SIZE if "Upscale" in subgroup_name else None: self.export_group(p, s, r), style='Large.TButton')
        export_button.grid(row=0, column=3, padx=(0, 10))

    def add_path(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            group_name = os.path.basename(folder_path)
            self.paths.append(folder_path)
            self.group_names.append(group_name)
            self.export_states.append(tk.BooleanVar(value=True))
            self.update_dynamic_paths()

    def update_dynamic_paths(self):
        for widget in self.dynamic_paths_area.winfo_children():
            if widget != self.add_path_button:
                widget.destroy()

        for path, group_name, state in zip(self.paths, self.group_names, self.export_states):
            dynamic_path_frame = ttk.Frame(self.dynamic_paths_area, style='TFrame')
            dynamic_path_frame.pack(fill=tk.X, padx=5, pady=5)

            export_check = ImageCheckbox(dynamic_path_frame, text="", variable=state, on_image_path=CHECKBOX_ON_IMAGE_PATH, off_image_path=CHECKBOX_OFF_IMAGE_PATH)
            export_check.grid(row=0, column=0, padx=(0, 10))

            group_label = ttk.Label(dynamic_path_frame, text=group_name, style='TLabel')
            group_label.grid(row=0, column=1, padx=(0, 10))

            export_button = ttk.Button(dynamic_path_frame, text="Export", command=lambda p=path, s=state: self.export_group(p, s), style='TButton')
            export_button.grid(row=0, column=3, padx=(0, 10))

    def export_group(self, folder_path, state, resize=None):
        if state.get():
            # Check if the folder_path contains 'Upscale' and set the resize value accordingly
            if "Upscale" in folder_path:
                resize = DESCALE_PIXEL_SIZE
            export_psd_to_PNG(folder_path, self.target_folder if self.export_all_to_same_folder.get() else folder_path, self.override_existing_files.get(), resize)

    def export_all_groups(self):
        """Export all entries that have their checkbox state currently ON """
        for path, state_var in self.checkbox_states.items():
            if state_var.get():
                resize = DESCALE_PIXEL_SIZE if "Upscale" in path else None
                self.export_group(path, state_var, resize)

    def set_upscale_size(self):
        # UI input for 44 pixels spell icons
        try:
            global DESCALE_PIXEL_SIZE
            DESCALE_PIXEL_SIZE = int(self.upscale_export_size_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer for export size.")

# //==================================================================================================
# // MAIN UI
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1400x830")  # 14x8 aspect ratio

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TFrame', background='#111111', bordercolor='#000000', borderwidth=0)
    style.configure('Large.TButton', background='#3c3c3c', foreground='white', borderwidth=0, font=('Helvetica', 12), bordercolor='#000000')
    style.configure('Large.TCheckbutton', background='#111111', foreground='white', font=('Helvetica', 12), bordercolor='#000000', borderwidth=0)
    style.configure('TLabel', background='#000000', foreground='white', font=('Helvetica', 12), bordercolor='#000000', borderwidth=0)
    style.configure('DarkGrey.TLabel', background='#000000', foreground='grey', font=('Helvetica', 12), bordercolor='#000000', borderwidth=0)
    style.configure('TEntry', fieldbackground='#3c3c3c', foreground='gray', font=('Helvetica', 12), bordercolor='#000000', borderwidth=0)
    style.configure('Large.TEntry', fieldbackground='#000000', foreground='white', font=('Helvetica', 16), bordercolor='#000000', borderwidth=0)

    app = PSDtoPNGConverter(root)
    print("start")
    root.mainloop()

# //==================================================================================================
# // TODO
# The groups and filepath sections should all be stored to a JSON file so that any custom added path/groups are loaded the next time.
# Make all the borders of the sections dark grey
