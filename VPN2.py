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
    channel = ssh.invoke_shell()
    time.sleep(1)

    # Create VPN tunnel interface
    channel.send("config system interface\n")
    time.sleep(1)
    channel.send(f"edit {tunnel_name}\n")
    time.sleep(1)
    channel.send("set type tunnel\n")
    channel.send(f"set interface {tunnel_name}\n")
    for subnet in local_subnets:
        channel.send(f"append local-subnet {subnet}\n")
    for subnet in remote_subnets:
        channel.send(f"append remote-subnet {subnet}\n")
    channel.send("set psksecret {}\n".format(pre_shared_key))
    channel.send("next\n")
    time.sleep(1)

    # Save configuration
    channel.send("end\n")
    time.sleep(1)

    # Configure firewall policies
    channel.send("config firewall policy\n")
    channel.send(f"edit 0\n")
    channel.send("set srcintf {}\n".format(tunnel_name))
    channel.send("set dstintf {}\n".format(outgoing_interface))
    channel.send("set srcaddr all\n")
    channel.send("set dstaddr all\n")
    channel.send("set action accept\n")
    channel.send("set schedule always\n")
    channel.send("set service CUSTOM\n")
    for port in destination_ports:
        channel.send(f"set service " + port + "\n")
    channel.send("next\n")
    channel.send("end\n")
    time.sleep(1)

    # Save configuration
    channel.send("write memory\n")
    time.sleep(1)

    # Close SSH connection
    channel.close()
    ssh.close()

# Run the script
create_vpn_tunnel()
