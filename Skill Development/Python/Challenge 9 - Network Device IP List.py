# Challenge 9: Network Device IP List
# Scenario:
# You're managing multiple network devices and need to store their IP addresses in a list, then perform some basic operations.
# Problem:

# Write a Python program that:
# Creates a list of 5 device IP addresses
# Prints the entire list
# Prints the first IP address in the list
# Prints the last IP address in the list
# Prints the total number of devices in the list
# Adds a new IP address to the list
# Prints the updated list

# Example:
# Input:
# devices = ["192.168.1.1", "192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5"]

# **Expected Output:**
# All devices: ['192.168.1.1', '192.168.1.2', '192.168.1.3', '192.168.1.4', '192.168.1.5']
# First device: 192.168.1.1
# Last device: 192.168.1.5
# Total devices: 5
# Adding new device: 192.168.1.6
# Updated list: ['192.168.1.1', '192.168.1.2', '192.168.1.3', '192.168.1.4', '192.168.1.5', '192.168.1.6']

# List basics you'll need:
# Create a list: my_list = ["item1", "item2", "item3"]
# Access first item: my_list[0] (lists start at index 0!)
# Access last item: my_list[-1]
# Get length: len(my_list)
# Add item: my_list.append("new_item")

devices = ['192.168.1.1', '192.168.1.2', '192.168.1.3', '192.168.1.4', '192.168.1.5']
total_ip = len(devices)

print(f"All the IP's are: {devices}")
print(f"The first IP is: {devices[0]}")
print(f"The last IP is: {devices[-1]}")
print(f"Total IP's: {total_ip}")
devices.append ('192.168.1.6')
print(f"Adding new IP: 192.168.1.6")
print(f"Updated Total IP's: {devices}")