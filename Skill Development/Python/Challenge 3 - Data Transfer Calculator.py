# Challenge 1E: Data Transfer Time Calculator
# Scenario:
# You need to download a large file over your network connection and want to estimate how long it will take.
# Problem:
# Write a Python program that:

# Takes a file size in Gigabytes (GB)
# Takes a download speed in Megabits per second (Mbps)
# Converts file size to Megabits
# Calculates how many seconds the download will take
# Converts seconds to minutes
# Prints both time in seconds and minutes, rounded to 2 decimal places

# Example:
# Input:
# file_size_gb = 5.2
# download_speed_mbps = 100

# **Expected Output:**
# File size: 5.2 GB
# Download speed: 100 Mbps
# Download time: 416.0 seconds
# Download time: 6.93 minutes

# Conversions you need:
# 1 GB = 8000 Megabits (1 GB = 8 Gigabits, 1 Gigabit = 1000 Megabits)
# Time = File size in Megabits ÷ Speed in Mbps
# 1 minute = 60 seconds

# Test Cases:
# # Test 1
# file_size_gb = 5.2
# download_speed_mbps = 100
# # Test 2
# file_size_gb = 10
# download_speed_mbps = 50
# # Test 3
# file_size_gb = 2.5
# download_speed_mbps = 200

#Specified file size in GB and speed in MB
file_size = 5.2
download_speed = 100

#There are 8000 megabits in a MB
#Created variable in which Mb (8000) / speed (100)
#Another variable in which seconds (416) / 60
Mb = (file_size * 8000)
seconds = Mb / download_speed
minutes = seconds / 60

#Rounded both outputs
rounded_sec = round(seconds, 2)
rounded_time = round(minutes, 2)

#Printed them out
print(f"Size in GB: {file_size}")
print(f"File size converted to Mb: {Mb} Mb.")
print(f"Download will take {rounded_sec} seconds.")
print(f"Download will take {rounded_time} minutes.")
