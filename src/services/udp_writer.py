# src/services/udp_writer.py
import socket

class UDPWriter:
    """
    UDP Writer for sending validation signals to PLCs or other network devices.
    Sends UDP packets from a local IP:port to a remote IP:port.
    """
    def __init__(self):
        self.socket_instance = None
        self.is_connected = False
        self.local_ip = None
        self.local_port = None
        self.remote_ip = None
        self.remote_port = None

    def connect(self, local_ip, local_port, remote_ip, remote_port):
        """
        Configure UDP writer connection
        
        Args:
            local_ip: Local IP address to send from (e.g., "192.168.1.100" or "0.0.0.0")
            local_port: Local port to send from (0 = auto-assign)
            remote_ip: Remote IP address to send to (e.g., "192.168.1.50")
            remote_port: Remote port to send to (e.g., 6000)
        
        Returns:
            (success: bool, message: str)
        """
        # Validate parameters
        if not remote_ip or not remote_port:
            self.is_connected = False
            return False, "Remote IP and port must be specified"
        
        try:
            # Create UDP socket
            self.socket_instance = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_instance.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # CRITICAL FIX: Bind to specific interface IP for multi-NIC systems
            # This ensures we send from the correct Ethernet adapter
            bind_ip = local_ip if local_ip else "0.0.0.0"
            bind_port = int(local_port) if local_port else 0
            
            # Bind to specific interface (not 0.0.0.0) for proper routing
            self.socket_instance.bind((bind_ip, bind_port))
            
            # Store connection info
            self.local_ip = bind_ip
            self.local_port = bind_port
            self.remote_ip = remote_ip
            self.remote_port = int(remote_port)
            self.is_connected = True
            
            return True, f"UDP output configured: {bind_ip}:{bind_port} → {remote_ip}:{remote_port}"
            
        except Exception as e:
            self.socket_instance = None
            self.is_connected = False
            return False, f"Failed to configure UDP output: {e}"

    def disconnect(self):
        """Close the UDP socket"""
        if self.socket_instance:
            try:
                self.socket_instance.close()
            except:
                pass
            self.socket_instance = None
        self.is_connected = False

    def send(self, message):
        """
        Send a message via UDP
        
        Args:
            message: String message to send
        
        Returns:
            (success: bool, message: str)
        """
        if not self.is_connected or not self.socket_instance:
            return False, "UDP output is not configured."
        
        try:
            # Send UDP packet
            data = message.encode('utf-8')
            self.socket_instance.sendto(data, (self.remote_ip, self.remote_port))
            return True, f"Sent to {self.remote_ip}:{self.remote_port}: {message.strip()}"
        except Exception as e:
            return False, f"Error sending UDP data: {e}"
