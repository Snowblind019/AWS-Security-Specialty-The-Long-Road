# Challenge 1: Network Device Uptime Parser
# Scenario:
# You're monitoring network devices and need to parse uptime strings from different vendors. Your script receives uptime data as a string and needs to convert it to total hours.

# Write a Python program that:
# Takes an uptime string in the format: "5 days, 14 hours, 23 minutes"
# Extracts the days, hours, and minutes
# Calculates and prints the total uptime in hours (as a decimal)

# Example:
# Input: uptime = "5 days, 14 hours, 23 minutes"
# Expected Output: Total uptime: 134.38 hours

# Requirements:
# Use variables to store days, hours, and minutes
# Perform calculations to convert everything to hours
# Print the result rounded to 2 decimal places

# Test Cases to Handle:
# Test 1
# uptime = "5 days, 14 hours, 23 minutes"
# Should output: 134.38 hours
#  Test 2  
# uptime = "0 days, 3 hours, 45 minutes"
# Should output: 3.75 hours
# Test 3
# uptime = "1 days, 0 hours, 0 minutes"
# # Should output: 24.0 hours

#Assigned the time variables 
days = 5
hours = 14
minutes = 23

#Assigned variable "time" as the output of all 3 variables
time = f"Uptime = {days} days, {hours} hour, {minutes} minutes."
print(time)

#Created a variable that consists of "days" * 24 hours (5*24), "hours" (14), "minutes" / 60 (23/60)
total_hours = (days * 24) + hours + (minutes / 60)

#Created a variable that makes the "total_hours" show only 2 decimal spaces 
rounded_hours = round(total_hours, 2)

#Printed the rounded_hours variable
print(f"Device has been up for a total of {rounded_hours} hours.")