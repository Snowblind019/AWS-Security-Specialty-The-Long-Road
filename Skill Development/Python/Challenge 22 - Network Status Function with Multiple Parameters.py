# Challenge 22: Network Status Function with Multiple Parameters
# Scenario:
# You need a function that checks if a device is healthy based on multiple metrics.
# Problem:
# Write a Python program that:

# Creates a function called check_device_health that:
# Takes three parameters: cpu_usage, memory_usage, disk_usage (all percentages)
# Checks if ALL metrics are below 80%
# Returns True if the device is healthy (all below 80%)
# Returns False if any metric is 80% or above

# Creates a second function called get_status_message that:
# Takes one parameter: is_healthy (True or False)
# If is_healthy is True: return "Device Status: Healthy"
# If is_healthy is False: return "Device Status: Needs Attention"

# Test with these devices:
# Device 1: CPU 65%, Memory 72%, Disk 45%
# Device 2: CPU 85%, Memory 70%, Disk 60%
# Device 3: CPU 55%, Memory 88%, Disk 50%

# Example Output:
# Device 1 - CPU: 65%, Memory: 72%, Disk: 45%
# Device Status: Healthy
# Device 2 - CPU: 85%, Memory: 70%, Disk: 60%
# Device Status: Needs Attention
# Device 3 - CPU: 55%, Memory: 88%, Disk: 50%
# Device Status: Needs Attention

# # Test Device 1
# cpu = 65
# memory = 72
# disk = 45
# print(f"Device 1 - CPU: {cpu}%, Memory: {memory}%, Disk: {disk}%")
# healthy = check_device_health(cpu, memory, disk)  # Call first function
# message = get_status_message(healthy)  # Call second function with result
# print(message)
# # Test Device 2 and 3...

# Key concepts:
# Functions with multiple parameters (separated by commas)
# Returning boolean values (True/False)
# Calling one function and using its result in another function
# Reusing functions with different values

def check_device_health(cpu_usage, memory_usage, disk_usage):
    if cpu_usage < 80 and memory_usage < 80 and disk_usage < 80:
        return True
    else:
        return False
    
def get_status_message(is_healthy):
    if is_healthy:
        return(f"Device Status: Healthy")
    else:
        return(f"Device Status: Needs Attention")
    
cpu = 65
memory = 72
disk =45
print(f"Device 1 - CPU: {cpu}%, Mamory: {memory}%, Disk: {disk}%")
healthy = check_device_health(cpu, memory, disk)
message = get_status_message(healthy)
print(message)
print()

cpu = 85
memory = 70
disk = 60
print(f"Device 2 - CPU: {cpu}%, Memory: {memory}%, Disk: {disk}%")
healthy = check_device_health(cpu,memory,disk)
message = get_status_message(healthy)
print(message)
print()

cpu = 55
memory = 88
disk = 50
print(f"Device 3 - CPU: {cpu}%, Memory: {memory}%, Disk: {disk}%")
healthy = check_device_health(cpu,memory,disk)
message = get_status_message(healthy)
print(message)
print()