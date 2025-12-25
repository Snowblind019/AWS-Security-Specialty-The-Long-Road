# Challenge 1B: Bandwidth Converter
# Scenario:
# You're analyzing network bandwidth usage and need to convert between different units.
# Problem:

# Write a Python program that:
# Takes bandwidth in Megabits per second (Mbps)
# Converts it to:
# Kilobits per second (Kbps)
# Gigabits per second (Gbps)
# Megabytes per second (MBps) - remember: 8 bits = 1 byte
# Prints all conversions rounded to 2 decimal places

# Example:
# Input:
# bandwidth_mbps = 250

# **Expected Output:**
# Bandwidth: 250 Mbps
# Converted to Kbps: 250000.00 Kbps
# Converted to Gbps: 0.25 Gbps
# Converted to MBps: 31.25 MBps

# Conversions to remember:
# 1 Mbps = 1000 Kbps
# 1 Gbps = 1000 Mbps
# 1 Byte = 8 bits

# Test Cases:
# # Test 1
# bandwidth_mbps = 250
# # Test 2
# bandwidth_mbps = 1000
# # Test 3
# bandwidth_mbps = 50

#Specified the bandwidth (in megabit)
bandwidth = 250

#Specified how much 1 mb is worth compared to other sizes and then multipled it by 250
Kbps = (bandwidth * 1000)
Gbps = (bandwidth * 0.001)
MBps = (bandwidth * 0.125)

#Rounded all of them to the 2nd decimal
rounded_kbps = round(Kbps, 2)
rounded_gbps = round(Gbps, 2)
rounded_mbps = round(MBps, 2)

#Printed all of them individually
print(f"Bandwidth: {bandwidth} Mbps")
print(f"Converted to Kbps: {rounded_kbps} Kbps")
print(f"Converted to Gbps: {rounded_gbps} Gbps")
print(f"Converted to MBps: {rounded_mbps} MBbps")
