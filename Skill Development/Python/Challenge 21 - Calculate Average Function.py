# Challenge 21: Calculate Average Function
# Scenario:
# You need to calculate averages for different network metrics. Instead of writing the same calculation code repeatedly, create a reusable function!
# Problem:
# Write a Python program that:

# Creates a function called calculate_average that:
# Takes one parameter: numbers (a list of numbers)
# Calculates the sum of all numbers in the list
# Divides by the count of numbers to get the average
# Returns the average rounded to 2 decimal places

# Test your function with:
# Ping times: [12, 15, 11, 14, 13]
# Bandwidth usage: [85, 92, 78, 88, 95]
# CPU percentages: [45, 52, 48, 50, 55]

# Print the results for each test
# Example Output:
# Average ping time: 13.0 ms
# Average bandwidth: 87.6 GB
# Average CPU usage: 50.0%

# Test it
# ping_times = [12, 15, 11, 14, 13]
# result = calculate_average(ping_times)
# print(f"Average ping time: {result} ms")
# Test with other lists...

# Key concepts:
# sum(list) - adds all numbers in a list
# len(list) - counts items in a list
# Pass a list as a parameter
# Function works with ANY list of numbers!

def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    average = total / count
    return round(average, 2)

ping_times = [12,13,15,15,16]
result = calculate_average(ping_times)
print(result)

ping_times = [12,15,11,14,13]
result = calculate_average(ping_times)
print(f"Average ping time: {result} ms")

bandwidth = [85,92,78,88,95]
result = calculate_average(bandwidth)
print(f"Average bandwidth: {result} GB")

cpu = [45,52,48,50,55]
result = calculate_average(cpu)
print(f"Average CPU usage: {result}%")