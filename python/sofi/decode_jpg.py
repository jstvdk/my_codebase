import argparse

import imghdr
import os
from PIL import Image


def reencode_jpeg_images(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg')):
                file_path = os.path.join(root, file)
                try:
                    with Image.open(file_path) as img:
                        rgb_img = img.convert('RGB')  # Ensure image is in RGB
                        rgb_img.save(file_path, format='JPEG')  # Overwrite with standard JPEG
                except Exception as e:
                    print(f"Failed to re-encode {file_path}: {e}")


def verify_jpeg_images(directory):
    invalid_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg')):
                file_path = os.path.join(root, file)
                # Check file type
                if imghdr.what(file_path) != 'jpeg':
                    invalid_files.append((file_path, 'Incorrect file type'))
                    continue
                # Check for corruption
                try:
                    with Image.open(file_path) as img:
                        img.verify()  # This will raise an exception if the image is corrupted
                except (IOError, SyntaxError) as e:
                    invalid_files.append((file_path, 'Corrupted image'))
    return invalid_files
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Re-encode JPEG images in a directory.')
    parser.add_argument('directory', help='The directory containing the images.')
    args = parser.parse_args()
    reencode_jpeg_images(args.directory)

    unsupported = verify_jpeg_images(args.directory)
    if unsupported:
        print("Issues found with the following JPEG files:")
        for file, reason in unsupported:
            print(f"{file}: {reason}")
    else:
        print("All JPEG files are valid.")
    
