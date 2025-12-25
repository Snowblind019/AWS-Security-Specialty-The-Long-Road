# Challenge 7: Bandwidth Speed Tier Checker
# Scenario:
# Your ISP offers different service tiers. You need to check what tier a customer's speed qualifies for and if they should consider upgrading.
# Problem:

# Write a Python program that:
# Takes a download speed in Mbps
# Uses if/elif/else statements to determine the tier:
# Less than 25 Mbps: "Basic tier - Consider upgrading"
# 25-100 Mbps: "Standard tier"
# 100-500 Mbps: "Premium tier"
# 500-1000 Mbps: "Ultra tier"
# Over 1000 Mbps: "Enterprise tier"

# Print the speed and the tier
# Example:
# Input:
# download_speed = 350

# **Expected Output:**
# Download speed: 350 Mbps
# Service tier: Premium tier
# Test Cases:
# # Test 1
# download_speed = 15
# # Output: "Basic tier - Consider upgrading"
# # Test 2
# download_speed = 75
# # Output: "Standard tier"
# # Test 3
# download_speed = 350
# # Output: "Premium tier"
# # Test 4
# download_speed = 850
# # Output: "Ultra tier"
# # Test 5
# download_speed = 1200
# # Output: "Enterprise tier"

download_speed_mbps = 23

print(f"Download speed: {download_speed_mbps} Mbps")
if download_speed_mbps < 25:
    print(f"Basic tier - Consider upgrading")
elif download_speed_mbps >= 25 and download_speed_mbps <= 100:
    print(f"Standard tier")
elif download_speed_mbps > 100 and download_speed_mbps <= 500:
    print(f"Premium tier")
elif download_speed_mbps > 500 and download_speed_mbps <= 1000:
    print(f"Ultra tier")
elif download_speed_mbps > 1000:
    print(f"Enterprise tier")