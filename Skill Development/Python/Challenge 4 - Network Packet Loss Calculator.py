# Challenge 4: Network Packet Loss Calculator
# Scenario:
# You're testing network quality by sending packets and need to calculate the packet loss percentage.
# Problem:

# Write a Python program that:
# Takes the total number of packets sent
# Takes the number of packets received
# Calculates how many packets were lost
# Calculates the packet loss percentage
# Prints the results rounded to 2 decimal places

# Example:
# Input:
# packets_sent = 1000
# packets_received = 973

# **Expected Output:**
# Packets sent: 1000
# Packets received: 973
# Packets lost: 27
# Packet loss: 2.70%

# Formulas you need:
# Packets lost = Packets sent - Packets received
# Packet loss percentage = (Packets lost ÷ Packets sent) × 100

# Test Cases:
# # Test 1
# packets_sent = 1000
# packets_received = 973
# # Test 2
# packets_sent = 500
# packets_received = 500
# # Test 3
# packets_sent = 2000
# packets_received = 1850

packet_sent = 1000
packet_received = 932

packet_lost = (packet_sent - packet_received)
packet_loss = (packet_lost / packet_sent) * 100

rounded_loss = round(packet_loss, 2)

print(f"Packets sent: {packet_sent}")
print(f"Packets received: {packet_received}")
print(f"Packets lost: {packet_lost}")
print(f"Packet loss: {rounded_loss}%")