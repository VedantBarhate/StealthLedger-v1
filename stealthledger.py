from steganography import SteganographyTool
from blockchain import create_blockchain
import bcrypt
import pickle
from PIL import Image
from io import BytesIO

class StealthLedger:
    def __init__(self, name, file_format) -> None:
        self.name = name
        self.file_format = file_format
        self.steganography = SteganographyTool(file_format=self.file_format)
        self.blockchain = create_blockchain(self.name)
    
    def _hash_passcode(self, passcode):
        """Hashes the passcode using bcrypt."""
        return bcrypt.hashpw(passcode.encode('utf-8'), bcrypt.gensalt())

    def add_node(self, data, image, identifier, passcode):
        with open(image, 'rb') as img_file:
            img_data = img_file.read()
        
        steged_img_data = self.steganography.hide_data_in_image(data, img_data, passcode)

        hashed_passcode = self._hash_passcode(passcode)
        self.blockchain.add_block(steged_img_data, identifier, hashed_passcode)

        return Image.open(BytesIO(steged_img_data))


    def retrive_from_node(self, identifier, passcode):
        with self.blockchain.conn:
                cursor = self.blockchain.conn.execute(f"SELECT block, passcode FROM {self.name} WHERE identifier = ?", (identifier,))
                record = cursor.fetchone()

        if not record:
            return f"No Node with the given identifier: {identifier} found."

        serialized_block, stored_hashed_passcode = record

        # Verify the passcode
        if not bcrypt.checkpw(passcode.encode('utf-8'), stored_hashed_passcode):
            return "Passcode does not match."

        # Deserialize the block and extract data from the image
        block = pickle.loads(serialized_block)
        img_data = block.data
        hidden_data = self.steganography.extract_data_from_image(img_data, passcode)
        return hidden_data


if __name__ == "__main__":
    sl1 = StealthLedger("test_ledger", 'jpg')

    data_to_hide_1 = {"name":"vedant", "password":"123456789"}
    sl1.add_node(data_to_hide_1, "user_1.jpg", "id@123", 'passcode@1')

    data_to_hide2 = {"name":"vibhor", "password":"123456789"}
    sl1.add_node(data_to_hide2, "user_2.jpg", "id@321", 'passcode@2')

    print("___________________________________________________________________")

    x = sl1.retrive_from_node("id@123", "passcode@1")
    print(x)
    y = sl1.retrive_from_node("id@321", "passcode@2")
    print(y)

