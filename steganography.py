import os
import subprocess
import pickle
from PIL import Image
from io import BytesIO
import tempfile


def save_image_to_temp(image_data, file_name):
    with open(file_name, 'wb') as temp_file:
        temp_file.write(image_data)

def load_image_from_bytes(image_bytes):
    return Image.open(BytesIO(image_bytes))


class SteganographyTool:
    """A class for hiding and extracting data within images using steghide."""

    SUPPORTED_FORMATS = ("jpg", "jpeg", "bmp")

    def __init__(self, file_format):
        if not self.is_supported_format(file_format):
            raise ValueError(f"Unsupported image format: {file_format}")
        self.file_format = file_format

    @staticmethod
    def is_supported_format(file_format):
        return file_format.lower() in SteganographyTool.SUPPORTED_FORMATS
    
    # Hides the data in the image
    def hide_data_in_image(self, data, input_image_data, passcode):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_input_image_path = os.path.join(temp_dir, f"input_image.{self.file_format}")
            temp_output_image_path = os.path.join(temp_dir, f"output_image.{self.file_format}")
            temp_data_path = os.path.join(temp_dir, "temp.bin")
            
            # Write the hidden data to a temporary file
            with open(temp_data_path, "wb") as temp_file:
                pickle.dump(data, temp_file)

            # Convert bytes to image if necessary
            image = load_image_from_bytes(input_image_data)
            image.save(temp_input_image_path)

            # Use steghide to embed the data into the image
            command = ["steghide", "embed", "-cf", temp_input_image_path, "-ef", temp_data_path, "-sf", temp_output_image_path, "-p", passcode]
            try:
                subprocess.run(command, check=True)
                print(f"Data hidden successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error hiding data: {e}")

            # Load the output image after steghide has embedded the data
            with open(temp_output_image_path, 'rb') as img_file:
                output_image_data = img_file.read()

        return output_image_data

    # Extracts hidden data from the image
    def extract_data_from_image(self, steg_image_data, passcode):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_steg_image_path = os.path.join(temp_dir, f"steg_image.{self.file_format}")
            outfile_name = os.path.join(temp_dir, "out_bin.bin")

            # Save the steganographic image to a temporary file
            save_image_to_temp(steg_image_data, temp_steg_image_path)

            # Use steghide to extract the hidden data from the image
            command = ["steghide", "extract", "-sf", temp_steg_image_path, "-xf", outfile_name, "-p", passcode]

            try:
                subprocess.run(command, check=True)
                # Read and return the extracted data
                with open(outfile_name, "rb") as file:
                    hidden_data = pickle.load(file)
                    print(f"Extracted Data: {hidden_data}")
                return hidden_data
            except subprocess.CalledProcessError as e:
                print(f"Error extracting data: {e}")
                return None

# if __name__ == "__main__":
#     tool = SteganographyTool("jpg")
#     # Hiding data
#     with open('user_1.jpg', 'rb') as img_file:
#         input_image_data = img_file.read()
#     data_to_hide = {"username": "Vedant", "password": "secret123"}
    
#     stegged_image_data = tool.hide_data_in_image(data_to_hide, input_image_data, "mysecretpasscode")
#     with open('output.jpg', 'wb') as img_file:
#         img_file.write(stegged_image_data)

#     print("Data embedding done...")

#     # Extracting data
#     with open('output.jpg', 'rb') as stegimg_file:
#         steg_image_data = stegimg_file.read()
#     extracted_data = tool.extract_data_from_image(steg_image_data, "mysecretpasscode")
#     print(f"Extracted Data: {extracted_data}.....")
