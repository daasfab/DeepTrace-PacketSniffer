import sys
from scapy.all import *  # importing all libraries
import threading
import os

# Initializing a list to store sniffed packets:
packets = []

# Function to convert MAC address from dashes to colons if necessary
def normalize_mac_address(mac):
    return mac.replace('-', ':')

# 1. Function to process each packet, checking its origin MAC address, storing only specified device's packets in a list:
def packet_processor(packet, target_mac):
    # if the packet has an Ethernet layer AND its MAC address matches target:
    if Ether in packet and packet[Ether].src == target_mac:
        packets.append(packet)
        print(f"Packet {len(packets) - 1}: {packet.summary()}")

# 2. Function to start the sniffer on a specified network interface
def start_sniffing(interface, target_mac):
    print(f"Sniffing on interface {interface} for device with MAC: {target_mac}")
    while not stopSniffingEvent.is_set():
        try:
            sniff(iface=interface, prn=lambda x: packet_processor(x, target_mac), timeout=1)
        except Exception as e:
            print(f"Error sniffing on interface {interface}: {e}")
            stopSniffingEvent.set()

stopSniffingEvent = threading.Event()

# 4. Fn. creates and starts a new thread that runs the start_sniffing fn. returns thread object
def sniff_packets(interface, target_mac):
    stopSniffingEvent.clear()
    sniff_thread = threading.Thread(target=start_sniffing, args=(interface, target_mac))
    sniff_thread.start()
    return sniff_thread

# 5. Fn. stops the sniffer by giving val to stopSniffingEvent, & prints message saying that sniffer has stopped
def stop_sniffer():
    stopSniffingEvent.set()
    print("Sniffer stopped :]")

# 6. Fn. filters packages based on the input protocol by iterating through the list
def filter_packets(protocol):
    filtered_packets = []
    for packet in packets:
        if protocol.lower() == "http" and HTTP in packet:
            filtered_packets.append(packet)
        elif protocol.lower() == "tcp" and TCP in packet:
            filtered_packets.append(packet)
        elif protocol.lower() == "udp" and UDP in packet:
            filtered_packets.append(packet)
        elif protocol.lower() == "ip" and IP in packet:
            filtered_packets.append(packet)
    return filtered_packets

# 7. Fn. used to display detailed information about specific packet 
def display_packet_info(packet_number):
    if 0 <= packet_number < len(packets):
        packet = packets[packet_number]
        packet.show()
    else:
        print("Invalid packet number.")

# Function to find the default network interface
def get_default_interface():
    if sys.platform.startswith('win'):
        default_interface = None
        routes = os.popen('route print').read()
        for line in routes.splitlines():
            if '0.0.0.0' in line:
                default_interface = line.split()[-1]
                break
        return default_interface
    else:
        import netifaces
        gws = netifaces.gateways()
        default_interface = gws['default'][netifaces.AF_INET][1]
        return default_interface

# 8. Main Function to organize the entire sniffer:
if __name__ == "__main__":
    # Automatically find the default network interface
    interface = get_default_interface()
    if not interface:
        print("Could not determine the default network interface. Exiting...")
        sys.exit(1)
    print(f"Default network interface detected: {interface}")

    target_mac = input("Enter the target MAC address (e.g., 00:11:22:33:44:55): ")
    target_mac = normalize_mac_address(target_mac)
    running_time = int(input("Enter the running time for the sniffer in seconds: "))

    sniff_thread = sniff_packets(interface, target_mac)

    # Stop the sniffer after the specified running time
    import time
    time.sleep(running_time)
    stop_sniffer()

    # Display all packet summaries
    for i, packet in enumerate(packets):
        print(f"Packet {i}: {packet.summary()}")

    # Prompt user to select a packet for detailed information
    while True:
        try:
            packet_number = int(input("Enter the packet number to see full details (or -1 to exit): "))
            if packet_number == -1:
                break
            display_packet_info(packet_number)
        except ValueError:
            print("Please enter a valid packet number.")
