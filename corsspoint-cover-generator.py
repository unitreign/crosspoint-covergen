#!/usr/bin/env python3
"""
Crosspoint Cover generator with Floyd-Steinberg Dithering
Converts images to 1-bit BMP format suitable for Crosspoint firmware
"""

from PIL import Image
import numpy as np
import sys
import os


def floyd_steinberg_dither(image):
    """
    Floyd-Steinberg dithering algorithm
    makes grayscale into binary (black/white only)
    """
    # Convert to numpy array for processing
    img_array = np.array(image, dtype=float)
    height, width = img_array.shape
    
    # go through each pixel
    for y in range(height):
        for x in range(width):
            old_pixel = img_array[y, x]
            # threshold at 127 (middle of 0-255)
            new_pixel = 255 if old_pixel > 127 else 0
            img_array[y, x] = new_pixel
            
            # calculate error and distribute to neighbors
            error = old_pixel - new_pixel
            
            # distribute error using FS weights
            if x + 1 < width:
                img_array[y, x + 1] += error * 7/16
            if y + 1 < height:
                if x > 0:
                    img_array[y + 1, x - 1] += error * 3/16
                img_array[y + 1, x] += error * 5/16
                if x + 1 < width:
                    img_array[y + 1, x + 1] += error * 1/16
    
    # convert back to PIL image
    binary_image = Image.fromarray(np.uint8(img_array)).convert('1')
    return binary_image


def convert_to_ereader_bmp(input_path, output_path=None):
    """
    main conversion function
    takes image and makes it into 1-bit BMP
    """
    # try to load the image
    try:
        img = Image.open(input_path)
    except Exception as e:
        print(f"Error loading image: {e}")
        return
    
    # convert to grayscale first if its not already
    if img.mode != 'L':
        img = img.convert('L')
    
    # resize to target dimensions
    # Change the size here for other devices, this is mainly for Xteink-X4
    target_width = 148
    target_height = 226
    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # apply the dithering
    dithered_img = floyd_steinberg_dither(img)
    
    # figure out output filename
    if output_path is None:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}_dithered.bmp"
    
    # save as BMP
    dithered_img.save(output_path, 'BMP')
    
    # print info
    width, height = dithered_img.size
    file_size = os.path.getsize(output_path)
    
    print(f"✓ Converted: {output_path}")
    print(f"  {width}x{height} | {file_size:,} bytes ({file_size/1024:.2f} KB) | 1-bit BMP")


def main():
    """main function"""
    if len(sys.argv) < 2:
        print("Usage: python ereader_dither.py <input_image>")
        print("Output: 148x226 pixels, 1-bit BMP with Floyd-Steinberg dithering")
        return
    
    input_path = sys.argv[1]
    
    # check if file exists
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        return
    
    # just do the conversion
    convert_to_ereader_bmp(input_path)


if __name__ == "__main__":
    main()