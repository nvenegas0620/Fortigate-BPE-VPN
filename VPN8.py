import paramiko
import time

def create_vpn_tunnel():
    # Prompt for FortiGate device details
    fortigate_hostname = input("Enter FortiGate hostname or IP address: ")
    fortigate_username = input("Enter FortiGate username: ")
    fortigate_password = input("Enter FortiGate password: ")

    # Prompt for VPN tunnel details
    tunnel_name = input("Enter VPN tunnel name: ")

    # Prompt for local subnets
    local_subnets = []
    while True:
        subnet = input("Enter local subnet (or leave blank to finish): ")
        if not subnet:
            break
        local_subnets.append(subnet)

    # Prompt for remote subnets
    remote_subnets = []
    while True:
        subnet = input("Enter remote subnet (or leave blank to finish): ")
        if not subnet:
            break
        remote_subnets.append(subnet)

    # Prompt for pre-shared key
    pre_shared_key = input("Enter pre-shared key: ")

    # Prompt for outgoing interface
    outgoing_interface = input("Enter outgoing interface: ")

    # Prompt for destination ports
    destination_ports = []
    while True:
        port = input("Enter destination port (or leave blank to finish): ")
        if not port:
            break
        destination_ports.append(port)

    # SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(fortigate_hostname, username=fortigate_username, password=fortigate_password)

    # Start an SSH shell
    shell = ssh.invoke_shell()

    # Send configuration commands
    shell.send("config vpn ipsec phase1-interface\n")
    time.sleep(1)
    shell.send(f"edit {tunnel_name}\n")
    time.sleep(1)
    shell.send(f"set interface {outgoing_interface}\n")
    shell.send("set mode main\n")
    shell.send("set proposal aes256-sha1\n")
    shell.send("set dhgrp 5\n")
    shell.send(f"set psksecret {pre_shared_key}\n")
    shell.send("next\n")
    time.sleep(1)

    shell.send("config vpn ipsec phase2-interface\n")
    time.sleep(1)
    shell.send(f"edit {tunnel_name}\n")
    time.sleep(1)
    shell.send(f"set phase1name {tunnel_name}\n")
    shell.send(f"set src-subnet {' '.join(local_subnets)}\n")
    shell.send(f"set dst-subnet {' '.join(remote_subnets)}\n")
    shell.send("set keylife 28800\n")
    shell.send("set proposal aes256-sha1\n")
    shell.send("next\n")
    time.sleep(1)

    shell.send("config firewall policy\n")
    time.sleep(1)
    shell.send(f"edit 0\n")
    shell.send(f"set srcintf {tunnel_name}\n")
    shell.send(f"set dstintf wan1\n")
    shell.send("set srcaddr all\n")
    shell.send("set dstaddr all\n")
    shell.send("set action accept\n")
    shell.send("set schedule always\n")
    shell.send("set service CUSTOM\n")
    for port in destination_ports:
        shell.send(f"set service {port}\n")
    shell.send("next\n")
    shell.send("end\n")
    time.sleep(1)

    shell.send("execute disk scan 17\n")
    time.sleep(5)

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
