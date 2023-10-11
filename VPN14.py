import paramiko
import time

# Function to create the VPN tunnel
def create_vpn_tunnel():
    # User inputs
    firewall_ip = input("Enter the IP address of the firewall: ")
    username = input("Enter the username: ")
    password = input("Enter the password: ")

    # SSH connection details
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(firewall_ip, username=username, password=password)

    # User inputs (continued)
    tunnel_name = input("Enter VPN tunnel name: ")
    outgoing_interface = input("Enter outgoing interface: ")
    proposal = input("Enter proposal: ")
    dh_group = input("Enter DH group: ")
    pre_shared_key = input("Enter pre-shared key: ")
    remote_gateway = input("Enter remote gateway IP: ")

    local_subnet_count = int(input("Enter the number of local subnets: "))
    local_subnet_group = f"{tunnel_name}_local_subnets"
    for i in range(local_subnet_count):
        subnet = input(f"Enter local subnet {i+1}: ")
        shell.send(f"config firewall address\n")
        shell.send(f"edit {tunnel_name}_local_subnet{i+1}\n")
        shell.send(f"set subnet {subnet}\n")
        shell.send(f"next\n")
        time.sleep(1)
        shell.send("end\n")
        time.sleep(1)

    remote_subnet_count = int(input("Enter the number of remote subnets: "))
    remote_subnet_group = f"{tunnel_name}_remote_subnets"
    for i in range(remote_subnet_count):
        subnet = input(f"Enter remote subnet {i+1}: ")
        shell.send(f"config firewall address\n")
        shell.send(f"edit {tunnel_name}_remote_subnet{i+1}\n")
        shell.send(f"set subnet {subnet}\n")
        shell.send(f"next\n")
        time.sleep(1)
        shell.send("end\n")
        time.sleep(1)

    firewall_policy_ports = []
    port_count = int(input("Enter the number of ports for the firewall policy: "))
    for i in range(port_count):
        port = input(f"Enter port {i+1}: ")
        firewall_policy_ports.append(port)

    # Create SSH shell
    shell = ssh.invoke_shell()

    # Send commands
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

    shell.send("config vpn ipsec phase2-interface\n")
    time.sleep(1)

    shell.send(f"edit {tunnel_name}\n")
    shell.send(f"set phase1name {tunnel_name}\n")
    shell.send(f"set srcaddr {tunnel_name}_local_subnets\n")
    shell.send(f"set dstaddr {tunnel_name}_remote_subnets\n")
    shell.send("set keylife 28800\n")
    shell.send(f"set proposal {proposal}\n")
    shell.send("next\n")
    time.sleep(1)
    shell.send("end\n")
    time.sleep(1)

    shell.send("config firewall addrgrp\n")
    shell.send(f"edit {local_subnet_group}\n")
    shell.send("set member")
    for i in range(local_subnet_count):
        shell.send(f" {tunnel_name}_local_subnet{i+1}")
    shell.send("\n")
    shell.send("next\n")
    time.sleep(1)
    shell.send("end\n")
    time.sleep(1)

    shell.send("config firewall addrgrp\n")
    shell.send(f"edit {remote_subnet_group}\n")
    shell.send("set member")
    for i in range(remote_subnet_count):
        shell.send(f" {tunnel_name}_remote_subnet{i+1}")
    shell.send("\n")
    shell.send("next\n")
    time.sleep(1)
    shell.send("end\n")
    time.sleep(1)

    shell.send("config firewall policy\n")
    time.sleep(1)

    shell.send("edit 0\n")
    shell.send("set srcintf " + local_subnet_group + "\n")
    shell.send("set dstintf " + tunnel_name + "\n")
    shell.send("set srcaddr all\n")
    shell.send("set dstaddr all\n")
    shell.send("set action accept\n")
    shell.send("set schedule always\n")

    for port in firewall_policy_ports:
        protocol = input(f"Enter protocol for port {port} (TCP/UDP): ")
        shell.send("set service CUSTOM\n")
        shell.send(f"config firewall service custom\n")
        shell.send(f"edit {tunnel_name}_port{port}\n")
        if protocol.upper() == "TCP":
            shell.send("set tcp-portrange " + port + "\n")
        elif protocol.upper() == "UDP":
            shell.send("set udp-portrange " + port + "\n")
        shell.send("next\n")
        time.sleep(1)
        shell.send("end\n")
        time.sleep(1)

        shell.send(f"set service {tunnel_name}_port{port}\n")

    shell.send("next\n")
    time.sleep(1)
    shell.send("end\n")
    time.sleep(1)

    shell.send("end\n")
    time.sleep(1)

    # Save configuration
    shell.send("write memory\n")
    time.sleep(1)

    # Close SSH connection
    ssh.close()

# Run the function to create the VPN tunnel
create_vpn_tunnel()
