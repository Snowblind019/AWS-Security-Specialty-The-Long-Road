# Challenge 10: Server Port Monitor
# Scenario:
# You're monitoring which ports are open on a server. You need to manage a list of open ports and perform various checks.
# Problem:

# Write a Python program that:
# Creates a list of open ports: [22, 80, 443, 3306, 8080]
# Prints the list of open ports
# Checks if port 443 is in the list (print "Port 443 is open" or "Port 443 is closed")
# Checks if port 25 is in the list (print "Port 25 is open" or "Port 25 is closed")
# Removes port 3306 from the list
# Prints the updated list
# Prints how many ports are currently open

# Example Output:
# Open ports: [22, 80, 443, 3306, 8080]
# Port 443 is open
# Port 25 is closed
# Closing port 3306...
# Updated open ports: [22, 80, 443, 8080]
# Total open ports: 4

# New list operations you'll need:
# Check if item exists: if item in my_list:
# Remove an item: my_list.remove(item)

port = [22,80,443,3306,8080]

print(f"All ports open: {port}")
if 443 in port:
    print(f"Port 443 is open")
else:
    print(f"Port 443 is not open")
if 25 in port:
    print(f"Port 25 is open")
else:
    print(f"Port 25 is not open")
port.remove(3306)
print(f"Removed port {port}")
print(f"Current open port: {len(port)}")