from stealthledger import *
import os
import time

def get_sorted_files(directory, extension):
    filenames = os.listdir(directory)
    return [f for f in filenames if f.endswith(extension)]

def initialize_ledger(name, image_format):
    return StealthLedger(name, image_format)

def hide_data_in_images(ledger, txt_files, img_files, pswd_files, data_dir, output_dir):
    hiding_times = []
    for i in range(len(txt_files)):
        with open(f"{data_dir}/data_to_hide/{txt_files[i]}", 'r') as data_to_hide_file, \
             open(f"{data_dir}/passwords/{pswd_files[i]}", 'r') as pswd_file:
            
            data_to_hide = data_to_hide_file.read()
            pswd = pswd_file.read()

            # Measure the time taken to add a node
            start_time = time.time()
            node = ledger.add_node(data_to_hide, f"{data_dir}/images/{img_files[i]}", f"id_{str(img_files[i])[:-4]}", pswd)
            end_time = time.time()

            hiding_times.append(end_time - start_time)

            # Save the steganographic image
            node.save(f"{output_dir}/steged_{img_files[i]}")
    return hiding_times

def retrive_from_ledger(ledger, img_files, pswd_files, data_dir, retv_dir):
    retriving_times = []
    for i in range(len(img_files)):
        with open(f"{data_dir}/passwords/{pswd_files[i]}", 'r') as pswd_file:
            pswd = pswd_file.read()

            start_time = time.time()
            hidden_data = ledger.retrive_from_node(f"id_{str(img_files[i])[:-4]}", pswd)
            end_time = time.time()

            retriving_times.append(end_time - start_time)

            file_name = f"retv_text_{str(i).zfill(3)}.txt"
            with open(f"{retv_dir}/{file_name}", 'w') as file:
                file.write(hidden_data)
    return retriving_times


def run_test(data_dir, ledger_name, file_format):
    output_dir = f"{data_dir}/steged_images"
    os.makedirs(output_dir, exist_ok=True)
    retv_dir = f"{data_dir}/retrived_data"
    os.makedirs(retv_dir, exist_ok=True)

    # Load and sort files
    txt_files = get_sorted_files(f"{data_dir}/data_to_hide", ".txt")
    img_files = get_sorted_files(f"{data_dir}/images", f".{file_format}")
    pswd_files = get_sorted_files(f"{data_dir}/passwords", ".txt")

    # Initialize StealthLedger
    test_ledger = initialize_ledger(ledger_name, file_format)

    # Perform steganography and measure times
    hiding_times = hide_data_in_images(test_ledger, txt_files, img_files, pswd_files, data_dir, output_dir)

    retriving_times = retrive_from_ledger(test_ledger, img_files, pswd_files, data_dir, retv_dir)

    print("\n____________________________________________________________________\n\nResults:")
    # Calculate and display statistics
    # print("Hiding times:", hiding_times)
    print("Average time for  adding a node:", sum(hiding_times) / len(hiding_times))
    print()
    print("Is blockchain valid:", test_ledger.blockchain.is_chain_valid())
    print()
    # print("Retriving times:", retriving_times)
    print("Average time retriving from node:", sum(retriving_times) / len(retriving_times))

    print("Done")


if __name__ == "__main__":
    # run_test("test_dataset_1", "test_1", "jpg")
    # run_test("test_dataset_2", "test_2", "bmp")
    # run_test("test_dataset_3", "test_3", "jpg")
    # run_test("test_dataset_3", "test_jury1", "jpg")
    run_test("test_dataset_3", "test_6", "jpg")
    pass
    
