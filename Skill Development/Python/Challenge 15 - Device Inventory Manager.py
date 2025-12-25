# Challenge 15: Device Inventory Manager
# Scenario:
# You're managing an inventory of network devices and need to track and update various attributes.
# Problem:

# Write a Python program that:
# Creates a dictionary for a switch with:
# "hostname": "Access-Switch-12"
# "location": "Building A - Floor 2"
# "port_count": 48
# "ports_used": 35
# "firmware": "15.2.4"

# Prints the device info
# Calculates available ports (port_count - ports_used) and prints it
# Calculates port utilization percentage ((ports_used / port_count) * 100) and prints it rounded to 2 decimals
# Checks if port utilization is above 80% - if yes, print "Warning: High port utilization!"; if no, print "Port utilization normal"
# Updates the firmware to "15.2.7" and ports_used to 38
# Adds a new key "last_updated" with value "2025-12-12"
# Prints the updated dictionary

# Example Output:
# Device info: {'hostname': 'Access-Switch-12', 'location': 'Building A - Floor 2', 'port_count': 48, 'ports_used': 35, 'firmware': '15.2.4'}
# Available ports: 13
# Port utilization: 72.92%
# Port utilization normal
# Updating firmware and port usage...
# Updated device: {'hostname': 'Access-Switch-12', 'location': 'Building A - Floor 2', 'port_count': 48, 'ports_used': 38, 'firmware': '15.2.7', 'last_updated': '2025-12-12'}

# What you'll practice:
# Dictionary with multiple data types
# Accessing values for calculations
# Percentage calculations from dictionary values
# Conditionals with dictionary values
# Modifying existing keys
# Adding new keys

inventory = {
    "hostname": "Access-Switch-12",
    "location": "Building A - Floor 2",
    "port_count": 48,
    "ports_used": 35,
    "firmware": "15.2.4",
}

print(f"Device info: {inventory}")
available_ports = inventory["port_count"] - inventory["ports_used"]
print(available_ports)

percent = (inventory["ports_used"] / inventory["port_count"]) * 100
rounded_percent = round(percent, 2)
print(f"{rounded_percent}%")

if percent >= 80:
    print(f"Warning: High port utilization!")
elif percent < 80:
    print(f"Port utilization normal")

inventory["firmware"] = "15.2.7"
inventory["ports_used"] = 38

inventory["last_updated"] = "2025-12-12"
print(inventory)