# Challenge 14: Network Interface Status Checker
# Scenario:
# You're checking the status of network interfaces on a device. Some interfaces might not have all information available.
# Problem:

# Write a Python program that:
# Creates a dictionary for a network interface:
# "interface": "GigabitEthernet0/1"
# "status": "up"
# "speed": 1000 (Mbps)
# "duplex": "full"

# Prints the interface info
# Checks if the key "vlan" exists in the dictionary - if yes, print its value; if no, print "VLAN not configured"
# Uses the .get() method to safely retrieve the "description" key (which doesn't exist) with a default value of "No description"
# Adds the keys "vlan" with value 10 and "description" with value "Uplink to Core"
# Prints the updated dictionary

# Example Output:
# Interface info: {'interface': 'GigabitEthernet0/1', 'status': 'up', 'speed': 1000, 'duplex': 'full'}
# VLAN not configured
# Description: No description
# Adding VLAN and description...
# Updated info: {'interface': 'GigabitEthernet0/1', 'status': 'up', 'speed': 1000, 'duplex': 'full', 'vlan': 10, 'description': 'Uplink to Core'}

# New dictionary operations:
# Check if key exists: if "key" in my_dict:
# Safe retrieval with default: my_dict.get("key", "default_value")
# If key exists, returns its value
# If key doesn't exist, returns the default value (doesn't cause an error!)

network = {
    "interface": "GigabitEthernet0/1",
    "status": "up",
    "speed": 1000,
    "duplex": "full"
}

print(f"Interface info: {network}")
if "vlan" in network:
    print(network["vlan"])
else:
    print(f"VLAN not configured")

description = network.get("description", "No description")
print(f"Description: {description}")

network["vlan"] = 10
network["description"] = "Uplink to Core"

print(network)

