# Challenge 17: Port Status Checker
# Scenario:
# You're monitoring which ports are open on multiple servers and need to check their security status.
# Problem:

# Write a Python program that:
# Creates a list of port numbers: [22, 80, 443, 3389, 8080]
# Creates a list of port names: ["SSH", "HTTP", "HTTPS", "RDP", "HTTP-Alt"]
# Creates a list of status: ["open", "open", "open", "open", "closed"]
# Use a for loop with range() to iterate through all three lists at once
# For each port, print the port number, name, and status
# Then add a security check:
# If port is 22 (SSH) and status is "open": print "Warning: SSH exposed to internet!"
# If port is 3389 (RDP) and status is "open": print "Critical: RDP exposed - high security risk!"
# If port is 80 (HTTP) and status is "open": print "Notice: Unencrypted traffic possible"
# Otherwise: print "Status: OK"

# Example Output:
# Port Status Report:
# Port 22 (SSH): open
# Warning: SSH exposed to internet!
# Port 80 (HTTP): open
# Notice: Unencrypted traffic possible
# Port 443 (HTTPS): open
# Status: OK
# Port 3389 (RDP): open
# Critical: RDP exposed - high security risk!
# Port 8080 (HTTP-Alt): closed
# Status: OK

# What you'll practice:
# Accessing three lists with the same index
# Using range(len()) pattern
# Multiple conditions checking both port number AND status
# Combining loops with if/elif/else

ports = [22, 80, 443, 3389, 8080]
names = ["SSH", "HTTP", "HTTPS", "RDP", "HTTP-Alt"]
currents = ["open", "open", "open", "open", "closed"]

for i in range(len(ports)):
    port = ports[i]
    name = names[i]
    current = currents[i]

    print(f"Port {port} ({name}): {current}")

    if port == 22 and current == "open":
        print(f"Warning: SSH exposed to internet!")
    elif port == 80 and current == "open":
        print(f"Notice: Unencrypted traffic possible")
    elif port == 443 and current == "open":
        print(f"Status: OK")
    elif port == 3389 and current == "open":
        print(f"Critical: RDP exposed - high security risk!")
    elif port == 8080 and current == "closed":
        print(f"Status: OK")