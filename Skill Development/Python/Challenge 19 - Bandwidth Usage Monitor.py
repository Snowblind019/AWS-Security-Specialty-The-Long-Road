# Challenge 19: Bandwidth Usage Monitor
# Scenario:
# You're monitoring bandwidth usage throughout the day. You need to track usage until a threshold is reached, then analyze all the data.
# Problem:

# Part 1: WHILE LOOP - Monitor Until Threshold
# Create a variable total_bandwidth set to 0 (GB used so far)
# Create a variable threshold set to 100 (GB limit)
# Create a list of hourly usage: [12, 8, 15, 22, 18, 10, 25, 14] (GB per hour)
# Create a variable hour set to 0
# Use a while loop that runs while total_bandwidth < threshold AND hour < len(hourly_usage)
# Inside the loop:
# Add the current hour's usage to total_bandwidth
# Print "Hour {hour}: Used {usage}GB - Total: {total}GB"
# Increment hour by 1

# After the loop, check:
# If total_bandwidth >= threshold: print "Warning: Bandwidth threshold exceeded!"
# Otherwise: print "Bandwidth usage normal"

# Part 2: FOR LOOP - Analyze Peak Hours
# Use the same hourly_usage list
# Use a for loop to go through each hour's usage
# For each hour, check:
# If usage > 20GB: print "Hour {number}: PEAK usage - {usage}GB"
# If usage 10-20GB: print "Hour {number}: Normal usage - {usage}GB"
# If usage < 10GB: print "Hour {number}: Low usage - {usage}GB"

# Example Output:
# === Part 1: Monitoring Bandwidth ===
# Hour 1: Used 12GB - Total: 12GB
# Hour 2: Used 8GB - Total: 20GB
# Hour 3: Used 15GB - Total: 35GB
# Hour 4: Used 22GB - Total: 57GB
# Hour 5: Used 18GB - Total: 75GB
# Hour 6: Used 10GB - Total: 85GB
# Hour 7: Used 25GB - Total: 110GB
# Warning: Bandwidth threshold exceeded!

# === Part 2: Analyzing Peak Hours ===
# Hour 1: Normal usage - 12GB
# Hour 2: Low usage - 8GB
# Hour 3: Normal usage - 15GB
# Hour 4: PEAK usage - 22GB
# Hour 5: Normal usage - 18GB
# Hour 6: Normal usage - 10GB
# Hour 7: PEAK usage - 25GB
# Hour 8: Normal usage - 14GB

total_bandwidth = 0
threshold = 100
hourly_usage = [12, 8, 15, 22, 18, 10, 25, 14]
hour = 0

while total_bandwidth < threshold and hour < len(hourly_usage):
    usage = hourly_usage[hour]
    total_bandwidth += usage
    print(f"Hour {hour +1}: Used {usage} GB - Total: {total_bandwidth}GB")
    hour += 1

if total_bandwidth >= threshold:
    print(f"Warning: Bandwidth threshold exceeded!")
else:
    print(f"Bandwidth usage normal")

for i in range(len(hourly_usage)):
    hourly = hourly_usage[i]

    if hourly > 20:
        print(f"Hour {i+1}: PEAK usage - {hourly}GB")
    elif hourly >= 10 and hourly < 20:
        print(f"Hour {i+1}: Normal usage - {hourly}GB")
    elif hourly < 10:
        print(f"Hour {i+1}: Low usage - {hourly}GB")