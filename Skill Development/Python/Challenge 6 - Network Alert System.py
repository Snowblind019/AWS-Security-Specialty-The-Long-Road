# Challenge 6: Network Alert System
# Scenario:
# You're monitoring packet loss on your network. You need to create an alert system that warns you based on different severity levels.
# Problem:

# Write a Python program that:
# Takes a packet loss percentage as input
# Uses if/elif/else statements to determine the alert level:
# If packet loss is 0%: Print "Network status: Excellent"
# If packet loss is greater than 0% but less than or equal to 2%: Print "Network status: Good"
# If packet loss is greater than 2% but less than or equal to 5%: Print "Network status: Fair - Monitor closely"
# If packet loss is greater than 5%: Print "Network status: Poor - Action required!"

# Example:
# Input:
# packet_loss = 3.5

# **Expected Output:**
# Packet loss: 3.5%
# Network status: Fair - Monitor closely

# Conditional operators you'll need:
# == (equal to)
# > (greater than)
# <= (less than or equal to)
# and (both conditions must be true)
# Test Cases:
# # Test 1
# packet_loss = 0
# # Should print: "Network status: Excellent"
# # Test 2
# packet_loss = 1.5
# # Should print: "Network status: Good"
# # Test 3
# packet_loss = 3.5
# # Should print: "Network status: Fair - Monitor closely"
# # Test 4
# packet_loss = 7.2
# # Should print: "Network status: Poor - Action required!"

packet_loss = 7.2

if packet_loss == 0:
    print("Network status: Excellent")
elif packet_loss > 0 and packet_loss <= 2:
    print("Network status: Good")
elif packet_loss > 2 and packet_loss <= 5:
    print("Network status: Fair - Monitor closely")
elif packet_loss > 5:
    print("Network status: Poor - Action required!")
