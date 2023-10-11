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

    # Enter configuration mode
    ssh.exec_command("config system interface\n")
    time.sleep(1)

    # Create VPN tunnel interface
    ssh.exec_command(f"edit {tunnel_name}\n")
    time.sleep(1)
    ssh.exec_command("set type tunnel\n")
    ssh.exec_command(f"set interface {tunnel_name}\n")
    for subnet in local_subnets:
        ssh.exec_command(f"append local-subnet {subnet}\n")
    for subnet in remote_subnets:
        ssh.exec_command(f"append remote-subnet {subnet}\n")
    ssh.exec_command("set psksecret {}\n".format(pre_shared_key))
    ssh.exec_command("next\n")
    time.sleep(1)

    # Save configuration
    ssh.exec_command("end\n")
    time.sleep(1)

    # Configure firewall policies
    ssh.exec_command("config firewall policy\n")
    ssh.exec_command(f"edit 0\n")
    ssh.exec_command("set srcintf {}\n".format(tunnel_name))
    ssh.exec_command("set dstintf {}\n".format(outgoing_interface))
    ssh.exec_command("set srcaddr all\n")
    ssh.exec_command("set dstaddr all\n")
    ssh.exec_command("set action accept\n")
    ssh.exec_command("set schedule always\n")
    ssh.exec_command("set service CUSTOM\n")
    for port in destination_ports:
        ssh.exec_command(f"set service {port}\n")
    ssh.exec_command("next\n")
    ssh.exec_command("end\n")
    time.sleep(1)

    # Save configuration
    ssh.exec_command("write memory\n")
    time.sleep(1)

    # Close SSH connection
    ssh.close()

# Run the script
create_vpn_tunnel()
