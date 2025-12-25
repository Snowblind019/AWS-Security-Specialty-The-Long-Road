# Challenge 11: Ping Response Time Analysis
# Scenario:
# You ran 10 ping tests and stored the response times. You need to analyze specific portions of the data.
# Problem:

# Write a Python program that:
# Creates a list of 10 ping times: [12, 15, 11, 45, 13, 14, 12, 16, 11, 13]
# Prints the entire list
# Prints the first 3 ping times (using list slicing)
# Prints the last 3 ping times (using list slicing)
# Prints ping times from index 3 to 6 (middle section)
# Changes the 4th ping time (the 45 which seems like an outlier) to 14
# Prints the updated list

# Example Output:
# All ping times: [12, 15, 11, 45, 13, 14, 12, 16, 11, 13]
# First 3 pings: [12, 15, 11]
# Last 3 pings: [16, 11, 13]
# Middle section (index 3-6): [45, 13, 14, 12]
# Correcting outlier at index 3...
# Updated ping times: [12, 15, 11, 14, 13, 14, 12, 16, 11, 13]

# New list operations you'll need:
# Slicing - Get multiple items:
# First 3 items: my_list[0:3] or my_list[:3]
# Last 3 items: my_list[-3:]
# Items from index 3 to 6: my_list[3:7] (note: end index is exclusive!)
# Modify an item: my_list[3] = new_value

pings = [12,15,11,45,13,14,12,16,11,13]

print(f"All the pings times are: {pings}")
print(f"First 3 pings times are: {pings[:3]}")
print(f"Last 3 ping times are: {pings[-3:]}")
print(f"Third - Sixth ping times are: {pings[3:6]}")
pings[3] = 14
print(f"Updated pings: {pings}")