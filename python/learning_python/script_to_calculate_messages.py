import re

def count_messages(file_path):
    # Define the regular expression pattern for matching timestamps
    pattern = re.compile(r'\[\d{2}\.\d{2}\.\d{4}, \d{2}:\d{2}:\d{2}\]')
    
    message_count = 0
    
    # Open and read the file
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # If the line matches the timestamp pattern, count it as a message
            if pattern.match(line):
                message_count += 1
    
    return message_count

# Path to the txt file
file_path = '/Users/vdk/_chat.txt'

# Calculate and print the number of messages
message_count = count_messages(file_path)
print(f'Total number of messages: {message_count}')