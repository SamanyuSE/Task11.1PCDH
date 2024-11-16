import socket
import gpiod
import time
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from threading import Thread

# Setup for relay control
CHIP_NAME = "gpiochip0"
RELAY_PIN_A = 17  # GPIO pin for Plant A relay
RELAY_PIN_B = 27  # GPIO pin for Plant B relay

# Thresholds for each plant
THRESHOLD_A = 500  # Threshold for Plant A
THRESHOLD_B = 600  # Threshold for Plant B

# UDP settings
LOCAL_IP = "0.0.0.0"  # Listen on all interfaces
LOCAL_PORT = 8888

# Data buffers for graphs
short_term_data_a = []
short_term_data_b = []
long_term_data_a = []
long_term_data_b = []

# Function to control pumps
def control_pumps(chip, line_a, line_b, moisture_a, moisture_b):
    if moisture_a < THRESHOLD_A:
        line_a.set_value(0)
        print("Pump A ON: Moisture below threshold.")
    else:
        line_a.set_value(1)
        print("Pump A OFF: Moisture above threshold.")

    if moisture_b < THRESHOLD_B:
        line_b.set_value(0)
        print("Pump B ON: Moisture below threshold.")
    else:
        line_b.set_value(1)
        print("Pump B OFF: Moisture above threshold.")

# Manual watering function
def manual_watering():
    selected_plant = plant_combobox.get()
    print(f"Manually watering {selected_plant} for 3 seconds...")
    if selected_plant == "Plant A":
        line_a.set_value(0)
        time.sleep(3)
        line_a.set_value(1)
    elif selected_plant == "Plant B":
        line_b.set_value(0)
        time.sleep(3)
        line_b.set_value(1)

# Function to update graphs
def update_graphs():
    ax1.clear()
    ax2.clear()

    selected_plant = plant_combobox.get()
    if selected_plant == "Plant A":
        ax1.plot(short_term_data_a, color="blue", linewidth=2, label="Short Term - Plant A")
        ax2.plot(long_term_data_a, color="blue", linewidth=2, label="Long Term - Plant A")
        ax1.set_title('Short Term Moisture Data - Plant A', color="blue")
        ax2.set_title('Long Term Moisture Data - Plant A', color="blue")
    elif selected_plant == "Plant B":
        ax1.plot(short_term_data_b, color="green", linewidth=2, label="Short Term - Plant B")
        ax2.plot(long_term_data_b, color="green", linewidth=2, label="Long Term - Plant B")
        ax1.set_title('Short Term Moisture Data - Plant B', color="green")
        ax2.set_title('Long Term Moisture Data - Plant B', color="green")

    for ax, label_color in [(ax1, "blue"), (ax2, "green")]:
        ax.set_xlabel('Time', color=label_color)
        ax.set_ylabel('Moisture Level', color=label_color)
        ax.tick_params(colors=label_color)
        ax.legend()

    canvas.draw()

# Dropdown change event handler
def on_plant_selection(event):
    update_graphs()

# UDP listener thread
def udp_listener():
    global line_a, line_b
    while True:
        data, addr = server_socket.recvfrom(1024)
        message = data.decode('utf-8')
        try:
            moisture_a, moisture_b = map(int, message.split(","))
            print(f"Moisture Levels - Plant A: {moisture_a}, Plant B: {moisture_b}")

            # Update data buffers
            short_term_data_a.append(moisture_a)
            short_term_data_b.append(moisture_b)
            if len(short_term_data_a) > 10:
                short_term_data_a.pop(0)
            if len(short_term_data_b) > 10:
                short_term_data_b.pop(0)

            long_term_data_a.append(moisture_a)
            long_term_data_b.append(moisture_b)
            if len(long_term_data_a) > 100:
                long_term_data_a.pop(0)
            if len(long_term_data_b) > 100:
                long_term_data_b.pop(0)

            control_pumps(chip, line_a, line_b, moisture_a, moisture_b)
            update_graphs()
        except ValueError:
            print("Invalid data received.")

# GPIO setup
chip = gpiod.Chip(CHIP_NAME)
line_a = chip.get_line(RELAY_PIN_A)
line_b = chip.get_line(RELAY_PIN_B)
line_a.request(consumer="smart_plant_A", type=gpiod.LINE_REQ_DIR_OUT)
line_b.request(consumer="smart_plant_B", type=gpiod.LINE_REQ_DIR_OUT)
line_a.set_value(1)
line_b.set_value(1)

# UDP server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((LOCAL_IP, LOCAL_PORT))
print("Listening for UDP packets...")

# Start UDP listener in a separate thread
thread = Thread(target=udp_listener, daemon=True)
thread.start()

# Create tkinter GUI
root = tk.Tk()
root.title("Smart Plant Monitoring System")
root.configure(bg="#f0f8ff")  # Light blue background

# Dropdown menu for plant selection
plant_label = tk.Label(root, text="Select Plant:", bg="#f0f8ff", font=("Arial", 12))
plant_label.pack(pady=10)

plant_options = ["Plant A", "Plant B"]
plant_combobox = ttk.Combobox(root, values=plant_options, font=("Arial", 12))
plant_combobox.set("Plant A")
plant_combobox.pack(pady=10)
plant_combobox.bind("<<ComboboxSelected>>", on_plant_selection)

# Manual watering button
water_button = tk.Button(
    root,
    text="Water Plant Manually",
    command=manual_watering,
    font=("Arial", 12),
    bg="#add8e6",  # Light blue
    fg="white"
)
water_button.pack(pady=10)

# Create a frame for the graphs
frame = tk.Frame(root, bg="#f0f8ff")
frame.pack(padx=20, pady=20)

# Create subplots for short-term and long-term data
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
fig.patch.set_facecolor("#f0f8ff")
canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.get_tk_widget().pack()

# Initially update graphs
update_graphs()

# Start the tkinter main loop
root.mainloop()
