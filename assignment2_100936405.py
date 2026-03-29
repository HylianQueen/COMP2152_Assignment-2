"""
Author: Zelda Leona Pelletier
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""

# TODO: Import the required modules (Step ii)
# socket, threading, sqlite3, os, platform, datetime
import socket
import threading
import sqlite3
import os
import platform
import datetime

# TODO: Print Python version and OS name (Step iii)
print ("Python Vesrsion:",platform.python_version())
print("Operating System:", os.name)

# TODO: Create the common_ports dictionary (Step iv)
# Add a 1-line comment above it explaining what it stores
# A Dictionary that stores the most common port nums and thei names.
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt"
}

# TODO: Create the NetworkTool parent class (Step v)
# - Constructor: takes target, stores as private self.__target
# - @property getter for target
# - @target.setter with empty string validation
# - Destructor: prints "NetworkTool instance destroyed"
class NetworkTool:
    def __init__(self, target):
        self.__target = target

# Q3: What is the benefit of using @property and @target.setter?
# Implementing @property and @target.setter facilitates controlled access to the private variable.
#It enables us to verify the value before changing it and helps prevent the introduction of invalid data.
#This enhances data protection and renders the class more secure and adaptable.
    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        if value != "":
            self._target = value
        else : print("Error: Must Select Target, Cannot Be Empty")

    def _del_(self):
        print("NetworkTool instance destroyed")

# Q1: How does PortScanner reuse code from NetworkTool?
# The code of NetworkTool is recycled by PortScanner through inheritance. 
# The PortScanner class does not require the rewriting of the code, as it inherits the target attribute, getter, and setter from NetworkTool.
# For instance, self may be implemented by PortScanner.target to access
# the target IP address, as that functionality is already implemented in NetworkTool.
class PortScanner(NetworkTool):
    def __init__(self, target):
        super().__init__(target)
        self.scan_results = []
        self.lock = threading.Lock()

    def _del_(self):
        print("PortScanner instance destroyed")
        super()._del_()

    def scan_port(self, port):
#  Q4: What would happen without try-except here?
#  The program could terminate unexpectedly if the try-except block were removed,
#  as any socket error during the connection attempt could result in this. 
#  The scanner is able to continue examining other ports despite the fact that one port 
#  generates an error by managing the exception. 
#  This enhances the program's dependability and stability.
        try:
            sock = socket.socket(socket.Af_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port))

            if result == 0:
                status = "Open"
            else:
                status = "Closed"

            service_name = common_ports.get(port, "Unkown")
            self.lock.acquire()
            self.scan_result.append((port, status, service_name))
            self.lock.release()

        except socket.error as e:
            print(f"Error scanning port {port}: {e}")  

        finally:
            sock.close()             

    def get_open_ports(self):
        return [result for result in self.scan_results if result[1] == "Open"]
    
   
#     Q2: Why do we use threading instead of scanning one port at a time?
# Threading allows the program to simultaneously scan numerous terminals, thereby accelerating the scan process.
# The program could take a long time to complete if 1024 ports were scanned one by one, as each connection waits for a response or termination.
# The scanner is more efficient and its performance is enhanced by the use of threads.
    def scan_range(self, start_port, end_port):
        threads = []

        for port in range( start_port, end_port + 1):
            thread = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(thread)

        for thread in threads: 
            thread.start()
        
        for thread in threads:
            thread.join()

def save_results(target, results):
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT,
            port INTEGER, status TEXT, service TEXT, scan_date TEXT
        )
        """)
        for port, status, service in results:
            cursor.execute(
                "INSERT INTO scans (target, port, status, service, scan_date) VALUES (?, ?, ?, ?, ?)",
                (target, port, status, service, str(datetime.datetime.now()))
            )
        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print("Database error:", e)

def load_past_scans():
    try:
        conn = sqlite3.connet("scan_history.db")
        cursor = conn.cursor()

        cursor.excecute("SELECT * FROM scans")
        rows = cursor.fetchall()

        conn.close()
    except sqlite3.Error:
        print("No past scans have been found.")



# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    target = input("Enter target ip address: ").strip()
    if target == "":
        target = "127.0.0.1"
    try:
        start_port = int(input("Enter start port number: "))
        end_port = int(input("Enter end port number: "))

        if start_port < 1 or start_port > 1024 or end_port < 1 or end_port > 1024:
            print("Port must be between 1 and 1024.")
        elif end_port < start_port:
            print("Ending port must be greater than or equal to starting port.")
        else:
            
            scanner = PortScanner(target)
            print(f"Scanning {target} from port {start_port} to {end_port}...")

            scanner.scan_range(start_port, end_port)
            open_ports = scanner.get_open_ports()

            print(f"--- Scan Results for {target} ---")
            for port, status, service in open_ports:
                print(f"Port {port}: {status} ({service})")

            print("------")
            print(f"Total open ports found: {len(open_ports)}")

            save_results(target, scanner.scan_results)
            show_history = input("Would you like to see past scan history? (Yes/No): ").strip().lower()
            if show_history == "Yes":
                load_past_scans()

    except ValueError:
        print("Invalid Entry. Please enter a valid integer.")


# Q5: New Feature Proposal
# I would incorporate a feature that allows users to save the scan results locally by exporting them to a.txt file.
# Before writing the scan results to the file, I would convert them to formatted text lines using a list comprehension. 
# This would simplify the process of maintaining a record of scans without the need to open the database each time.


# Diagram: See diagram_studentID.png in the repository root
