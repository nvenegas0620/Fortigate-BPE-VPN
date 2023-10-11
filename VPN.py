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
    ssh.invoke_shell()
    ssh.send("config system interface\n")
    time.sleep(1)

    # Create VPN tunnel interface
    ssh.send(f"edit {tunnel_name}\n")
    time.sleep(1)
    ssh.send("set type tunnel\n")
    ssh.send(f"set interface {tunnel_name}\n")
    for subnet in local_subnets:
        ssh.send(f"append local-subnet {subnet}\n")
    for subnet in remote_subnets:
        ssh.send(f"append remote-subnet {subnet}\n")
    ssh.send("set psksecret {}\n".format(pre_shared_key))
    ssh.send("next\n")

    # Save configuration
    ssh.send("end\n")
    time.sleep(1)

    # Configure firewall policies
    ssh.send("config firewall policy\n")
    ssh.send(f"edit 0\n")
    ssh.send("set srcintf {}\n".format(tunnel_name))
    ssh.send("set dstintf {}\n".format(outgoing_interface))
    ssh.send("set srcaddr all\n")
    ssh.send("set dstaddr all\n")
    ssh.send("set action accept\n")
    ssh.send("set schedule always\n")
    ssh.send("set service CUSTOM\n")
    for port in destination_ports:
        ssh.send(f"set service " + port + "\n")
    ssh.send("next\n")
    ssh.send("end\n")
    time.sleep(1)

    # Save configuration
    ssh.send("write memory\n")
    time.sleep(1)

    # Close SSH connection
    ssh.close()

# Run the script
create_vpn_tunnel()
