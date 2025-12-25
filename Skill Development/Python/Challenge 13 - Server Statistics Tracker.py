# Challenge 13: Server Statistics Tracker
# Scenario:
# You're tracking statistics for multiple servers and need to calculate some metrics from the data.
# Problem:

# Write a Python program that:
# Creates a dictionary with server stats:
# "cpu_usage": 75.5
# "memory_usage": 82.3
# "disk_usage": 45.0
# "network_in": 1500 (MB)
# "network_out": 2300 (MB)

# Prints all the stats
# Calculates and prints the total network traffic (network_in + network_out)
# Checks if CPU usage is above 80% - if yes, print "CPU Warning!", if no, print "CPU Normal"
# Checks if memory usage is above 80% - if yes, print "Memory Warning!", if no, print "Memory Normal"
# Adds a new stat: "alerts" with value 2
# Prints the updated dictionary

# Example Output:
# Server stats: {'cpu_usage': 75.5, 'memory_usage': 82.3, 'disk_usage': 45.0, 'network_in': 1500, 'network_out': 2300}
# Total network traffic: 3800 MB
# CPU Normal
# Memory Warning!
# Adding alert count...
# Updated stats: {'cpu_usage': 75.5, 'memory_usage': 82.3, 'disk_usage': 45.0, 'network_in': 1500, 'network_out': 2300, 'alerts': 2}

# What you'll practice:
# Creating dictionaries with numeric values
# Accessing dictionary values for calculations
# Using dictionary values in conditional statements
# Adding new keys

tracking = {
    'cpu_usage': 75.5,
    "memory_usage": 82.3,
    "disk_usage": 45.0,
    "network_in": 1500,
    "network_out": 2300
}

print(tracking)

traffic = tracking["network_in"] + tracking["network_out"]
print(traffic)

if tracking["cpu_usage"] > 80:
    print(f"CPU Warning!")
else:
    print(f"CPU Normal")
if tracking["memory_usage"] > 80:
    print(f"Memory Warning!")
else:
    print(f"Memory Normal")

tracking["alerts"] = 2
print(tracking)