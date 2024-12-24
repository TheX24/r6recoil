import tkinter as tk
from tkinter import ttk
import threading
import time
import ctypes
from pynput import keyboard, mouse
import os

# Define global variables
primary_weapon = True
mouse_speed = 1
sleep_duration = 0.012  # Default sleep duration
active = False
both_buttons_held = False
listener_active = False
listener_thread = None
keyboard_listener = None
mouse_listener = None
pressed_buttons = set()
moving = False  # Flag to track moving state
use_custom_speed = False  # Flag to use custom speed
custom_speed = 1  # Custom speed value

# Define constants for mouse input
MOUSEEVENTF_MOVE = 0x0001

# Function to update mouse speed from GUI
def set_speed(name, speed):
    global mouse_speed
    mouse_speed = int(speed)  # Ensure mouse_speed is an integer
    print(f"Selected speed: {name} ({mouse_speed} pixels per 7 ms)")

# Function to update sleep duration from GUI
def set_sleep_duration(duration):
    global sleep_duration
    sleep_duration = float(duration)  # Ensure sleep_duration is a float
    print(f"Set sleep duration to: {sleep_duration} seconds")

# Function to toggle the program activation state
def on_press(key):
    global active, listener_active
    try:
        if listen_keys_var.get():  # Check if the checkbox is checked
            if key.char == '1':
                if not listener_active:
                    start_mouse_movement()
            elif key.char == '2':
                if listener_active:
                    stop_mouse_movement()
    except AttributeError:
        if key == keyboard.Key.caps_lock:
            active = not active
            print("Active" if active else "Inactive")

def on_click(x, y, button, pressed):
    global both_buttons_held, moving
    if pressed:
        pressed_buttons.add(button)
    else:
        pressed_buttons.discard(button)
    
    if mouse.Button.left in pressed_buttons and mouse.Button.right in pressed_buttons:
        if not both_buttons_held:
            both_buttons_held = True
            print("Both buttons held")
            start_moving()
    else:
        if both_buttons_held:
            both_buttons_held = False
            moving = False
            print("Stopped moving mouse")

def start_moving():
    global moving
    def move_mouse():
        global moving
        if not moving:
            print("Started moving mouse")
            moving = True
        while both_buttons_held and active and listener_active:
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, 0, mouse_speed, 0, 0)
            time.sleep(sleep_duration)
        if moving:
            print("Stopped moving mouse")
            moving = False
    threading.Thread(target=move_mouse).start()

def is_caps_lock_on():
    return ctypes.windll.user32.GetKeyState(0x14) & 1

# Function to read speed options from a text file
def read_speed_options(file_name):
    speed_options = {}
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(file_path, 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.strip().split('=')
                speed_options[key.strip()] = int(value.strip())
    return speed_options

# Create the GUI
root = tk.Tk()
root.title("EZ Recoil")
root.geometry("410x150")  # Set the window size

# Set the theme for ttk widgets
style = ttk.Style(root)
style.theme_use('winnative')

# Create a frame for padding
frame = ttk.Frame(root, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

# Create a label for speed selection
speed_label = ttk.Label(frame, text="Select Weapon:")
speed_label.grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)

# Read speed options from the text file
speed_options = read_speed_options('speed_options.txt')

# Create a dropdown menu for speed selection
speed_var = tk.StringVar(root)
speed_var.set(next(iter(speed_options)))  # Default value

def on_speed_change(event):
    selected_speed = speed_var.get()
    if not use_custom_speed:
        set_speed(selected_speed, speed_options[selected_speed])

speed_menu = ttk.Combobox(frame, textvariable=speed_var, values=list(speed_options.keys()), height=5)
speed_menu.bind("<<ComboboxSelected>>", on_speed_change)
speed_menu.grid(row=0, column=1, padx=5, pady=10, sticky=tk.W)

# Create a checkbox and number input for custom speed
custom_speed_var = tk.IntVar()

def toggle_custom_speed():
    global use_custom_speed
    use_custom_speed = custom_speed_var.get()
    if use_custom_speed:
        set_speed("Custom", custom_speed)
    else:
        on_speed_change(None)

custom_speed_check = ttk.Checkbutton(frame, text="Use Custom Speed", variable=custom_speed_var, command=toggle_custom_speed)
custom_speed_check.grid(row=1, column=0, padx=5, pady=10, sticky=tk.W)

def update_custom_speed(*args):
    global custom_speed
    try:
        custom_speed = int(custom_speed_entry.get())  # Convert to integer
        if use_custom_speed:
            set_speed("Custom", custom_speed)
    except ValueError:
        pass  # Ignore invalid input

custom_speed_entry = ttk.Entry(frame)
custom_speed_entry.insert(0, "1")
custom_speed_entry.grid(row=1, column=1, padx=5, pady=10, sticky=tk.W)
custom_speed_entry.bind("<KeyRelease>", update_custom_speed)

# Create a label and entry for sleep duration
sleep_duration_label = ttk.Label(frame, text="Set Interval (seconds):")
sleep_duration_label.grid(row=2, column=0, padx=5, pady=10, sticky=tk.W)

sleep_duration_entry = ttk.Entry(frame)
sleep_duration_entry.insert(0, str(sleep_duration))
sleep_duration_entry.grid(row=2, column=1, padx=5, pady=10, sticky=tk.W)

def update_sleep_duration(*args):
    try:
        set_sleep_duration(sleep_duration_entry.get())
    except ValueError:
        pass  # Ignore invalid input

sleep_duration_entry.bind("<KeyRelease>", update_sleep_duration)

# Function to toggle the "always on top" attribute
def toggle_always_on_top():
    root.attributes("-topmost", always_on_top_var.get())

# Create a checkbox for "always on top"
always_on_top_var = tk.IntVar()
always_on_top_check = ttk.Checkbutton(frame, text="Always on Top", variable=always_on_top_var, command=toggle_always_on_top)
always_on_top_check.grid(row=0, column=2, padx=5, pady=10, sticky=tk.W)

# Create a checkbox to toggle listening for key.char == '1' and key.char == '2'
listen_keys_var = tk.IntVar()
listen_keys_check = ttk.Checkbutton(frame, text="Turn on SWD", variable=listen_keys_var)
listen_keys_check.grid(row=1, column=2, padx=5, pady=10, sticky=tk.W)

# Function to start mouse movement
def start_mouse_movement():
    global listener_active, active
    active = is_caps_lock_on()  # Check Caps Lock state when starting
    listener_active = True
    toggle_button.config(text="Stop")
    print("Mouse movement started")

# Function to stop mouse movement
def stop_mouse_movement():
    global listener_active, active
    listener_active = False
    active = False  # Reset active state
    toggle_button.config(text="Start")
    print("Mouse movement stopped")

# Create a start/stop button to toggle the program
def toggle_program():
    global listener_thread, keyboard_listener, mouse_listener
    if listener_active:
        stop_mouse_movement()
    else:
        start_mouse_movement()
        listener_thread = threading.Thread(target=run_listener)
        listener_thread.start()

def run_listener():
    global keyboard_listener, mouse_listener
    # Collect events until released
    with keyboard.Listener(on_press=on_press) as k_listener, mouse.Listener(on_click=on_click) as m_listener:
        keyboard_listener = k_listener
        mouse_listener = m_listener
        k_listener.join()
        m_listener.join()

toggle_button = ttk.Button(frame, text="Start", command=toggle_program)
toggle_button.grid(row=2, column=2, columnspan=4, padx=5, pady=10, sticky=tk.W)

# Run the GUI loop
root.mainloop()