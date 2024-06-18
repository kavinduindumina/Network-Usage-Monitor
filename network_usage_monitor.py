import psutil
import tkinter as tk
from tkinter import ttk
import time
import csv
import threading
from datetime import datetime, timedelta

# Data structure to hold historical usage data
usage_data = []

def get_network_usage():
    net_io = psutil.net_io_counters()
    bytes_sent = net_io.bytes_sent
    bytes_recv = net_io.bytes_recv
    # Convert bytes to megabytes
    mb_sent = bytes_sent / (1024 * 1024)
    mb_recv = bytes_recv / (1024 * 1024)
    return mb_sent, mb_recv

def update_label():
    global last_sent, last_recv
    sent, recv = get_network_usage()
    
    # Calculate speed in Mbps
    speed_sent = (sent - last_sent) * 8  # in Mbps
    speed_recv = (recv - last_recv) * 8  # in Mbps
    
    last_sent, last_recv = sent, recv
    
    sent_label.config(text=f"MB Sent: {sent:.2f}")
    recv_label.config(text=f"MB Received: {recv:.2f}")
    sent_speed_label.config(text=f"Upload Speed: {speed_sent:.2f} Mbps")
    recv_speed_label.config(text=f"Download Speed: {speed_recv:.2f} Mbps")
    
    root.after(1000, update_label)  # Update every second

def log_data():
    global usage_data
    while True:
        sent, recv = get_network_usage()
        current_time = datetime.now()
        usage_data.append((current_time, sent, recv))
        
        # Write to CSV file
        with open('network_usage_log.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([current_time, sent, recv])
        
        time.sleep(1)

def calculate_usage(period_start, period_end):
    total_sent = 0
    total_recv = 0
    for entry in usage_data:
        timestamp, sent, recv = entry
        if period_start <= timestamp <= period_end:
            total_sent += sent
            total_recv += recv
    return total_sent, total_recv

def update_periodic_usage():
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)
    yesterday_start = today_start - timedelta(days=1)
    week_start = today_start - timedelta(days=now.weekday())
    last_week_start = week_start - timedelta(weeks=1)
    month_start = datetime(now.year, now.month, 1)
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)
    
    today_sent, today_recv = calculate_usage(today_start, now)
    yesterday_sent, yesterday_recv = calculate_usage(yesterday_start, today_start)
    week_sent, week_recv = calculate_usage(week_start, now)
    last_week_sent, last_week_recv = calculate_usage(last_week_start, week_start)
    month_sent, month_recv = calculate_usage(month_start, now)
    last_month_sent, last_month_recv = calculate_usage(last_month_start, month_start)
    
    today_usage_label.config(text=f"Today's Usage: Sent: {today_sent:.2f} MB, Received: {today_recv:.2f} MB")
    yesterday_usage_label.config(text=f"Yesterday's Usage: Sent: {yesterday_sent:.2f} MB, Received: {yesterday_recv:.2f} MB")
    week_usage_label.config(text=f"This Week's Usage: Sent: {week_sent:.2f} MB, Received: {week_recv:.2f} MB")
    last_week_usage_label.config(text=f"Last Week's Usage: Sent: {last_week_sent:.2f} MB, Received: {last_week_recv:.2f} MB")
    month_usage_label.config(text=f"This Month's Usage: Sent: {month_sent:.2f} MB, Received: {month_recv:.2f} MB")
    last_month_usage_label.config(text=f"Last Month's Usage: Sent: {last_month_sent:.2f} MB, Received: {last_month_recv:.2f} MB")
    
    root.after(60000, update_periodic_usage)  # Update every minute
    

# Initial usage values
last_sent, last_recv = get_network_usage()

# Start logging in a separate thread
log_thread = threading.Thread(target=log_data)
log_thread.daemon = True
log_thread.start()

# Set up the GUI
root = tk.Tk()
root.title("Network Usage Monitor")

notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True)

# Create frames for each tab
speed_frame = ttk.Frame(notebook, width=400, height=280)
daily_frame = ttk.Frame(notebook, width=400, height=280)
weekly_frame = ttk.Frame(notebook, width=400, height=280)
monthly_frame = ttk.Frame(notebook, width=400, height=280)

speed_frame.pack(fill='both', expand=True)
daily_frame.pack(fill='both', expand=True)
weekly_frame.pack(fill='both', expand=True)
monthly_frame.pack(fill='both', expand=True)

# Add frames to notebook
notebook.add(speed_frame, text='Speed')
notebook.add(daily_frame, text='Daily Usage')
notebook.add(weekly_frame, text='Weekly Usage')
notebook.add(monthly_frame, text='Monthly Usage')

# Speed tab
sent_label = tk.Label(speed_frame, text="MB Sent: 0.00", font=("Helvetica", 14))
sent_label.pack(pady=5)

recv_label = tk.Label(speed_frame, text="MB Received: 0.00", font=("Helvetica", 14))
recv_label.pack(pady=5)

sent_speed_label = tk.Label(speed_frame, text="Upload Speed: 0.00 Mbps", font=("Helvetica", 14))
sent_speed_label.pack(pady=5)

recv_speed_label = tk.Label(speed_frame, text="Download Speed: 0.00 Mbps", font=("Helvetica", 14))
recv_speed_label.pack(pady=5)

# Daily Usage tab
today_usage_label = tk.Label(daily_frame, text="Today's Usage: Sent: 0.00 MB, Received: 0.00 MB", font=("Helvetica", 12))
today_usage_label.pack(pady=5)

yesterday_usage_label = tk.Label(daily_frame, text="Yesterday's Usage: Sent: 0.00 MB, Received: 0.00 MB", font=("Helvetica", 12))
yesterday_usage_label.pack(pady=5)

# Weekly Usage tab
week_usage_label = tk.Label(weekly_frame, text="This Week's Usage: Sent: 0.00 MB, Received: 0.00 MB", font=("Helvetica", 12))
week_usage_label.pack(pady=5)

last_week_usage_label = tk.Label(weekly_frame, text="Last Week's Usage: Sent: 0.00 MB, Received: 0.00 MB", font=("Helvetica", 12))
last_week_usage_label.pack(pady=5)

# Monthly Usage tab
month_usage_label = tk.Label(monthly_frame, text="This Month's Usage: Sent: 0.00 MB, Received: 0.00 MB", font=("Helvetica", 12))
month_usage_label.pack(pady=5)

last_month_usage_label = tk.Label(monthly_frame, text="Last Month's Usage: Sent: 0.00 MB, Received: 0.00 MB", font=("Helvetica", 12))
last_month_usage_label.pack(pady=5)

# Start the update loop
update_label()
update_periodic_usage()

# Run the GUI event loop
root.mainloop()
