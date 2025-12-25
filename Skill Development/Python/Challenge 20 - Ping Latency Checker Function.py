# Challenge 20: Ping Latency Checker Function
# Scenario:
# You're tired of writing the same latency checking code over and over. Time to make it reusable with a function!
# Problem:
# Write a Python program that:

# Creates a function called check_latency that:
# Takes one parameter: response_time (in milliseconds)
# Returns a string based on the response time:
# If < 50ms: return "Excellent"
# If 50-100ms: return "Good"
# If 100-200ms: return "Fair"
# If > 200ms: return "Poor"

# Test your function by calling it with different values and printing the results
# Example Output:
# Testing latency checker:
# 12ms: Excellent
# 75ms: Good
# 150ms: Fair
# 250ms: Poor

# # Test it
# print("Testing latency checker:")
# result = check_latency(12)
# print(f"12ms: {result}")
# result = check_latency(75)
# print(f"75ms: {result}")
# # ... more tests

def check_latency(response_time):

    if response_time < 50:
        return(f"Excellent")
    elif response_time >= 50 and response_time < 100:
        return(f"Good")
    elif response_time >= 100 and response_time < 200:
        return(f"Fair")
    elif response_time >= 200:
        return(f"Poor")
    
result = check_latency(58)
print(result)