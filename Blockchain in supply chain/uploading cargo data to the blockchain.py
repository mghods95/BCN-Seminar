import hashlib
import json
from datetime import datetime

class SupplyChainBlock:
    """Maritime supply chain blockchain block class"""
    def __init__(self, index, timestamp, cargo_data, previous_hash="0"):
        self.index = index
        self.timestamp = timestamp
        self.cargo_data = cargo_data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Calculate SHA256 hash for the block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "cargo_data": self.cargo_data,
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class MaritimeBlockchain:
    """Simplified blockchain system for maritime supply chain"""
    def __init__(self):
        # Initialize chain with genesis block
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        """Create the first block (genesis block) with default data"""
        return SupplyChainBlock(
            index=0,
            timestamp=str(datetime.now()),
            cargo_data={"description": "Genesis Block - Maritime Supply Chain"},
            previous_hash="0"
        )

    def get_latest_block(self):
        """Return the last block in the chain"""
        return self.chain[-1]

    def add_block(self, new_block):
        """Add a new block to the chain (link to previous block)"""
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def query_cargo_by_bol(self, bill_of_lading):
        """Query all blockchain records for a specific bill of lading number"""
        cargo_records = []
        # Iterate through all blocks (skip genesis block)
        for block in self.chain[1:]:
            if block.cargo_data.get("bill_of_lading") == bill_of_lading:
                cargo_records.append({
                    "block_index": block.index,
                    "timestamp": block.timestamp,
                    "cargo_data": block.cargo_data,
                    "block_hash": block.hash
                })
        return cargo_records

# ------------------- Test: Cargo Data On-Chain & Query -------------------
if __name__ == "__main__":
    # 1. Initialize maritime supply chain blockchain
    maritime_chain = MaritimeBlockchain()
    print("✅ Maritime blockchain initialized (genesis block created)")

    # 2. Add cargo data blocks to the chain (simulate real shipping events)
    # Event 1: Cargo departure from Shanghai Port
    cargo_event_1 = {
        "bill_of_lading": "BL20260112001",
        "shipper": "ABC Logistics",
        "consignee": "XYZ Corp",
        "location": "Shanghai Port",
        "status": "Cargo loaded onto vessel",
        "vessel_name": "MV Ocean Star"
    }
    block1 = SupplyChainBlock(
        index=1,
        timestamp=str(datetime.now()),
        cargo_data=cargo_event_1
    )
    maritime_chain.add_block(block1)

    # Event 2: Cargo arrival at Singapore Port (transshipment)
    cargo_event_2 = {
        "bill_of_lading": "BL20260112001",
        "shipper": "ABC Logistics",
        "consignee": "XYZ Corp",
        "location": "Singapore Port",
        "status": "Transshipment completed",
        "vessel_name": "MV Ocean Star"
    }
    block2 = SupplyChainBlock(
        index=2,
        timestamp=str(datetime.now()),
        cargo_data=cargo_event_2
    )
    maritime_chain.add_block(block2)

    # Event 3: Another cargo (different bill of lading)
    cargo_event_3 = {
        "bill_of_lading": "BL20260112002",
        "shipper": "DEF Shipping",
        "consignee": "UVW Ltd",
        "location": "Hamburg Port",
        "status": "Cargo discharged",
        "vessel_name": "MV Euro Line"
    }
    block3 = SupplyChainBlock(
        index=3,
        timestamp=str(datetime.now()),
        cargo_data=cargo_event_3
    )
    maritime_chain.add_block(block3)

    # 3. Query cargo tracking history by bill of lading
    print("\n--- Query Cargo Tracking (BL20260112001) ---")
    tracking_results = maritime_chain.query_cargo_by_bol("BL20260112001")
    if tracking_results:
        for record in tracking_results:
            print(f"\nBlock {record['block_index']} - {record['timestamp']}")
            print(f"Status: {record['cargo_data']['status']}")
            print(f"Location: {record['cargo_data']['location']}")
            print(f"Block Hash: {record['block_hash']}")
    else:
        print("No records found for the specified bill of lading.")

    # 4. Validate entire chain integrity
    print("\n--- Validate Entire Blockchain Integrity ---")
    chain_is_valid = True
    for i in range(1, len(maritime_chain.chain)):
        current_block = maritime_chain.chain[i]
        previous_block = maritime_chain.chain[i-1]
        
        # Check if current block hash is valid
        if current_block.hash != current_block.calculate_hash():
            chain_is_valid = False
        # Check if current block links to correct previous block
        if current_block.previous_hash != previous_block.hash:
            chain_is_valid = False

    if chain_is_valid:
        print("✅ Entire blockchain is valid (no tampering detected)")
    else:
        print("❌ Blockchain is compromised (tampering detected)")
