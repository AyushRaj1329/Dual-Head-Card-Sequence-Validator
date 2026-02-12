"""
Test script to verify that output signals are being sent as binary integers.
This script listens on a UDP port and displays received data in both hex and decimal format.
"""

import socket
import sys

def listen_for_output_signals(local_ip="0.0.0.0", local_port=6000):
    """
    Listen for UDP packets and display them as binary integers.
    
    Args:
        local_ip: IP to listen on (default: 0.0.0.0 - all interfaces)
        local_port: Port to listen on (default: 6000)
    """
    print(f"Starting UDP listener on {local_ip}:{local_port}")
    print("Waiting for output signals...")
    print("-" * 60)
    
    try:
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((local_ip, local_port))
        
        print(f"✓ Listening on {local_ip}:{local_port}")
        print("Configure your app to send output to this address and port.")
        print("-" * 60)
        
        while True:
            # Receive data
            data, addr = sock.recvfrom(1024)
            
            # Display received data
            print(f"\nReceived from {addr[0]}:{addr[1]}")
            print(f"  Raw bytes: {data}")
            print(f"  Hex: {data.hex()}")
            
            # Try to interpret as single byte integer
            if len(data) == 1:
                int_value = data[0]
                print(f"  Integer value: {int_value}")
                
                # Map to card type and status
                card_type_map = {
                    1: "Single - OK",
                    2: "Single - NOT OK",
                    4: "Half - OK",
                    5: "Half - NOT OK",
                    7: "Quarter - OK",
                    8: "Quarter - NOT OK"
                }
                
                if int_value in card_type_map:
                    print(f"  Meaning: {card_type_map[int_value]}")
                else:
                    print(f"  ⚠ Unknown value (expected 1-8)")
            else:
                print(f"  ⚠ Received {len(data)} bytes (expected 1 byte)")
                # Try to decode as string
                try:
                    text = data.decode('utf-8')
                    print(f"  As text: {repr(text)}")
                except:
                    print(f"  Cannot decode as UTF-8")
            
            print("-" * 60)
    
    except KeyboardInterrupt:
        print("\n\nListener stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    # Parse command line arguments
    local_ip = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    local_port = int(sys.argv[2]) if len(sys.argv) > 2 else 6000
    
    listen_for_output_signals(local_ip, local_port)
