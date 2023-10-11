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

    # Open interactive shell session
    shell = ssh.invoke_shell()
    time.sleep(1)

    # Enter configuration mode
    shell.send("config system interface\n")
    time.sleep(1)

    # Create VPN tunnel interface
    shell.send(f"edit {tunnel_name}\n")
    time.sleep(1)
    shell.send("set type tunnel\n")
    shell.send(f"set interface {tunnel_name}\n")
    for subnet in local_subnets:
        shell.send(f"append local-subnet {subnet}\n")
    for subnet in remote_subnets:
        shell.send(f"append remote-subnet {subnet}\n")
    shell.send("set psksecret {}\n".format(pre_shared_key))
    shell.send("next\n")
    time.sleep(1)

    # Save configuration
    shell.send("end\n")
    time.sleep(1)

    # Configure firewall policies
    shell.send("config firewall policy\n")
    shell.send(f"edit 0\n")
    shell.send("set srcintf {}\n".format(tunnel_name))
    shell.send("set dstintf {}\n".format(outgoing_interface))
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

    # Save configuration
    shell.send("write memory\n")
    time.sleep(1)

    # Close SSH connection
    shell.close()
    ssh.close()

# Run the script
create_vpn_tunnel()
