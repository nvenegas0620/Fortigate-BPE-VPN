import paramiko

# Prompt user for SSH connection parameters
hostname = input("Enter the firewall IP address: ")
username = input("Enter your username: ")
password = input("Enter your password: ")

# Establish SSH connection
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname, username=username, password=password)

# Execute command to retrieve ARP table
command = 'get system arp'
stdin, stdout, stderr = client.exec_command(command)

# Parse and print ARP table
arp_output = stdout.read().decode('utf-8')
arp_lines = arp_output.strip().split('\n')
arp_table_start = 0
for i, line in enumerate(arp_lines):
    if line.strip().startswith("1"):
        arp_table_start = i
        break

arp_table = arp_lines[arp_table_start:]
print("IP Address\t\tMAC Address")
for line in arp_table:
    entry = line.split()
    if len(entry) >= 2:
        ip = entry[0]
        mac = entry[1]
        print(f"{ip}\t{mac}")

# Close SSH connection
client.close()
