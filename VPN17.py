import paramiko
import time

def create_vpn_tunnel():
    # Prompt for FortiGate device details
    fortigate_hostname = input("Enter FortiGate hostname or IP address: ")
    fortigate_username = input("Enter FortiGate username: ")
    fortigate_password = input("Enter FortiGate password: ")

    # Prompt for VPN tunnel details
    tunnel_name = input("Enter VPN tunnel name: ")

    # Prompt for local subnet addresses
    local_subnet_count = int(input("Enter the number of local subnets: "))
    local_subnets = []
    for i in range(local_subnet_count):
        local_subnet = input(f"Enter local subnet {i+1}: ")
        local_subnets.append(local_subnet)

    # Prompt for remote subnet addresses
    remote_subnet_count = int(input("Enter the number of remote subnets: "))
    remote_subnets = []
    for i in range(remote_subnet_count):
        remote_subnet = input(f"Enter remote subnet {i+1}: ")
        remote_subnets.append(remote_subnet)

    # Prompt for pre-shared key
    pre_shared_key = input("Enter pre-shared key: ")

    # Prompt for outgoing interface
    outgoing_interface = input("Enter outgoing interface: ")

    # Prompt for LAN interface
    lan_interface = input("Enter LAN interface: ")

    # Prompt for proposal
    proposal = input("Enter proposal (e.g., aes256-sha1): ")

    # Prompt for DH group
    dh_group = input("Enter DH group (e.g., 5): ")

    # Prompt for remote gateway IP address
    remote_gateway = input("Enter remote gateway IP address: ")

    # Prompt for firewall policy ports
    firewall_policy_ports = input("Enter firewall policy ports (comma-separated): ")
    firewall_policy_ports = firewall_policy_ports.split(",")

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
        local_subnet_obj = f"{tunnel_name}_local_subnet{i+1}"
        shell.send(f"edit {local_subnet_obj}\n")
        shell.send(f"set subnet {local_subnets[i]}\n")
        shell.send("next\n")
        time.sleep(1)
    time.sleep(1)

    # Create address objects for remote subnets
    for i in range(remote_subnet_count):
        remote_subnet_obj = f"{tunnel_name}_remote_subnet{i+1}"
        shell.send(f"edit {remote_subnet_obj}\n")
        shell.send(f"set subnet {remote_subnets[i]}\n")
        shell.send("next\n")
        time.sleep(1)
    shell.send("end\n")
    time.sleep(1)

    # Create address groups for local and remote subnets
    local_subnet_group = f"{tunnel_name}_local"
    remote_subnet_group = f"{tunnel_name}_remote"
    shell.send("config firewall addrgrp\n")
    shell.send(f"edit {local_subnet_group}\n")
    for i in range(local_subnet_count):
        local_subnet_obj = f"{tunnel_name}_local_subnet{i+1}"
        shell.send(f"append member {local_subnet_obj}\n")
    shell.send("next\n")
    time.sleep(1)
    shell.send(f"edit {remote_subnet_group}\n")
    for i in range(remote_subnet_count):
        remote_subnet_obj = f"{tunnel_name}_remote_subnet{i+1}"
        shell.send(f"append member {remote_subnet_obj}\n")
    shell.send("next\n")
    time.sleep(1)
    shell.send("end\n")
    time.sleep(1)

    # Create custom services for firewall policy
    for port in firewall_policy_ports:
        port_protocol = input(f"Enter protocol (TCP/UDP) for port {port}: ")
        port_protocol = port_protocol.upper()
        shell.send("config firewall service custom\n")
        time.sleep(1)
        shell.send(f"edit {tunnel_name}_port{port}\n")
        shell.send(f"set tcp-portrange {port}\n") if port_protocol == "TCP" else shell.send(f"set udp-portrange {port}\n")
        shell.send("next\n")
        time.sleep(1)
        shell.send("end\n")
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
    shell.send("end\n")
    time.sleep(1)

    # Configure Phase 2
    shell.send("config vpn ipsec phase2-interface\n")
    time.sleep(1)

    shell.send(f"edit {tunnel_name}\n")
    shell.send(f"set phase1name {tunnel_name}\n")
    shell.send(f"set src-name {local_subnet_group}\n")
    shell.send(f"set dst-name {remote_subnet_group}\n")
    shell.send(f"set proposal {proposal}\n")
    shell.send("next\n")
    time.sleep(1)
    shell.send("end\n")
    time.sleep(1)

    # Check for available policy ID
    shell.send("config firewall policy\n")
    time.sleep(1)
    shell.send("get\n")
    time.sleep(1)

    output = ""
    while True:
        if shell.recv_ready():
            output += shell.recv(1024).decode("utf-8")
        else:
            if "end" in output:
                policy_ids = [int(line.split()[1]) for line in output.splitlines() if line.startswith("edit")]
                available_policy_id = 1
                while available_policy_id in policy_ids:
                    available_policy_id += 1
                break
            else:
                time.sleep(1)

    # Configure firewall policies
    shell.send(f"edit {available_policy_id}\n")
    shell.send(f"set srcintf {lan_interface}\n")
    shell.send(f"set dstintf {tunnel_name}\n")
    shell.send("set srcaddr {local_subnet_group}\n")
    shell.send("set dstaddr {remote_subnet_group}\n")
    shell.send("set action accept\n")
    shell.send("set schedule always\n")
    shell.send("set service CUSTOM\n")
    for port in firewall_policy_ports:
        shell.send(f"set service {tunnel_name}_port{port}\n")
    shell.send("next\n")
    time.sleep(1)

    shell.send(f"edit {available_policy_id + 1}\n")
    shell.send(f"set srcintf {tunnel_name}\n")
    shell.send(f"set dstintf {lan_interface}\n")
    shell.send("set srcaddr {remote_subnet_group}\n")
    shell.send("set dstaddr {local_subnet_group}\n")
    shell.send("set action accept\n")
    shell.send("set schedule always\n")
    shell.send("set service CUSTOM\n")
    for port in firewall_policy_ports:
        shell.send(f"set service {tunnel_name}_port{port}\n")
    shell.send("next\n")
    time.sleep(1)
    shell.send("end\n")
    time.sleep(1)

    # Save configuration and exit
    shell.send("end\n")
    time.sleep(1)
    shell.send("fnsysctl save\n")
    time.sleep(1)
    shell.send("exit\n")
    time.sleep(1)

    # Close SSH connection
    ssh.close()

# Call the function to create the VPN tunnel
create_vpn_tunnel()
