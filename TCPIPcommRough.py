
import os
import re
import subprocess
import socket
import pandas as pd
import threading
import tkinter as tk
from tkinter import ttk
import time
device_ip = "169.254.1.1"  # Replace with the IP from the previous step
port = 52  # Replace with the device's TCP port
cmd = '038'
running= True

def create_socket_connection(ip, port):
    try:
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the camera
        sock.connect((ip, port))
        return sock
    
    except socket.error as e:
        print(f"Socket connection error: {e}")
        return None
    
def send_command(sock, command):
    try:
        # Send the specified command
        sock.sendall(command.encode('ascii'))  # Send the command
        
        # Wait to receive an acknowledgment from the camera
        response = sock.recv(1024)  # Receive the response
        #print(f"Sent: {command.strip()} | Received: {response.decode('ascii').strip()}")
        return response.decode('ascii')
    
    except socket.error as e:
        print(f"Socket error: {e}")
        return None
    
def listen_for_data(sock, file_name='camera_data.xlsx'):
    global running
    try:
        while running:  # Check if the script should keep running
            # Continuously listen for data from the camera
            data = sock.recv(1024)  # Adjust buffer size as needed
            
            if data:
                decoded_data = data.decode('ascii').strip()
                print("Received Data:", decoded_data)
                
                # Parse the response and extract relevant information
                parsed_data = parse_response(decoded_data)
                
                # Save the parsed data to Excel
                save_to_excel(parsed_data, file_name)
            else:
                # If no data is received, break the loop
                print("No data received. Exiting...")
                break
    
    except socket.error as e:
        print(f"Socket error while receiving data: {e}")
    finally:
        sock.close()

def parse_response(response):
    # Example of parsing the response
    response_parts = response.split(',')

    # Extract specific fields from the response (handle potential missing data)
    read_text1 = response_parts[9] if len(response_parts) > 9 else None
    read_text2 = response_parts[13] if len(response_parts) > 13 else None
    read_text3 = response_parts[17] if len(response_parts) > 17 else None
    read_text4 = response_parts[21] if len(response_parts) > 21 else None

    # Store the extracted data in a dictionary
    parsed_data = {
        'Timestamp': [pd.Timestamp.now()],  # Current timestamp
        'Text1': [read_text1],
        'Text2': [read_text2],
        'Text3': [read_text3],
        'Text4': [read_text4]
    }

    return parsed_data

def save_to_excel(data_dict, file_name='camera_data.xlsx'):
    # Create a pandas DataFrame with the extracted data
    df = pd.DataFrame(data_dict)
    
    # Check if the file exists
    if os.path.exists(file_name):
        # Load existing data from the Excel file
        existing_data = pd.read_excel(file_name, sheet_name='Sheet1')
        # Append the new data
        updated_data = pd.concat([existing_data, df], ignore_index=True)
    else:
        # If the file doesn't exist, the new data will be the entire dataset
        updated_data = df
    
    # Write the updated data to the Excel file
    updated_data.to_excel(file_name, index=False, sheet_name='Sheet1')
    print(f"Data saved to {file_name} successfully!")


sock = create_socket_connection(device_ip, port)

import numpy as np
import matplotlib.pyplot as plt
import time

# Function to interpret received values from the device
def parse_received_val(received_val):
    rVal = received_val[3:]
    if '-' in rVal:
        rVal = rVal.replace("-", "")
        rVal = -1 * float("." + rVal)
    else:
        rVal = rVal.replace("+", "")
        rVal = float("." + rVal)
    return rVal

# Parameters
sampling_interval = 0.1  # Time between samples in seconds
duration = 5  # Duration to record data in seconds

# Initialize list to store rVal data
rVal_data = []
start_time = time.time()

# Record data for the specified duration
while time.time() - start_time < duration:
    # Fetch new data from the device
    receivedVal = send_command(sock, "M0\r\n")
    rVal = parse_received_val(receivedVal)

    # Append the current rVal to the data list
    rVal_data.append(rVal)

    # Print the current rVal to the console
    print(f"Current rVal: {rVal}")

    # Wait for the next sample
    time.sleep(sampling_interval)

# Convert rVal_data to a numpy array for easier plotting
rVal_data = np.array(rVal_data)

# Plot the recorded data
plt.figure()
plt.plot(rVal_data, marker='o', linestyle='-')
plt.title("Recorded rVal Data")
plt.xlabel("Position (time-parametric))")
plt.ylabel("Height (um)")
plt.grid(True)
plt.show()
