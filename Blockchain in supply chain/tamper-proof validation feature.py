import hashlib
import json
from datetime import datetime

class SupplyChainBlock:
    """Maritime supply chain blockchain block class for generating and validating blocks"""
    def __init__(self, index, timestamp, cargo_data, previous_hash="0"):
        self.index = index  # Block index
        self.timestamp = timestamp  # Timestamp of block creation
        self.cargo_data = cargo_data  # Cargo details (e.g., bill of lading, shipper, destination)
        self.previous_hash = previous_hash  # Hash of the previous block (ensures chain integrity)
        self.hash = self.calculate_hash()  # Hash of current block

    def calculate_hash(self):
        """Calculate block hash (core logic: ensures data immutability)"""
        # Convert block data to ordered string to avoid hash inconsistency from key order changes
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "cargo_data": self.cargo_data,
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()
        # Use SHA256 (standard blockchain hashing algorithm) to generate unique hash
        return hashlib.sha256(block_string).hexdigest()

# ------------------- Test: Generate Blocks + Validate Data Integrity -------------------
if __name__ == "__main__":
    # 1. Generate genesis block (first block in the chain)
    cargo_info_1 = {
        "bill_of_lading": "BL20260112001",  # Unique bill of lading number
        "shipper": "ABC Logistics",         # Cargo shipper
        "consignee": "XYZ Corp",            # Cargo consignee
        "destination": "Hamburg Port"       # Destination port
    }
    block1 = SupplyChainBlock(
        index=1,
        timestamp=str(datetime.now()),
        cargo_data=cargo_info_1
    )
    print(f"Block 1 Hash: {block1.hash}")

    # 2. Generate second block (linked to the previous block)
    cargo_info_2 = {
        "bill_of_lading": "BL20260112002",
        "shipper": "DEF Shipping",
        "consignee": "UVW Ltd",
        "destination": "Shanghai Port"
    }
    block2 = SupplyChainBlock(
        index=2,
        timestamp=str(datetime.now()),
        cargo_data=cargo_info_2,
        previous_hash=block1.hash
    )
    print(f"Block 2 Hash: {block2.hash}")

    # 3. Validate data integrity (simulate tampering scenario)
    print("\n--- Validate Data Integrity ---")
    # Normal case: Verify if block 2 hash matches original
    original_hash = block2.hash
    recalculated_hash = block2.calculate_hash()
    if recalculated_hash == original_hash:
        print("✅ Data not tampered with - validation passed")
    else:
        print("❌ Data tampered with - validation failed")

    # Tampered case: Modify cargo data and re-validate
    block2.cargo_data["destination"] = "London Port"  # Tamper with destination port
    recalculated_hash = block2.calculate_hash()  # Recalculate hash after tampering
    if recalculated_hash == original_hash:
        print("✅ Data not tampered with - validation passed")
    else:
        print("❌ Data tampered with - validation failed")
