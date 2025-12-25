# Challenge 8: Server CPU Temperature Monitor
# Scenario:
# You're monitoring server CPU temperatures and need to trigger appropriate responses based on temperature readings.
# Problem:

# Write a Python program that:
# Takes a CPU temperature in Celsius
# Uses if/elif/else statements to determine the status:

# Below 50°C: "Temperature: Normal - All systems operational"
# 50-70°C: "Temperature: Elevated - Increase fan speed"
# 70-85°C: "Temperature: High - Check cooling system"
# 85-95°C: "Temperature: Critical - Throttling CPU"
# 95°C or above: "Temperature: DANGER - Emergency shutdown required!"
# Additionally, if the temperature is negative (which shouldn't happen), print "Sensor error - Invalid reading"

# Example:
# Input:
# cpu_temp = 78

# **Expected Output:**
# CPU Temperature: 78°C
# Temperature: High - Check cooling system
# Test Cases:
# # Test 1
# cpu_temp = 45
# # Output: "Temperature: Normal - All systems operational"
# # Test 2
# cpu_temp = 65
# # Output: "Temperature: Elevated - Increase fan speed"
# # Test 3
# cpu_temp = 78
# # Output: "Temperature: High - Check cooling system"
# # Test 4
# cpu_temp = 92
# # Output: "Temperature: Critical - Throttling CPU"
# # Test 5
# cpu_temp = 98
# # Output: "Temperature: DANGER - Emergency shutdown required!"
# # Test 6
# cpu_temp = -5
# # Output: "Sensor error - Invalid reading"

temp = 723

if temp >= 1 and temp < 50:
    print(f"Temperature: Normal - All systems operational")
elif temp >= 50 and temp < 70:
    print(f"Temperature: Elevated - Increase fan speed")
elif temp > 70 and temp < 85:
    print(f"Temperature: High - Check cooling system")
elif temp > 85 and temp < 95:
    print(f"Temperature: Critical - Throttling CPU")
elif temp >= 95:
    print(f"Temperature: DANGER - Emergency shutdown required!")
else:
    print(f"Sensor error - Invalid reading")