import paramiko
import time

def create_vpn_tunnel():
    # Prompt for FortiGate device details
    fortigate_hostname = input("Enter FortiGate hostname or IP address: ")
    fortigate_username = input("Enter FortiGate username: ")
    fortigate_password = input("Enter FortiGate password: ")

    # Prompt for VPN tunnel details
    tunnel_name = input("Enter VPN tunnel name: ")

    # Prompt for local subnet addresses and address group name
    local_subnet_count = int(input("Enter the number of local subnets: "))
    local_subnets = []
    local_subnet_objs = []
    for i in range(local_subnet_count):
        local_subnet = input(f"Enter local subnet {i+1}: ")
        local_subnets.append(local_subnet)
        local_subnet_obj = input(f"Enter local subnet {i+1} object name: ")
        local_subnet_objs.append(local_subnet_obj)
    local_subnet_group_name = input("Enter local subnet address group name: ")

    # Prompt for remote subnet addresses and address group name
    remote_subnet_count = int(input("Enter the number of remote subnets: "))
    remote_subnets = []
    remote_subnet_objs = []
    for i in range(remote_subnet_count):
        remote_subnet = input(f"Enter remote subnet {i+1}: ")
        remote_subnets.append(remote_subnet)
        remote_subnet_obj = input(f"Enter remote subnet {i+1} object name: ")
        remote_subnet_objs.append(remote_subnet_obj)
    remote_subnet_group_name = input("Enter remote subnet address group name: ")

    # Prompt for pre-shared key
    pre_shared_key = input("Enter pre-shared key: ")

    # Prompt for outgoing interface
    outgoing_interface = input("Enter outgoing interface: ")

    # Prompt for proposal
    proposal = input("Enter proposal (e.g., aes256-sha1): ")

    # Prompt for DH group
    dh_group = input("Enter DH group (e.g., 5): ")

    # Prompt for remote gateway IP address
    remote_gateway = input("Enter remote gateway IP address: ")

    # SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(fortigate_hostname, username=fortigate_username, password=fortigate_password)

    # Start an SSH shell
    shell = ssh.invoke_shell()

    # Send configuration commands
    shell.send("config firewall address\n")
    time.sleep(1)

    # Create address objects for local subnets
    for i in range(local_subnet_count):
        shell.send(f"edit {local_subnet_objs[i]}\n")
        shell.send(f"set subnet {local_subnets[i]}\n")
        shell.send("next\n")
        time.sleep(1)

    # Create address group for local subnets
    shell.send(f"edit {local_subnet_group_name}\n")
    for i in range(local_subnet_count):
        shell.send(f"append member {local_subnet_objs[i]}\n")
    shell.send("next\n")
    time.sleep(1)

    # Create address objects for remote subnets
    for i in range(remote_subnet_count):
        shell.send(f"edit {remote_subnet_objs[i]}\n")
        shell.send(f"set subnet {remote_subnets[i]}\n")
        shell.send("next\n")
        time.sleep(1)

    # Create address group for remote subnets
    shell.send(f"edit {remote_subnet_group_name}\n")
    for i in range(remote_subnet_count):
        shell.send(f"append member {remote_subnet_objs[i]}\n")
    shell.send("next\n")
    time.sleep(1)

    # Configure Phase 1
    shell.send("config vpn ipsec phase1-interface\n")
    time.sleep(1)

    shell.send(f"edit {tunnel_name}\n")
    shell.send(f"set interface {outgoing_interface}\n")
    shell.send("set mode main\n")
    shell.send(f"set proposal {proposal}\n")
    shell.send(f"set dhgrp {dh_group}\n")
    shell.send(f"set psksecret {pre_shared_key}\n")
    shell.send(f"set remote-gw {remote_gateway}\n")
    shell.send("next\n")
    time.sleep(1)

    # Configure Phase 2
    shell.send("config vpn ipsec phase2-interface\n")
    time.sleep(1)

    shell.send(f"edit {tunnel_name}\n")
    shell.send(f"set phase1name {tunnel_name}\n")
    shell.send(f"set srcaddr {local_subnet_group_name}\n")
    shell.send(f"set dstaddr {remote_subnet_group_name}\n")
    shell.send("set keylife 28800\n")
    shell.send(f"set proposal {proposal}\n")
    shell.send("next\n")
    time.sleep(1)

    # Configure firewall policy
    shell.send("config firewall policy\n")
    time.sleep(1)

    shell.send("edit 0\n")
    shell.send(f"set srcintf {local_subnet_group_name}\n")
    shell.send(f"set dstintf {outgoing_interface}\n")
    shell.send("set srcaddr all\n")
    shell.send("set dstaddr all\n")
    shell.send("set action accept\n")
    shell.send("set schedule always\n")
    shell.send("set service CUSTOM\n")
    shell.send("set service 80\n")
    shell.send("set service 443\n")
    shell.send("next\n")
    time.sleep(1)

    shell.send("end\n")
    time.sleep(1)

    shell.send("write memory\n")
    time.sleep(1)

    # Receive and print the output
    while True:
        if shell.recv_ready():
            output = shell.recv(1024).decode("utf-8")
            print(output)
        else:
            break

    # Close the SSH connection
    shell.close()
    ssh.close()

# Run the script
create_vpn_tunnel()
