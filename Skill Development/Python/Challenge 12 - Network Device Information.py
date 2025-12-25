# Challenge 12: Network Device Information
# Scenario:
# You're managing network devices and need to store information about a router using key-value pairs.
# Problem:

# Write a Python program that:
# Creates a dictionary for a router with these keys and values:
# "hostname": "Core-Router-01"
# "ip_address": "192.168.1.1"
# "model": "Cisco 2960"
# "ports": 24
# "status": "online"

# Prints the entire dictionary
# Prints just the hostname
# Prints just the IP address
# Adds a new key "uptime_hours" with value 720
# Changes the "status" to "maintenance"
# Prints the updated dictionary

# Example Output:
# Router info: {'hostname': 'Core-Router-01', 'ip_address': '192.168.1.1', 'model': 'Cisco 2960', 'ports': 24, 'status': 'online'}
# Hostname: Core-Router-01
# IP Address: 192.168.1.1
# Adding uptime information...
# Changing status to maintenance...
# Updated info: {'hostname': 'Core-Router-01', 'ip_address': '192.168.1.1', 'model': 'Cisco 2960', 'ports': 24, 'status': 'maintenance', 'uptime_hours': 720}

# Dictionary basics you'll need:
# Create a dictionary: my_dict = {"key1": "value1", "key2": "value2"}
# Access a value: my_dict["key1"]
# Add a new key-value: my_dict["new_key"] = "new_value"
# Change a value: my_dict["existing_key"] = "updated_value"

keys = {
    "hostname": "Core-Router-01",
    "ip_address": "192.168.1.1",
    "model": "Cisco 2960",
    "ports": 24,
    "status": "online"
}
print(keys)
print(keys["ip_address"])

keys['uptime_hours'] = "720"
print(keys["uptime_hours"])

keys['status'] = "maintenance"
print(keys)