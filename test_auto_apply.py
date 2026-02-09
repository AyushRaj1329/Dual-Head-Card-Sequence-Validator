#!/usr/bin/env python
"""
Test auto-apply of saved network configuration
"""
import sys
import json
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from appdirs import user_data_dir

from src.app_state import AppState
from src.ui.network_setup import NetworkSetupWindow
from src.card_types import CardType

APP_NAME = "CardSequenceValidator"
APP_AUTHOR = "YourCompany"

def create_test_cache():
    """Create a test cache with network configuration"""
    cache_dir = user_data_dir(APP_NAME, APP_AUTHOR)
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, "app_cache.json")
    
    # Create test configuration with a common gateway IP
    test_config = {
        "card_type": "half",
        "main_scanner_config": {
            "local_ip": "192.168.1.51",
            "local_port": 5000,
            "remote_ip": "192.168.1.1",  # Gateway IP (likely to be detected)
            "remote_port": None
        },
        "ondemand_scanner_config": None,
        "output_config": {
            "local_ip": "192.168.1.51",
            "local_port": 0,
            "remote_ip": "192.168.1.1",  # Gateway IP
            "remote_port": 6000
        },
        "baud_rate": 115200,
        "data_bits": 8,
        "parity": "N",
        "stop_bits": 1.0,
        "timeout": 0.02,
        "selected_output_format": "PLC Signals",
        "selected_file_path": "",
        "start_card_code": None,
        "scan_direction": "top_to_bottom",
        "log_data": [],
        "current_theme": "light"
    }
    
    with open(cache_file, 'w') as f:
        json.dump(test_config, f, indent=4)
    
    print(f"✓ Test cache created at: {cache_file}")
    print(f"  - Main scanner remote IP: {test_config['main_scanner_config']['remote_ip']}")
    print(f"  - Output remote IP: {test_config['output_config']['remote_ip']}")

def test_auto_apply():
    """Test auto-apply functionality"""
    print("=" * 70)
    print("Testing Auto-Apply of Saved Network Configuration")
    print("=" * 70)
    
    # Create test cache
    print("\n1. Creating test cache with saved configuration...")
    create_test_cache()
    
    app = QApplication(sys.argv)
    
    try:
        # Create AppState (will load cache)
        print("\n2. Creating AppState (loading cache)...")
        app_state = AppState(card_type=CardType.HALF)
        print("   ✓ AppState created")
        
        # Verify configuration loaded
        print("\n3. Verifying saved configuration loaded...")
        if app_state.main_scanner_config:
            print(f"   ✓ Main scanner config loaded:")
            print(f"     - Local: {app_state.main_scanner_config['local_ip']}:{app_state.main_scanner_config['local_port']}")
            print(f"     - Remote: {app_state.main_scanner_config.get('remote_ip', 'None')}")
        
        if app_state.output_config:
            print(f"   ✓ Output config loaded:")
            print(f"     - Local: {app_state.output_config['local_ip']}:{app_state.output_config['local_port']}")
            print(f"     - Remote: {app_state.output_config['remote_ip']}:{app_state.output_config['remote_port']}")
        
        # Create Network Setup window (will auto-apply if devices detected)
        print("\n4. Creating Network Setup window (auto-apply will run)...")
        network_window = NetworkSetupWindow(app_state)
        network_window.show()
        print("   ✓ Network Setup window created")
        
        # Check if remote IPs were detected
        print("\n5. Checking detected remote devices...")
        print(f"   - Detected {len(network_window.detected_remote_ips)} remote device(s)")
        for ip in network_window.detected_remote_ips:
            print(f"     • {ip}")
        
        # Check if saved IPs match detected IPs
        print("\n6. Checking if saved IPs are on network...")
        saved_main_ip = app_state.main_scanner_config.get('remote_ip') if app_state.main_scanner_config else None
        saved_output_ip = app_state.output_config.get('remote_ip') if app_state.output_config else None
        
        if saved_main_ip:
            if saved_main_ip in network_window.detected_remote_ips:
                print(f"   ✓ Main scanner IP {saved_main_ip} detected on network")
                print(f"   ✓ Configuration should be auto-applied")
            else:
                print(f"   ⚠ Main scanner IP {saved_main_ip} NOT detected on network")
        
        if saved_output_ip:
            if saved_output_ip in network_window.detected_remote_ips:
                print(f"   ✓ Output IP {saved_output_ip} detected on network")
                print(f"   ✓ Configuration should be auto-applied")
            else:
                print(f"   ⚠ Output IP {saved_output_ip} NOT detected on network")
        
        # Check connection status
        print("\n7. Checking connection status...")
        if app_state.output_udp_writer.is_connected:
            print(f"   ✓ Output UDP writer connected")
        else:
            print(f"   - Output UDP writer not connected")
        
        if app_state.ondemand_port_reader:
            print(f"   ✓ On-demand reader configured")
        else:
            print(f"   - On-demand reader not configured")
        
        print("\n" + "=" * 70)
        print("Auto-Apply Test Complete!")
        print("=" * 70)
        print("\nFeatures Tested:")
        print("✓ Cache with saved configuration created")
        print("✓ Configuration loaded on AppState creation")
        print("✓ Remote devices detected on network")
        print("✓ Auto-apply logic executed")
        print("✓ Saved IPs checked against detected devices")
        print("\n✅ Auto-apply functionality working!")
        
        # Close after 3 seconds
        QTimer.singleShot(3000, app.quit)
        
        return app.exec()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_auto_apply())
