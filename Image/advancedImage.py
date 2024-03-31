from tkinter import messagebox
import cv2
import numpy as np
import pywt


# Function to convert a message to its binary representation
def convert_message_to_bits(message):
    return [int(b) for char in message for b in f'{ord(char):08b}']


# Function to convert binary representation back to the original message
def convert_bits_to_message(bits):
    bits_str = ''.join(map(str, bits))
    bytes_list = [int(bits_str[i:i + 8], 2) for i in range(0, len(bits_str), 8)]
    return ''.join(map(chr, bytes_list))


# Function to convert an integer value to its binary representation
def convert_int_to_bits(int_value):
    bin_str = format(int_value, "08b")
    return [int(bit) for bit in bin_str]


# Function to convert binary representation back to an integer value
def convert_bits_to_int(bits):
    result = 0
    for bit in bits:
        result = (result << 1) | bit
    return result


# Function to determine the least significant bit difference between two values
def lsb(a, b):
    if a == b:
        return 0
    elif a == 1 and b == 0:
        return 2
    else:
        return -2


# Class for hiding a message within an image
class AdvancedImageHide:
    def __init__(self, image_path: str, message: str):
        self.image = cv2.imread(image_path)
        self.message = message + '#'  # Append '#' to mark the end of the message
        self.message_bits = convert_message_to_bits(self.message)
        self.message_bits_len = len(self.message_bits)
        self.index = 0

    # Encode the message into the image using wavelet transform
    def encode_image(self):
        b, g, r = cv2.split(self.image)
        red_coeff = pywt.dwt2(r, 'haar')
        green_coeff = pywt.dwt2(g, 'haar')
        blue_coeff = pywt.dwt2(b, 'haar')

        encoded_red, encoded_green, encoded_blue = self.encode_channels(red_coeff, green_coeff, blue_coeff)

        idwt_red = self.inverse_wavelet_transform(encoded_red)
        idwt_green = self.inverse_wavelet_transform(encoded_green)
        idwt_blue = self.inverse_wavelet_transform(encoded_blue)

        encoded_image = cv2.merge((idwt_blue, idwt_green, idwt_red))
        messagebox.showinfo('Success', 'Text has been encoded successfully!')
        return encoded_image

    # Encode the message into individual color channels using LSB substitution
    def encode_channels(self, red_coeff, green_coeff, blue_coeff):
        approx_coeff_red, (c_h_red, c_v_red, c_d_red) = red_coeff
        approx_coeff_green, (c_h_green, c_v_green, c_d_green) = green_coeff
        approx_coeff_blue, (c_h_blue, c_v_blue, c_d_blue) = blue_coeff

        encoded_red_ca = approx_coeff_red.copy()
        encoded_green_ca = approx_coeff_green.copy()
        encoded_blue_ca = approx_coeff_blue.copy()

        for i in range(len(approx_coeff_red)):
            for j in range(len(approx_coeff_red)):
                if self.index < self.message_bits_len:
                    encoded_red_ca[i, j] = self.encode_pixel(approx_coeff_red[i, j], self.message_bits[self.index])
                    self.index += 1
                if self.index < self.message_bits_len:
                    encoded_green_ca[i, j] = self.encode_pixel(approx_coeff_green[i, j], self.message_bits[self.index])
                    self.index += 1
                if self.index < self.message_bits_len:
                    encoded_blue_ca[i, j] = self.encode_pixel(approx_coeff_blue[i, j], self.message_bits[self.index])
                    self.index += 1

        return (encoded_red_ca, (c_h_red, c_v_red, c_d_red)), (encoded_green_ca, (c_h_green, c_v_green, c_d_green)), (
            encoded_blue_ca, (c_h_blue, c_v_blue, c_d_blue))

    # Encode a single pixel value with the least significant bit of the message
    @staticmethod
    def encode_pixel(pixel_value, bit_to_encode):
        pixel = convert_int_to_bits(int(pixel_value))[-2]
        return pixel_value + lsb(bit_to_encode, pixel)

    # Inverse wavelet transform to reconstruct the encoded image
    @staticmethod
    def inverse_wavelet_transform(encoded_coeff):
        modified_coeff, (coeffH, coeffV, coeffD) = encoded_coeff
        return np.uint8(pywt.idwt2((modified_coeff, (coeffH, coeffV, coeffD)), 'haar'))


# Class for revealing a hidden message from an image
class AdvancedImageReveal:
    def __init__(self, image_path: str):
        self.image = cv2.imread(image_path)
        self.cAs = self.extract_approximation_coefficients()
        self.bit_sequence = self.extract_bit_sequence()

    # Extract approximation coefficients from the image using wavelet transform
    def extract_approximation_coefficients(self):
        b, g, r = cv2.split(self.image)
        coeffs = (
            pywt.dwt2(r, 'haar'),
            pywt.dwt2(g, 'haar'),
            pywt.dwt2(b, 'haar')
        )
        return [coeff[0] for coeff in coeffs]

    # Extract the bit sequence hidden in the approximation coefficients
    def extract_bit_sequence(self):
        bit_sequence = []
        for i in range(len(self.cAs[0])):
            for j in range(len(self.cAs[0])):
                for cA in self.cAs:
                    bits = convert_int_to_bits(int(cA[i, j]))
                    if len(bits) > 2:
                        bit_sequence.append(bits[-2])
        return bit_sequence

    # Decode the hidden message from the bit sequence
    def decode_message(self):
        decoded_msg = convert_bits_to_message(self.bit_sequence)
        split_index = decoded_msg.find('#')
        if split_index != -1:
            decoded_msg = decoded_msg[:split_index]
        return decoded_msg

    # Get the decoded message
    def get_decoded_message(self):
        return self.decode_message()
