# Challenge 18: Network Connection Monitor
# Scenario:
# You're monitoring network connections and need to retry failed connections, then analyze all connection attempts.
# Problem:

# Part 1: WHILE LOOP - Connection Retry
# Create a variable connection_attempts set to 0
# Create a variable max_attempts set to 5
# Create a variable connected set to False
# Use a while loop that runs as long as connection_attempts < max_attempts AND connected == False
# Inside the loop:

# Increment connection_attempts by 1
# Print "Attempt {number}: Trying to connect..."
# If connection_attempts == 3, set connected = True and print "Connected successfully!"
# After the loop, if still not connected, print "Failed to connect after 5 attempts"

# Part 2: FOR LOOP - Analyze Connection Times
# Create a list of connection times: [120, 95, 250, 180, 60] (milliseconds for each attempt)
# Use a for loop to go through each connection time
# For each time, check:
# If time < 100ms: print "Attempt {number}: Excellent - {time}ms"
# If time 100-200ms: print "Attempt {number}: Good - {time}ms"
# If time > 200ms: print "Attempt {number}: Slow - {time}ms"

# Example Output:
# === Part 1: Connection Attempts ===
# Attempt 1: Trying to connect...
# Attempt 2: Trying to connect...
# Attempt 3: Trying to connect...
# Connected successfully!

# === Part 2: Analyzing Connection Times ===
# Attempt 1: Good - 120ms
# Attempt 2: Excellent - 95ms
# Attempt 3: Slow - 250ms
# Attempt 4: Good - 180ms
# Attempt 5: Excellent - 60ms

connection_attempts = 0
max_attempts = 5
connected = False
connection_attempts = 0

while connection_attempts < max_attempts and connected == False:
    connection_attempts += 1
    print(f"Attempt {connection_attempts}: Trying to connect")

    if connection_attempts == 3:
        connected = True
        print(f"Connected successfully!")
    
if connected == False:
    print(f"Failed to connect after {max_attempts} attempts")

print()
    
connection_times = [120, 95, 250, 180, 60]

for i in range(len(connection_times)):
    time = connection_times[i]


    if time < 100:
        print(f"Attempt {i+1} ms: Excellent - {time}ms")
    elif time >= 100 and time < 200:
        print(f"Attempt {i+1}: Good - {time}ms")
    elif time >= 200:
        print(f"Attempt {i+1}: Slow - {time}ms")