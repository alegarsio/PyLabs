"""
(c) Copyright Alegrarsio Gifta 
Netlab is lightweight network simulator based on python
Version 0.1
"""

__version__ = 0.1
__author__ = "alegrarsio"

import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
from tkinter import PhotoImage
from tkinter import Tk


import ipaddress
import time
import sys
import base64
import binascii
import subprocess

from distutils.core import setup
from Cython.Build import cythonize


class STD:
    def __init__(self, master):
        self.master = master
        self.master.title("PyLab")
        
        
        ico = Image.open('logo/PYLAB.png')
        photo = ImageTk.PhotoImage(ico)
        master.wm_iconphoto(False, photo)
        
        self.header_frame = tk.Frame(master, bg="lightgrey")
        self.header_frame.pack(side=tk.TOP, fill=tk.X , padx=3 , pady=3)
        
        
        
        self.device_settings = {}
        
        
        self.sidebar_frame = tk.Frame(master, width=100, bg="lightgrey")
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        
        self.canvas_frame = tk.Frame(master)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        
        pc_image = self.load_image("asset/pc.png")
        switch_image = self.load_image("asset/switch.png")
        router_image = self.load_image("asset/router.png")
        server_image = self.load_image("asset/server.png")  
        apn_image = self.load_image("asset/accesspoint.png")  
        
        
        wire_image = self.load_image("wire/wire.png")
        wireless_image = self.load_image("wire/wireless.png")
        trash_icon = self.load_image("animation/trash.png")
        cross_icon = self.load_image("wire/cross.png")
        laptop_icon = self.load_image("asset/laptop.png")
        printer_icon = self.load_image("asset/printer.png")
        
        cli_icon = self.load_image("asset/cli.png")
        pcap_icon = self.load_image("asset/pcap.png")
        coaxial_wire = self.load_image("wire/blue.png")
        
        self.master.geometry("1500x600")
        
        tk.Button(self.sidebar_frame, image=pc_image, command=lambda: self.add_device("pc")).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.sidebar_frame, image=switch_image, command=lambda: self.add_device("switch")).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.sidebar_frame, image=router_image, command=lambda: self.add_device("router")).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.sidebar_frame, image=server_image, command=lambda: self.add_device("server")).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.sidebar_frame, image=apn_image, command=lambda: self.add_device("access-point")).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.sidebar_frame, image=laptop_icon, command=lambda: self.add_device("laptop")).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.sidebar_frame, image=printer_icon, command=lambda: self.add_device("printer")).pack(side=tk.TOP, padx=5, pady=5)
        
        self.toolbar_frame = tk.Frame(master, bg="lightgrey")
        self.toolbar_frame.pack(side=tk.RIGHT, fill=tk.Y)

        
        self.connect_button = tk.Button(self.toolbar_frame, image=wire_image, command=self.toggle_connect_mode)
        self.connect_button.pack(side=tk.TOP, padx=4, pady=4)
        self.connect_cross_button = tk.Button(self.toolbar_frame, image=cross_icon, command=self.toggle_connect_cross_mode)
        self.connect_cross_button.pack(side=tk.TOP, padx=4, pady=4)
        self.connect_coaxial_button = tk.Button(self.toolbar_frame, image=coaxial_wire, command=self.toggle_connect_coaxial_mode)
        self.connect_coaxial_button.pack(side=tk.TOP, padx=5, pady=5)
        self.connect_wireless_button = tk.Button(self.toolbar_frame, image=wireless_image, command=self.toggle_connect_wireless_mode)
        self.connect_wireless_button.pack(side=tk.TOP, padx=5, pady=5)
        
        
        self.delete_button = tk.Button(self.toolbar_frame, image=trash_icon, command=self.toggle_delete_mode)
        self.delete_button.pack(side=tk.TOP, padx=5, pady=5 )
        
        
        
        self.send_packet_mode = False
        
        
        
        self.canvas = tk.Canvas(self.canvas_frame, bg='grey')
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        green_line = self.load_image("animation/greenline.png")
        
        self.device_images = {
            "pc": pc_image,
            "switch": switch_image,
            "router": router_image,
            "server": server_image,
            "access-point" : apn_image,
            "wire" : wire_image,
            "wireless" : wireless_image,
            "trash" : trash_icon,
            "cross" : cross_icon,
            "greenline-active" : green_line,
            "laptop" : laptop_icon,
            "printer" : printer_icon,
            "cli" : cli_icon,
            "pcap" : pcap_icon,
            "coaxial" : coaxial_wire
        }
        
        
        self.devices = { "pc": 0, 
                        "switch": 0, 
                        "router": 0,
                        "server": 0  ,
                        "access-point": 0,
                        "laptop" : 0,
                        "printer" : 0
                       }  
        
        self.default_ports = {
            'pc': [21, 22, 80],
            'laptop': [21, 22, 80],
            'router': [21, 22, 23, 80],
            'server': [21, 22, 23, 25, 80, 443]
        }
        
        self.device_ids = {}  
        self.selected_device = None
        self.drag_data = {'x': 0, 'y': 0, 'item': None}
        self.connect_mode = False
        self.connect_wireless_mode = False
        self.connect_start_device = None
        self.connect_lines = []
        self.packet_queue = []
        
        self.delete_mode = False
        self.send_packet_mode = False
        self.connect_cross_mode = False
        self.cli_mode = False
        self.connect_coaxial_mode = False


        self.canvas.bind("<Button-1>", self.select_or_connect_device)
        self.canvas.bind("<B1-Motion>", self.drag_device)
        self.canvas.bind("<ButtonRelease-1>", self.drop_device)
        self.canvas.bind("<Double-Button-1>", self.double_click_device)
        
        
        self.add_grid_to_canvas()
        
    

    
    def add_grid_to_canvas(self):
        
        grid_width = 50
        grid_height = 50

        
        for x in range(0, self.canvas.winfo_width(), grid_width):
            self.canvas.create_line(x, 0, x, self.canvas.winfo_height(), fill="black")

        
        for y in range(0, self.canvas.winfo_height(), grid_height):
            self.canvas.create_line(0, y, self.canvas.winfo_width(), y, fill="black")
    def get_device_ip(self, device_id):
        
        if device_id in self.device_settings:
            return self.device_settings[device_id].get('IP')
        return None
    def is_same_network(self, ip1, ip2):
        if ip1 is None or ip2 is None:
            return False
        network1 = ipaddress.ip_network(ip1)
        network2 = ipaddress.ip_network(ip2)
        return network1.network_address == network2.network_address

    
    def double_click_device(self, event):
        x, y = event.x, event.y
        items = self.canvas.find_overlapping(x, y, x, y)
        if items:
            clicked_device = items[0]
            if clicked_device in self.device_ids:
                self.open_device_options(clicked_device)

    from PIL import Image, ImageTk

    def open_device_options(self, device):
        options_menu = tk.Menu(self.master, tearoff=0)


        console_image = Image.open("asset/console.png")
        console_image = console_image.resize((15, 15), Image.LANCZOS)  
        config_image = Image.open("asset/config.png")
        config_image = config_image.resize((15, 15), Image.LANCZOS)  
        routing_image = Image.open("asset/routing.png")
        routing_image = routing_image.resize((15, 15), Image.LANCZOS)  


        console_image_tk = ImageTk.PhotoImage(console_image)
        config_image_tk = ImageTk.PhotoImage(config_image)
        routing_image_tk = ImageTk.PhotoImage(routing_image)

    
        options_menu.add_command(label="Console", image=console_image_tk, compound="left", command=lambda: self.open_console(device))
        options_menu.add_command(label="Configure IP", image=config_image_tk, compound="left", command=lambda: self.open_ip_settings(device))
        options_menu.add_command(label="Routing Settings", image=routing_image_tk, compound="left", command=lambda: self.open_routing_settings(device))

    
        options_menu.console_image = console_image_tk
        options_menu.config_image = config_image_tk
        options_menu.routing_image = routing_image_tk

        options_menu.post(self.master.winfo_pointerx(), self.master.winfo_pointery())

    def open_routing_settings(self, device):
        routing_window = tk.Toplevel(self.master)
        routing_window.title("Routing Settings")
        routing_window.geometry("400x250")

        frame = tk.Frame(routing_window)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        title_label = tk.Label(frame, text="Routing Configuration", font=("Helvetica", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        destination_label = tk.Label(frame, text="Destination Network:", font=("Helvetica", 12))
        destination_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.destination_entry = tk.Entry(frame, font=("Helvetica", 12))
        self.destination_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")

        next_hop_label = tk.Label(frame, text="Next Hop:", font=("Helvetica", 12))
        next_hop_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.next_hop_entry = tk.Entry(frame, font=("Helvetica", 12))
        self.next_hop_entry.grid(row=2, column=1, padx=5, pady=5, sticky="we")

        
        if device in self.device_settings:
            settings = self.device_settings[device]
            if 'Routing' in settings:
                routing_config = settings['Routing']
                self.destination_entry.insert(tk.END, routing_config.get('Destination', ''))
                self.next_hop_entry.insert(tk.END, routing_config.get('NextHop', ''))

        save_button = tk.Button(frame, text="Save", font=("Helvetica", 12), command=lambda: self.save_routing_settings(device, routing_window))
        save_button.grid(row=3, column=0, columnspan=2, pady=20, sticky="we")

        frame.grid_rowconfigure(4, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        routing_window.update_idletasks()
    def save_routing_settings(self, device, routing_window):
        destination = self.destination_entry.get()
        next_hop = self.next_hop_entry.get()

        try:
            ipaddress.ip_network(destination, strict=False)
            ipaddress.ip_address(next_hop)
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid destination network or next hop")
            return

        if device not in self.device_settings:
            self.device_settings[device] = {}

        self.device_settings[device]['Routing'] = {"Destination": destination, "NextHop": next_hop}
        routing_window.destroy()
    def send_packet(self):
        if not self.connect_start_device or not self.selected_device:
            messagebox.showerror("Error", "Please select source and destination devices.")
            return

        source_device_id = self.device_ids.get(self.connect_start_device)
        destination_device_id = self.device_ids.get(self.selected_device)
        destination_ip = self.get_device_ip(destination_device_id)

        next_hop = self.find_route(source_device_id, destination_ip)
        if next_hop:
            
            messagebox.showinfo("Success", f"Packet sent from {source_device_id} to {destination_device_id} via {next_hop}.")
        else:
            messagebox.showerror("Error", "No route found from source to destination.")

    def open_ip_settings(self, device):
        self.current_device = device
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Device Settings")
        settings_window.geometry("400x250+300+200") 

        frame = tk.Frame(settings_window)
        frame.pack(padx=20, pady=20, fill="both", expand=True)  
        title_label = tk.Label(frame, text="Network Setting", font=("Helvetica", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        ip_label = tk.Label(frame, text="IP Address:", font=("Helvetica", 12))
        ip_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.ip_entry = tk.Entry(frame, font=("Helvetica", 12))
        self.ip_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")  
        subnet_label = tk.Label(frame, text="Subnet Mask:", font=("Helvetica", 12))
        subnet_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.subnet_entry = tk.Entry(frame, font=("Helvetica", 12))
        self.subnet_entry.grid(row=2, column=1, padx=5, pady=5, sticky="we")  

        gateway_label = tk.Label(frame, text="Gateway:", font=("Helvetica", 12))
        gateway_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.gateway_entry = tk.Entry(frame, font=("Helvetica", 12))
        self.gateway_entry.grid(row=3, column=1, padx=5, pady=5, sticky="we") 

        if device in self.device_settings:
            settings = self.device_settings[device]
            if 'IP' in settings:
                self.ip_entry.insert(tk.END, settings['IP'])
            if 'Subnet' in settings:
                self.subnet_entry.insert(tk.END, settings['Subnet'])
            if 'Gateway' in settings:
                self.gateway_entry.insert(tk.END, settings['Gateway'])

        save_button = tk.Button(frame, text="Save", font=("Helvetica", 12), command=lambda: self.save_settings(device, settings_window))
        save_button.grid(row=4, column=0, columnspan=2, pady=20, sticky="we")

        frame.grid_rowconfigure(5, weight=1)
        frame.grid_columnconfigure(0, weight=1)


    def save_settings(self, device, settings_window):
        ip_address = self.ip_entry.get()
        subnet_mask = self.subnet_entry.get()
        gateway = self.gateway_entry.get()

        try:
            ipaddress.ip_address(ip_address)
            ipaddress.ip_network(subnet_mask, strict=False)
            ipaddress.ip_address(gateway)
        except ValueError:
            
            tk.messagebox.showerror("Error", "Invalid IP address, subnet mask, or gateway")
            return


        self.device_settings[device] = {"IP": ip_address, "Subnet": subnet_mask, "Gateway": gateway}
        settings_window.destroy()
    def open_console(self, device):
        console_window = tk.Toplevel(self.master)
        console_window.title(f"Console - ({self.device_settings.get(device, {}).get('IP', '0.0.0.0')})")
        console_window.geometry("500x400")
        
    

        ico = Image.open('asset/console.png')
        photo = ImageTk.PhotoImage(ico)
        console_window.wm_iconphoto(False, photo)


        frame = tk.Frame(console_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_area = tk.Text(frame, wrap=tk.WORD, font=("Courier", 12), bg="black", fg="white", insertbackground="white")
        text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        input_frame = tk.Frame(console_window)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        input_entry = tk.Entry(input_frame, font=("Courier", 12), bg="black", fg="white", insertbackground="white")
        input_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)

        def execute_command():
            command = input_entry.get()
            if command:
                output = self.run_device_command(device, command)
                text_area.insert(tk.END, f"{device}> {command}\n{output}\n")
                input_entry.delete(0, tk.END)
        
        execute_button = tk.Button(input_frame, text="Execute", command=execute_command)
        execute_button.pack(side=tk.RIGHT)

        input_entry.bind("<Return>", lambda event: execute_command())
        
    def run_device_command(self, device, command):
        
        
        if command.lower() == "ipconfig":
            
            ip_config = self.device_settings.get(device, {}).get('IP', '0.0.0.0')
            subnet_mask = self.device_settings.get(device, {}).get('Subnet','0.0.0.0')
            gateway = self.device_settings.get(device, {}).get('Gateway','0.0.0.0')
            return f"IP Configuration\n\nEthernet adapter {device}:\n   IP Address: {ip_config}\n   Subnet Mask : {subnet_mask}\n   Default Gateway : {gateway}"
        elif command.lower() == "show routing":
            routing_config = self.device_settings.get(device, {}).get('Routing', 'No routing configured')
            if routing_config == 'No routing configured':
                return routing_config
            return f"Destination: {routing_config.get('Destination')}, Next Hop: {routing_config.get('NextHop')}"
        elif command.lower().startswith("ping"):
            parts = command.split()
            if len(parts) == 2:
                ip_address = parts[1]
                return self.ping_device(ip_address)
            elif len(parts) == 4 and parts[1].lower() == '-c':
                try:
                    count = int(parts[2])
                    ip_address = parts[3]
                    return self.ping_device_c(ip_address, count)
                except ValueError:
                    return "Usage: ping -c <count> <ip_address>"
            else:
                return "Usage: ping <ip_address>\nping -c <count> <ip_address>"
            
        elif command.lower().startswith("ip address set address"):
            parts = command.split()
            print(f"Console AF_INET : {parts}")  
            if len(parts) != 6 or parts[2].lower() != 'set' or parts[3].lower() != 'address':
                return "Usage: ip address set address <ip_address> <subnet_mask>"
            ip_address = parts[4]
            subnet_mask = parts[5]
            
            
            for settings in self.device_settings.values():
                if settings.get('IP') == ip_address:
                    return "IP address is already in use"

            if device not in self.device_settings:
                self.device_settings[device] = {}
            self.device_settings[device]['IP'] = ip_address
            self.device_settings[device]['Subnet'] = subnet_mask
            return f"IP Address set to {ip_address} with Subnet mask {subnet_mask}"
        elif command.lower().startswith("ip address set gateway"):
            parts = command.split()
            print(f"Console Gateway: {parts}")  
            if len(parts) != 5 or parts[2].lower() != 'set' or parts[3].lower() != 'gateway':
                return "Usage: ip address set gateway <gateway>"
            gateway = parts[4]
            if device not in self.device_settings:
                self.device_settings[device] = {}
            self.device_settings[device]['Gateway'] = gateway
            return f"Gateway set to {gateway} for device {device}"
        elif command.lower() == "whoami":
            return self.whoami(device)
        elif command.lower().startswith("netstat"):
            if device not in self.device_settings:
                return "Device not found."
            if device not in self.default_ports:
                return "Port configuration not found for the device."
            
            ports = self.default_ports[device]
            return f"Port scan result for device {device}:\n{', '.join(map(str, ports))}"
        else:
            return "Unknown command"
   
    def ping_device(self, ip_address):
        simulated_devices = {device_info['IP']: device for device, device_info in self.device_settings.items()}
        
        if ip_address not in simulated_devices:
            return f"Ping request could not find host {ip_address}. Please check the name and try again."

        source_device_ip = list(simulated_devices.keys())[0]  
        source_device_subnet = self.device_settings[simulated_devices[source_device_ip]]['Subnet']

        
        source_network = ipaddress.ip_network(f"{source_device_ip}/{source_device_subnet}", strict=False)
        target_ip = ipaddress.ip_address(ip_address)

        
        if target_ip not in source_network:
            return f"Destination host unreachable for {ip_address}"

        response = f"Pinging {ip_address} with 32 bytes of data:\n"
        for i in range(4):
            time.sleep(1)  
            response += f"Reply from {ip_address}: bytes=32 time={i*10}ms TTL=64\n"
        
        
        return response
    def ping_device_c(self, ip_address,count):
        simulated_devices = {device_info['IP']: device for device, device_info in self.device_settings.items()}
        
        if ip_address not in simulated_devices:
            return f"Ping request could not find host {ip_address}. Please check the name and try again."

        source_device_ip = list(simulated_devices.keys())[0]  
        source_device_subnet = self.device_settings[simulated_devices[source_device_ip]]['Subnet']

        
        source_network = ipaddress.ip_network(f"{source_device_ip}/{source_device_subnet}", strict=False)
        target_ip = ipaddress.ip_address(ip_address)

        
        if target_ip not in source_network:
            return f"Destination host unreachable for {ip_address}"

        response = f"Pinging {ip_address} with 32 bytes of data:\n"
        for i in range(count):
            time.sleep(1)  
            response += f"Reply from {ip_address}: bytes=32 time={i*10}ms TTL=64\n"
        
        
        return response
    
    
    
    def get_device_name(self, device_type):
        
        if device_type == "pc":
            return "PC"
        elif device_type == "switch":
            return "Switch"
        elif device_type == "router":
            return "Router"
        
        else:
            return "Unknown Device"
                
    def load_image(self, filename):
        try:
            image = Image.open(filename)
            image = image.resize((50, 50))
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print("Error loading image:", e)

    def add_device(self, device_type):
        if device_type in self.device_images:
            image = self.device_images[device_type]
            device_num = self.devices[device_type] + 1
            device_id = f"{device_type}{device_num}"
            self.devices[device_type] += 1  
            device = self.canvas.create_image(50, 50, image=image)
            self.device_ids[device] = device_id 
            text_id = self.canvas.create_text(50, 80, text=device_id)  
            self.device_ids[device] = text_id
            
    def toggle_cli_mode(self):
        self.cli_mode = not self.cli_mode
        self.connect_mode = False
        self.connect_cross_mode = False
        self.connect_wireless_mode = False
        self.delete_mode = False
        self.send_packet_mode = False
    def toggle_connect_cross_mode(self):
        self.connect_cross_mode = not self.connect_cross_mode
        if self.connect_cross_mode:
            self.connect_cross_button.config(bg="green")
        else:
            self.connect_cross_button.config(text="Connect Cross",bg="SystemButtonFace")
   

  
        
    def send_command(self, console_entry, console_text, device_id):
        command = console_entry.get()
        console_entry.delete(0, tk.END)  
        try:
            output = self.run_command(device_id, command)  
            console_text.insert(tk.END, output + "\n")  
        except Exception as e:
            console_text.insert(tk.END, str(e) + "\n")  

    def run_command(self, device_id, command):
        if command.strip().lower() == "ipconfig":
          
            ip_address = self.get_device_ip(device_id)
            if ip_address:
                return f"IP Address of {device_id}: {ip_address}"
            else:
                return f"IP Address of {device_id} not found."
        else:
            
            return f"Command '{command}' has been executed on device {device_id}."
    def toggle_connect_mode(self):
        self.connect_mode = not self.connect_mode
        if self.connect_mode:
            self.connect_button.config(bg="green") 
        else:
            self.connect_button.config(text="Connect Wire", bg="SystemButtonFace")  

    
    def toggle_connect_wireless_mode(self):
        self.connect_wireless_mode = not self.connect_wireless_mode
        if self.connect_wireless_mode:
            self.connect_wireless_button.config(bg="green")
        else:
            self.connect_wireless_button.config(text="Connect Wireless", bg="SystemButtonFace")
    def toggle_send_packet_mode(self):
        
        self.send_packet_mode = not self.send_packet_mode
        if self.send_packet_mode:
            self.send_packet_button.config(bg="green") 
        else:
            self.send_packet_button.config(bg="SystemButtonFace")
    def toggle_delete_mode(self):
        self.delete_mode = not self.delete_mode
        if self.delete_mode:
            self.delete_button.config(bg="green")
        else:
            self.delete_button.config(text="Delete", bg="SystemButtonFace")
    def toggle_connect_coaxial_mode(self):
        self.connect_coaxial_mode = not self.connect_coaxial_mode
        if self.connect_coaxial_mode:
            self.connect_coaxial_button.config(bg="green")
        else:
            self.connect_coaxial_button.config(text="Connect Coaxial", bg="SystemButtonFace")
    def select_or_connect_device(self, event):
        x, y = event.x, event.y
        items = self.canvas.find_overlapping(x, y, x, y)
        if items:
            clicked_device = items[0]
            if self.connect_mode:
                if self.connect_start_device is None:
                    self.connect_start_device = clicked_device
                else:
                    if clicked_device != self.connect_start_device:
                        start_coords = self.canvas.coords(self.connect_start_device)
                        end_coords = self.canvas.coords(clicked_device)
                        
                        if len(start_coords) >= 2 and len(end_coords) >= 2:
                            line = self.canvas.create_line(start_coords[0], start_coords[1],
                                                           end_coords[0], end_coords[1],
                                                           fill='black', width=2.8)
                            self.connect_lines.append(line)
                            self.canvas.tag_lower(line)
                            self.connect_start_device = None
            elif self.connect_wireless_mode:
                if self.connect_start_device is None:
                    self.connect_start_device = clicked_device
                else:
                    if clicked_device != self.connect_start_device:
                        start_coords = self.canvas.coords(self.connect_start_device)
                        end_coords = self.canvas.coords(clicked_device)
                        
                        if len(start_coords) >= 2 and len(end_coords) >= 2:
                            mid_x = (start_coords[0] + end_coords[0]) / 2
                            mid_y = (start_coords[1] + end_coords[1]) / 2
                            
                            control_x1 = (start_coords[0] + mid_x) / 2
                            control_y1 = start_coords[1]
                            control_x2 = (mid_x + end_coords[0]) / 2
                            control_y2 = end_coords[1]
                            
                            curve = self.canvas.create_line(start_coords[0], start_coords[1],
                                                            control_x1, control_y1,
                                                            control_x2, control_y2,
                                                            end_coords[0], end_coords[1],
                                                            fill='black', width=2.5, smooth=True)
                            self.connect_lines.append(curve)
                            self.canvas.tag_lower(curve)
                            self.connect_start_device = None
            elif self.connect_cross_mode:
                if self.connect_start_device is None:
                    self.connect_start_device = clicked_device
                else:
                    if clicked_device != self.connect_start_device:
                        start_coords = self.canvas.coords(self.connect_start_device)
                        end_coords = self.canvas.coords(clicked_device)
                        
                        if len(start_coords) >= 2 and len(end_coords) >= 2:
                            mid_x = (start_coords[0] + end_coords[0]) / 2
                            mid_y = (start_coords[1] + end_coords[1]) / 2
                            
                            
                            line1 = self.canvas.create_line(start_coords[0], mid_y,
                                                            end_coords[0], mid_y,
                                                            fill='black', width=2.8,
                                                            dash=(5, 5))  
                            line2 = self.canvas.create_line(mid_x, start_coords[1],
                                                            mid_x, end_coords[1],
                                                            fill='black', width=2.8,
                                                            dash=(5, 5))  
                            self.connect_lines.append(line1)
                            self.connect_lines.append(line2)
                            self.canvas.tag_lower(line1)
                            self.canvas.tag_lower(line2)
                            self.connect_start_device = None
            elif self.connect_coaxial_mode:
                if self.connect_start_device is None:
                    self.connect_start_device = clicked_device
                else:
                    if clicked_device != self.connect_start_device:
                        start_coords = self.canvas.coords(self.connect_start_device)
                        end_coords = self.canvas.coords(clicked_device)
                        
                        if len(start_coords) >= 2 and len(end_coords) >= 2:
                            mid_x1 = start_coords[0] + (end_coords[0] - start_coords[0]) / 3
                            mid_y1 = start_coords[1] + (end_coords[1] - start_coords[1]) / 3
                            mid_x2 = start_coords[0] + 2 * (end_coords[0] - start_coords[0]) / 3
                            mid_y2 = start_coords[1] + 2 * (end_coords[1] - start_coords[1]) / 3

                            zigzag = self.canvas.create_line(start_coords[0], start_coords[1],
                                mid_x1, mid_y1,
                                mid_x2, mid_y2,
                                end_coords[0], end_coords[1],
                                fill='blue', width=5, dash=(10, 5))  

                            self.connect_lines.append(zigzag)
                            self.canvas.tag_lower(zigzag)
                            self.connect_start_device = None
            elif self.delete_mode:
                self.canvas.delete(clicked_device)
                if clicked_device in self.devices:
                    text_id = self.device_ids.pop(clicked_device, None)
                    if text_id:
                        self.canvas.delete(text_id)
                    self.devices.remove(clicked_device)
            if self.send_packet_mode:
                if self.selected_device is None:
                    self.selected_device = clicked_device
                else:
                    if clicked_device != self.selected_device:
                        self.send_packet()
                        self.selected_device = None
            if self.cli_mode :
                self.open_console(event)
            else:
                self.selected_device = clicked_device
                self.drag_data['item'] = self.selected_device
                self.drag_data['x'] = x
                self.drag_data['y'] = y

    def drag_device(self, event):
        if not self.connect_mode and not self.connect_wireless_mode and self.selected_device:
            dx = event.x - self.drag_data['x']
            dy = event.y - self.drag_data['y']
            self.canvas.move(self.selected_device, dx, dy)
            text_id = self.device_ids.get(self.selected_device)
            if text_id:
                self.canvas.move(text_id, dx, dy)
            
            
            for line in self.connect_lines:
                coords = self.canvas.coords(line)
                start_item = self.canvas.find_closest(coords[0], coords[1])[0]
                end_item = self.canvas.find_closest(coords[2], coords[3])[0]
                if start_item == self.selected_device:
                    self.canvas.coords(line, coords[0] + dx, coords[1] + dy, coords[2], coords[3])
                elif end_item == self.selected_device:
                    self.canvas.coords(line, coords[0], coords[1], coords[2] + dx, coords[3] + dy)

            self.drag_data['x'] = event.x
            self.drag_data['y'] = event.y

    def drop_device(self, event):
        if not self.connect_mode and not self.connect_wireless_mode and not self.delete_mode:
            self.selected_device = None
            
            
            for line in self.connect_lines:
                coords = self.canvas.coords(line)
                start_item = self.canvas.find_closest(coords[0], coords[1])[0]
                end_item = self.canvas.find_closest(coords[2], coords[3])[0]
                if start_item not in self.canvas.find_all() or end_item not in self.canvas.find_all():
                   
                    self.canvas.delete(line)
                    self.connect_lines.remove(line)
                    break

