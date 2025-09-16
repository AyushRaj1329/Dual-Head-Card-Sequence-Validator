import subprocess
import hashlib
import sys
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

# IMPORTANT: This public key must be replaced with the content of your public_key.pem file.
PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3ceSF2w0VpTGwSzRBvkj
+sTqDWQT5zfKwzL14zHLEHWrt4oh6MT9jSvkvYPa2h/DqzFapwRCyicCeR86PbtS
OPVntSv7eRCjWsBw7Edys06Nd+dA0UXwt9cF8ig2b8N9aXlmgdfi9P/4+Jl53WtU
CFQvbNXIpuaqS7kz+mnO6ouPrQbl7Sv/Q5pfXXWOyHrSt1o39XjgxVsn9ilQ6XJc
fH8Ar0VDOIhCliYG/jwImMgzKij4fsOSxqD+BVwg+G3th+Bl+6s5/x6mecCq/OGV
ciDlr3ucaE4UmhtB4tv/hCtbkKr5MssL6sgiIol3p+Tfic9K3bN6mRI90UwxwrxP
bQIDAQAB
-----END PUBLIC KEY-----"""

def get_machine_fingerprint():
    """
    Generates a unique machine fingerprint based on hardware serial numbers.
    """
    try:
        # Get motherboard serial number
        motherboard_serial = subprocess.check_output('wmic baseboard get serialnumber', shell=True).decode().split('\n')[1].strip()
        # Get CPU ID
        cpu_serial = subprocess.check_output('wmic cpu get processorid', shell=True).decode().split('\n')[1].strip()
        # Get primary disk drive serial number
        disk_serial = subprocess.check_output('wmic diskdrive get serialnumber', shell=True).decode().split('\n')[1].strip()

        # Combine the serials and hash them
        combined_serials = f"{motherboard_serial}-{cpu_serial}-{disk_serial}"
        fingerprint = hashlib.sha256(combined_serials.encode()).hexdigest()
        return fingerprint, None # Return fingerprint and no error
    except Exception as e:
        return None, f"Error generating machine fingerprint: {e}"

def validate_license():
    """
    Validates the license file. If the license is valid, it returns (True, message, machine_id).
    If the license is invalid or not found, it returns (False, message, machine_id).
    """
    machine_fingerprint, error_msg = get_machine_fingerprint()
    if machine_fingerprint is None:
        return False, f"Could not generate a machine ID. {error_msg}", "N/A"

    try:
        with open('license.dat', 'r') as f:
            file_content = f.read().strip()
            # DEBUG PRINT: print(f"DEBUG: Raw license file content: '{file_content}'")
            parts = file_content.split(':')
            if len(parts) != 2:
                raise ValueError(f"License file malformed: Expected 2 parts separated by ':', got {len(parts)}")
            license_fingerprint, signature_hex = parts
        
        signature = bytes.fromhex(signature_hex)

        public_key = serialization.load_pem_public_key(
            PUBLIC_KEY_PEM.encode()
        )

        # Verify the signature
        public_key.verify(
            signature,
            license_fingerprint.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Check if the fingerprint in the license matches the current machine's fingerprint
        if license_fingerprint == machine_fingerprint:
            return True, "License is valid.", machine_fingerprint
        else:
            return False, "License is for a different machine.", machine_fingerprint

    except InvalidSignature:
        return False, "Invalid license signature. The license file may be corrupt or tampered with.", machine_fingerprint
    except FileNotFoundError:
        return False, "License file not found.", machine_fingerprint
    except Exception as e:
        return False, f"An error occurred during license validation: {e}", machine_fingerprint
