"""
Unit test to verify that UDPWriter sends binary integers correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.udp_writer import UDPWriter
import socket
import threading
import time

def test_binary_integer_sending():
    """Test that binary integers are sent correctly."""
    
    print("=" * 60)
    print("Testing UDPWriter Binary Integer Sending")
    print("=" * 60)
    
    # Create a receiver socket to capture what's sent
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    receiver.bind(("127.0.0.1", 0))  # Bind to any available port
    receiver_port = receiver.getsockname()[1]
    
    print(f"\n✓ Receiver listening on 127.0.0.1:{receiver_port}")
    
    # Create UDPWriter and connect to receiver
    writer = UDPWriter()
    success, msg = writer.connect("127.0.0.1", 0, "127.0.0.1", receiver_port)
    print(f"✓ Writer connected: {msg}")
    
    # Test cases: (value, expected_bytes, description)
    test_cases = [
        ("1", bytes([1]), "Single - OK"),
        ("2", bytes([2]), "Single - NOT OK"),
        ("4", bytes([4]), "Half - OK"),
        ("5", bytes([5]), "Half - NOT OK"),
        ("7", bytes([7]), "Quarter - OK"),
        ("8", bytes([8]), "Quarter - NOT OK"),
    ]
    
    print("\n" + "-" * 60)
    print("Test Results:")
    print("-" * 60)
    
    all_passed = True
    
    for value, expected_bytes, description in test_cases:
        # Send binary integer
        success, msg = writer.send(value, as_binary_int=True)
        
        # Receive what was sent
        receiver.settimeout(1.0)
        try:
            received_data, addr = receiver.recvfrom(1024)
            
            # Check if it matches expected
            if received_data == expected_bytes:
                status = "✓ PASS"
            else:
                status = "✗ FAIL"
                all_passed = False
            
            print(f"\n{status}: {description}")
            print(f"  Input: '{value}'")
            print(f"  Expected bytes: {expected_bytes.hex()} ({expected_bytes[0]})")
            print(f"  Received bytes: {received_data.hex()} ({received_data[0] if received_data else 'empty'})")
            
        except socket.timeout:
            print(f"\n✗ FAIL: {description}")
            print(f"  Input: '{value}'")
            print(f"  Error: No data received (timeout)")
            all_passed = False
        except Exception as e:
            print(f"\n✗ FAIL: {description}")
            print(f"  Input: '{value}'")
            print(f"  Error: {e}")
            all_passed = False
    
    # Cleanup
    writer.disconnect()
    receiver.close()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests PASSED - Binary integers are being sent correctly!")
    else:
        print("✗ Some tests FAILED - Check the output above")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = test_binary_integer_sending()
    sys.exit(0 if success else 1)
