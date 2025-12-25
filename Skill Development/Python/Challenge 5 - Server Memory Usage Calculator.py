# Challenge 5: Server Memory Usage Calculator
# Scenario:
# You're monitoring a server's memory and need to calculate how much RAM is being used and what percentage of total memory that represents.
# Problem:

# Write a Python program that:
# Takes the total RAM in GB
# Takes the amount of RAM currently used in MB
# Converts used RAM from MB to GB
# Calculates free RAM in GB
# Calculates the percentage of RAM being used
# Prints all results rounded to 2 decimal places

# Example:
# Input:
# total_ram_gb = 16
# used_ram_mb = 8192

# **Expected Output:**
# Total RAM: 16.0 GB
# Used RAM: 8.19 GB
# Free RAM: 7.81 GB
# Memory usage: 51.20%

# Conversions and formulas you need:
# 1 GB = 1024 MB
# Used RAM in GB = Used RAM in MB ÷ 1024
# Free RAM = Total RAM - Used RAM
# Usage percentage = (Used RAM ÷ Total RAM) × 100
# Test Cases:
# # Test 1
# total_ram_gb = 16
# used_ram_mb = 8192
# # Test 2
# total_ram_gb = 32
# used_ram_mb = 24576
# # Test 3
# total_ram_gb = 8
# used_ram_mb = 2048

total_ram = 32
used_ram_mb = 24576
one_gb = 1024

gb_used = (used_ram_mb / 1024)
gb_free = (total_ram - gb_used)
percent_used = (gb_used / total_ram) * 100
roounded_used = round(gb_used, 2)
rounded_percent = round(percent_used, 2)

print(f"Total RAM: {total_ram} GB")
print(f"Used RAM: {roounded_used} GB")
print(f"Free RAM: {gb_free} GB")
print(f"Memory Usage: {rounded_percent}%")