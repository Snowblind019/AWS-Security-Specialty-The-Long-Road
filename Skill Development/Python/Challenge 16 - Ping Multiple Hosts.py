# Challenge 16: Ping Multiple Hosts
# Scenario:
# You have a list of IP addresses and need to check the status of each one. Instead of writing separate code for each IP, you'll use a loop!
# Problem:

# Write a Python program that:
# Creates a list of IP addresses: ["192.168.1.1", "192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5"]
# Uses a for loop to iterate through each IP address
# For each IP, print: "Pinging 192.168.1.1..." (with the actual IP)
# Create a second list of response times: [12, 15, 11, 250, 13] (in milliseconds)
# Use a for loop with range() to iterate through indices
# For each response time, check:
# If response time is less than 50ms: print "IP: Good latency"
# If response time is 50-100ms: print "IP: Moderate latency"
# If response time is over 100ms: print "IP: High latency - investigate!"

# Example Output:
# Pinging 192.168.1.1...
# Pinging 192.168.1.2...
# Pinging 192.168.1.3...
# Pinging 192.168.1.4...
# Pinging 192.168.1.5...

# Checking response times...
# 192.168.1.1: Good latency (12ms)
# 192.168.1.2: Good latency (15ms)
# 192.168.1.3: Good latency (11ms)
# 192.168.1.4: High latency - investigate! (250ms)
# 192.168.1.5: Good latency (13ms)

addresses = ['192168.1.1', '192168.1.2', '192168.1.3', '192168.1.4', '192168.1.5']

for ip in addresses:
    print(ip)

print()
print(f"Checking response times")

ping = [12,15,11,250,13]

for ip_address in range(len(addresses)):
    ip = addresses[ip_address]
    response = ping[ip_address]

    if response < 50:
        print(f"{ip} Good latency {response} ms")
    elif response >= 50 and response < 100:
        print(f"{ip} Moderate latency {response} ms")
    elif response >= 100:
        print(f"{ip} High latency {response} ms - investigate!")