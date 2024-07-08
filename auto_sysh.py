import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import win32com.client
import logging
from steamgrid import SteamGridDB
from PIL import Image
import requests
from io import BytesIO
from tkinter import messagebox
from tkinter.simpledialog import askstring

import sv_ttk

# Read values from config file
import configparser

config_file_path = 'config_sysh.ini'
def open_config_file():
    os.startfile(config_file_path)

# Check if the config file exists
if not os.path.exists(config_file_path):
    # If the config file doesn't exist, create it with default values
    with open(config_file_path, 'w') as configfile:
        configfile.write('[DEFAULT]\n')
        configfile.write('EmulatorDirectory=\n')
        configfile.write('SteamGridDBAPIKey=\n')
        configfile.write('GamesDirectory=\n')
        configfile.write('GamesDirectoryRecursive=0\n')
        configfile.write('SecondaryGamesDirectory=\n')
        configfile.write('SecondaryGamesDirectoryRecursive=0\n')
        configfile.write('ShortcutsDirectory=')

config = configparser.ConfigParser()
config.read(config_file_path)

emu_directory = config.get('DEFAULT', 'EmulatorDirectory', fallback=None)

def read_api_key_from_file():
    api_key = config.get('DEFAULT', 'SteamGridDBAPIKey', fallback=None)
    if not api_key:
        api_key = askstring('SteamGridDB API key', 'Enter your SteamGridDB API key')
        config.set('DEFAULT', 'SteamGridDBAPIKey', api_key)
        with open('config_sysh.ini', 'w') as configfile:
            config.write(configfile)

    if not api_key:
        messagebox.showerror(title="SteamGridDB API key not found.", message="Please add your SteamGridDB API key to the 'config_sysh.ini' file.")
        logging.error("SteamGridDB API key not found in config file.")
    return api_key

logging.basicConfig(filename='shortcuts.log', level=logging.INFO)

def create_shortcut(emulator_path, game_path, game_name, shortcuts_directory,api_key):
    print("Creating shortcut...")
    
    # Create a shortcut for the emulator .exe
    shortcut_name = game_name.split("[")[0].strip() + ".lnk"
    shortcut_path = os.path.join(shortcuts_directory, shortcut_name)

        # Create the shortcut with the required arguments
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.TargetPath = emulator_path
    shortcut.Arguments = f'-u 1 -f -g "{game_path}"'
    
    # Use the SteamGridDB API to get an icon for the game
    if not api_key:
        return
    sgdb = SteamGridDB(api_key)
    try:
        # Search for the game on SteamGridDB
        results = sgdb.search_game(game_name)
        
        if results:
            # Get the first result
            game = results[0]
            
            # Get the icon for the game
            icons = sgdb.get_icons_by_gameid([game.id])
            
            if icons:
                # Get the first icon
                icon = icons[0]
                
                # Get the URL of the icon image
                icon_image_url = icon.url
                
                if icon_image_url:
                    # Download the icon image
                    response = requests.get(icon_image_url)
                    image_data = response.content
                    
                    # Convert the image data to a PIL Image object
                    image = Image.open(BytesIO(image_data))
                    
                    # Get the selected icon size from the dropdown menu
                    icon_size_str = icon_size_var.get()
                    icon_size = int(icon_size_str.split("x")[0])
                    
                    # Resize the image to the selected size
                    image = image.resize((icon_size, icon_size))
                    
                    # Save the image as an ICO file in the games directory
                    games_directory = os.path.dirname(game_path)
                    icon_path = os.path.join(games_directory, game_name + ".ico")
                    image.save(icon_path)
                    
                    print(f"Icon saved: {icon_path}")
                    
                    # Set the icon for the shortcut
                    shortcut.IconLocation = icon_path
                    
                    print(f"Icon location: {shortcut.IconLocation}")
                    shortcut.save()

                    return shortcut_name;
    
    except Exception as e:
        messagebox.showerror(message=f"Error getting icon from SteamGridDB: {e}")
        logging.error(f"Error getting icon from SteamGridDB: {e}")
    
    if not shortcut.IconLocation:
        # If no icon was found on SteamGridDB, use the default emu icon
        shortcut.IconLocation = emulator_path
    
    shortcut.WorkingDirectory = os.path.dirname(game_path)
    shortcut.Save()
    print(f"Shortcut created: {shortcut_path}")
    logging.info(f"Shortcut created: {shortcut_path}")

def create_shortcuts_for_directory(emulator_path, games_directories, shortcuts_directory,api_key):
    if not api_key:
        return
    # Create a set to keep track of existing shortcuts in the specified directory
    existing_shortcuts = [os.path.basename(item) for item in list_files(shortcuts_directory, ['.lnk'],False)]
    
    # Create a shortcut for each game in the specified directories
    for games_directory in games_directories:
        for game_file in list_files(games_directory['dir'], ['.nsp', '.xci'], recursive=games_directory['recursive']):
            game_name = os.path.splitext(os.path.basename(game_file))[0]
            
            # Check if a shortcut already exists for this game
            if game_name in existing_shortcuts:
                continue
            
            shortcut=create_shortcut(emulator_path, game_file, game_name, shortcuts_directory,api_key)
            
            # Add the game name to the set of existing shortcuts
            existing_shortcuts.append(shortcut)
    messagebox.showinfo("Information","Shortcuts created")

def list_files(path, extensions, recursive=False):
    found_files = []
    if recursive:
        for root, dirs, files in os.walk(path):
            for file in files:
                if any(file.lower().endswith(ext.lower()) for ext in extensions):
                    found_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(path):
            if any(file.lower().endswith(ext.lower()) for ext in extensions):
                found_files.append(os.path.join(path, file))
    return found_files


def select_emulator_path():
    # Automatically set the emulator directory to the default location
    # default_emulator_dir = os.path.expanduser("~\\AppData\\Local\\suyu")
    # emulator_path = filedialog.askopenfilename(initialdir=default_emulator_dir, filetypes=[("Executable Files", "*.exe")])
    emulator_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
    
    # Validate that the selected file is a valid emulator executable
    if "suyu.exe" not in emulator_path and "sudachi.exe" not in emulator_path:
        messagebox.showerror(title="Invalid emulator executable.",message="Executable not found in folder")
        logging.error("Invalid emulator executable.")
        return
    
    # Save the selected directory to the config file
    config.set('DEFAULT', 'EmulatorDirectory', emulator_path)
    with open('config_sysh.ini', 'w') as configfile:
        config.write(configfile)
    
    emulator_entry.delete(0, tk.END)
    emulator_entry.insert(tk.END, emulator_path)

def select_games_directory():
    # Use askdirectory to allow the user to select a single directory
    games_directory = filedialog.askdirectory(title="Select Games Directory")
    
    # Save the selected games directory to the config file
    config.set('DEFAULT', 'GamesDirectory', games_directory)
    with open('config_sysh.ini', 'w') as configfile:
        config.write(configfile)
    
    # Clear the entry and insert the selected directory
    games_directory_entry.delete(0, tk.END)
    games_directory_entry.insert(tk.END, games_directory)

def select_games_directory_recursive():    
    config.set('DEFAULT', 'GamesDirectoryRecursive', str(subdirectories_var.get()))
    with open('config_sysh.ini', 'w') as configfile:
        config.write(configfile)
    
def select_games_directory_recursive_sec():    
    config.set('DEFAULT', 'SecondaryGamesDirectoryRecursive', str(subdirectories_var_sec.get()))
    with open('config_sysh.ini', 'w') as configfile:
        config.write(configfile)

def select_secondary_games_directory():
    # Use askdirectory to allow the user to select a single directory
    secondary_games_directory = filedialog.askdirectory(title="Select Secondary Games Directory (Optional)")
    
    # Save the selected secondary games directory to the config file
    config.set('DEFAULT', 'SecondaryGamesDirectory', secondary_games_directory)
    with open('config_sysh.ini', 'w') as configfile:
        config.write(configfile)
    
    # Clear the entry and insert the selected directory
    secondary_games_directory_entry.delete(0, tk.END)
    secondary_games_directory_entry.insert(tk.END, secondary_games_directory)

def select_shortcuts_directory():
    default_shortcuts_dir = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    shortcuts_directory = filedialog.askdirectory(initialdir=default_shortcuts_dir)
    
    # Save the selected shortcuts directory to the config file
    config.set('DEFAULT', 'ShortcutsDirectory', shortcuts_directory)
    with open('config_sysh.ini', 'w') as configfile:
        config.write(configfile)
    
    shortcuts_directory_entry.delete(0, tk.END)
    shortcuts_directory_entry.insert(tk.END, shortcuts_directory)

def create_shortcuts():
    emulator_path = emulator_entry.get()
    
    # Get the primary and secondary games directories from their respective entries
    primary_games_directory = games_directory_entry.get()
    
    secondary_games_directory = secondary_games_directory_entry.get()
    
    # Combine the primary and secondary directories into a list of directories
    games_directories = [{"dir":primary_games_directory,"recursive":subdirectories_var.get()==1}]
    
    if secondary_games_directory:
        games_directories.append({"dir":secondary_games_directory,"recursive":subdirectories_var_sec.get()==1})    
    
    shortcuts_directory = shortcuts_directory_entry.get()
    if not os.path.isfile(emulator_path) or not all(os.path.exists(games_directory['dir']) for games_directory in games_directories) or not os.path.exists(shortcuts_directory):
        messagebox.showerror(title="Invalid paths.",message="Check all directory condiguration")
        logging.error("Invalid paths.")
        return       
    create_shortcuts_for_directory(emulator_path, games_directories, shortcuts_directory,read_api_key_from_file())

window = tk.Tk()
window.title("Auto Shortcuts")
window.geometry("424x520")
window.resizable(False, False)

sv_ttk.set_theme("dark")


emulator_entry = tk.Entry(window,width=70)
if emu_directory:
    emulator_entry.insert(tk.END, emu_directory)
emulator_entry.grid(row=2, column=0, columnspan=4, pady=10)

emulator_button = ttk.Button(window,text="Select emulator exe",command = select_emulator_path,width=40)
emulator_button.grid(row=1, column=0, columnspan=4,pady=10)

subdirectories_var = tk.IntVar(value=config.getint('DEFAULT', 'GamesDirectoryRecursive', fallback=0))
subdirectories_checkbox = ttk.Checkbutton(window, text="Recursive?", variable=subdirectories_var, command=select_games_directory_recursive)
subdirectories_checkbox.grid(row=4, column=0, pady=10)

games_directory_entry=tk.Entry(window,width=50)
games_directory=config.get('DEFAULT','GamesDirectory',fallback=None)
if games_directory:
        games_directory_entry.insert(tk.END,games_directory)
games_directory_entry.grid(row=4,column=1,columnspan=3,pady=10)

games_directory_button=ttk.Button(window,text="Select Primary Games Directory",command=select_games_directory,width=40)
games_directory_button.grid(row=3,column=0,columnspan=4,pady=10)

subdirectories_var_sec = tk.IntVar(value=config.getint('DEFAULT', 'SecondaryGamesDirectoryRecursive', fallback=0))
subdirectories_checkbox_sec = ttk.Checkbutton(window, text="Recursive?", variable=subdirectories_var_sec, command=select_games_directory_recursive_sec)
subdirectories_checkbox_sec.grid(row=6, column=0, pady=10)

secondary_games_directory_entry=tk.Entry(window,width=50)
secondary_games_directory=config.get('DEFAULT','SecondaryGamesDirectory',fallback=None)
if secondary_games_directory:
    secondary_games_directory_entry.insert(tk.END,secondary_games_directory)
secondary_games_directory_entry.grid(row=6,column=1,columnspan=3,pady=10)

secondary_games_directory_button=ttk.Button(window,text="Select Secondary Games Directory (Optional)",command=select_secondary_games_directory,width=40)
secondary_games_directory_button.grid(row=5,column=0,columnspan=4,pady=10)

shortcuts_directory_entry=tk.Entry(window,width=50)
shortcuts_directory=config.get('DEFAULT','ShortcutsDirectory',fallback=None)
if shortcuts_directory:
    shortcuts_directory_entry.insert(tk.END,shortcuts_directory)
shortcuts_directory_entry.grid(row=8,column=0,columnspan=4,pady=10)

shortcuts_directory_button=ttk.Button(window,text="Select Shortcuts Directory",command = select_shortcuts_directory,width=40)
shortcuts_directory_button.grid(row=7,column=0,columnspan=4,pady=10)

icon_size_label=ttk.Label(window,text="Icon Size:")
icon_size_label.grid(row=10,column=1,columnspan=3,pady=10)

icon_size_var=tk.StringVar(window)
icon_size_var.set("64x64")

icon_size_dropdown=tk.OptionMenu(window,icon_size_var,"64x64","32x32","64x64","128x128","256x256")
icon_size_dropdown.grid(row=10,column=3,columnspan=1,pady=10)

open_config_button=tk.Button(window,text="Open Config File",command=open_config_file,width=20)
open_config_button.grid(row=10,column=0,columnspan=3,pady=10)

create_button=ttk.Button(window,text="Create Shortcuts",command=create_shortcuts,width=40)
create_button.grid(row=11,columnspan=4,pady=10)

window.mainloop()
