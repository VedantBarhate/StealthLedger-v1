import hashlib
import ujson
import sqlite3
import time
import pickle

class Block:
    def __init__(self, index, data, previous_hash, timestamp=None):
        self.index = index
        self.data = data
        self.previous_hash = previous_hash
        self.timestamp = timestamp if timestamp else time.time()
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Calculate the SHA-256 hash of the block."""
        block_data = {
            'index': self.index,
            'data': str(self.data),
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp
            }
        block_string = ujson.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self, name):
        self.chain = []
        self.name = name
        self.conn = sqlite3.connect('database.db')
        self.create_table()
        self.load_chain_from_db()

    def create_table(self):
        """Create a table for the blockchain if it doesn't exist."""
        with self.conn:
            self.conn.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.name} (
                    block_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block BLOB NOT NULL,
                    identifier TEXT NOT NULL UNIQUE,
                    passcode TEXT NOT NULL
                )
            ''')

    def get_latest_block(self):
        """Return the latest block in the chain."""
        return self.chain[-1] if self.chain else None

    def add_block(self, data, identifier, passcode):
        """Add a new block to the chain with the provided data."""
        latest_block = self.get_latest_block()

        # Automatically set the block's index and previous hash
        index = latest_block.index + 1 if latest_block else 0
        previous_hash = latest_block.hash if latest_block else "0"

        # Create a new block with the given data and automatically generated values
        new_block = Block(index=index, data=data, previous_hash=previous_hash)
        self.chain.append(new_block)

        # Serialize block object to save it in the database
        serialized_block = pickle.dumps(new_block)

        # Save the block to the database
        with self.conn:
            self.conn.execute(f'''INSERT INTO {self.name} (block, identifier, passcode) VALUES (?, ?, ?)''', (serialized_block, identifier, passcode))

    def load_chain_from_db(self):
        """Load blockchain from the database."""
        cursor = self.conn.execute(f"SELECT block FROM {self.name} ORDER BY block_id")
        rows = cursor.fetchall()
        for row in rows:
            # Deserialize the block object from the database
            block = pickle.loads(row[0])
            self.chain.append(block)

    def is_chain_valid(self):
        """Check the validity of the blockchain."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def display_chain(self):
        """Display the blockchain."""
        for block in self.chain:
            print(f"Block {block.index}: {block.data}, Hash: {block.hash}, Previous Hash: {block.previous_hash}")

def create_blockchain(name):
    blockchain = Blockchain(name)
    if len(blockchain.chain) == 0:
        blockchain.add_block(b"Genesis_Block", "0th block", "")
    return blockchain


if __name__ == "__main__":
    # Create a new blockchain
    my_blockchain = create_blockchain("MySecureBlockchain")

    with open("user_1.jpg", "rb") as file:
        data = file.read()

    # Add new blocks with only data and passcode
    my_blockchain.add_block(data, "first", "pass1234")

    # Display the blockchain
    my_blockchain.display_chain()

    # Check if the blockchain is valid
    if my_blockchain.is_chain_valid():
        print("Blockchain is valid!")
    else:
        print("Blockchain is not valid!")