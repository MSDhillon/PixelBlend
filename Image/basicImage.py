from tkinter import messagebox
from PIL import Image
from typing import IO, Union, List

ENCODINGS = {"UTF-8": 8, "UTF-32LE": 32}


# Function to handle versatile image opening
def open_image(path: Union[str, IO[bytes]]) -> Image.Image:
    try:
        if isinstance(path, Image.Image):  # Check if the image is already an Image object
            return path
        return Image.open(path)  # Open from file path
    except FileNotFoundError:
        print(f"Could not open {path}")
        exit()


# Function to convert text characters to their binary equivalent
def convert_to_bits(chars: str, encoding: str = "UTF-8") -> List[str]:
    return [bin(ord(x))[2:].rjust(ENCODINGS[encoding], "0") for x in chars]


# Function to manipulate the least significant bit of a colour component
def set_lsb(component: int, bit: str) -> int:
    return component & ~1 | int(bit)  # Clear LSB and set it to the input bit


class BasicImageHide:
    def __init__(
            self,
            image: Union[str, IO[bytes], Image.Image],
            message: str,
            encoding: str = "UTF-8"
    ):
        self.index = 0  # Index to track bits embedded in the message
        self.image = image
        self.message = message
        self.message_length = len(self.message)
        self.encoding = encoding
        self.message_bits_len = ''
        self.message_bits = ''
        assert self.message_length != 0, "Message length cannot be 0"
        self.carrier_image = None

    def encode(self):
        self.open_image()
        self.prepare_message()
        image = self.embed_message()
        messagebox.showinfo('Success', 'Text has been encoded successfully!')
        return image

    def open_image(self):
        # Open the image (or handle if already an Image object)
        if isinstance(self.image, str):
            with open_image(self.image) as carrier_image:
                # Ensure image is in RGB format for consistent colour manipulation
                if carrier_image not in ['RGB', 'RGBA']:
                    try:
                        carrier_image = carrier_image.convert('RGB')
                    except Exception:
                        raise Exception("Invalid image format")
                self.carrier_image = carrier_image.copy()  # Work on a copy
        elif isinstance(self.image, Image.Image):
            if self.image not in ['RGB', 'RGBA']:
                try:
                    self.image = self.image.convert('RGB')
                except Exception:
                    raise Exception("Invalid image format")
            self.carrier_image = self.image.copy()  # Work on a copy
        else:
            raise ValueError("Invalid image format. Provide image filepath or PIL Image object.")

    def prepare_message(self):
        # Prepare message for embedding (include length prefix)
        message = str(self.message_length) + ':' + str(self.message)
        self.message_bits = ''.join(convert_to_bits(message, self.encoding))
        # Add padding bits to make the message length divisible by 3
        self.message_bits += '0' * ((3 - (len(self.message_bits) % 3)) % 3)

    def embed_message(self):
        # Image capacity check
        width, height = self.carrier_image.size
        pixels = width * height
        self.message_bits_len = len(self.message_bits)

        if self.message_bits_len > pixels * 3:
            raise Exception("Message length exceeds image")

        # Embed the message bits into image pixels
        generator = iter(range(pixels))
        loop = True
        while loop:
            if self.index + 3 <= self.message_bits_len:
                generated_number = next(generator)
                col = generated_number % width
                row = int(generated_number / width)
                self.encode_pixel((col, row))
            else:
                loop = False

        return self.carrier_image

    def encode_pixel(self, coordinate: tuple[int, int]):
        # Extract pixel colour components
        r, g, b, *a = self.carrier_image.getpixel(coordinate)

        # Embed bits into the LSBs of colour components
        r = set_lsb(r, self.message_bits[self.index])
        g = set_lsb(g, self.message_bits[self.index + 1])
        b = set_lsb(b, self.message_bits[self.index + 2])
        # Update the pixel with modified colour values
        if self.carrier_image.mode == 'RGBA':
            self.carrier_image.putpixel(coordinate, (r, g, b, *a))
        else:
            self.carrier_image.putpixel(coordinate, (r, g, b))

        self.index += 3  # Move to the next 3 bits in the message


class BasicImageReveal:
    def __init__(
            self,
            image: Union[str, IO[bytes]],
            encoding: str = 'UTF-8',
    ):
        # Determine the bit length per character based on encoding
        self.encoding_length = ENCODINGS[encoding]
        self.image = image
        # Initialise variables for decoding process
        self.buff, self.count = 0, 0  # Buffer to assemble characters, a bit counter
        self.bitab: List[str] = []  # Accumulated binary characters
        self.limit: Union[None, int] = None  # Message length (decoded dynamically)
        self.message = ''  # Extracted message

    def decode(self):
        # Open the image
        with open_image(self.image) as carrier_image:
            width, height = carrier_image.size
            tot_pixels = width * height

            generator = iter(range(tot_pixels))  # Create a generator for pixel iteration

            for _ in range(tot_pixels):  # Iterate over each pixel
                generated_number = next(generator)
                col = generated_number % width
                row = int(generated_number / width)

                if self.decode_pixel((col, row), carrier_image):
                    break  # Stop when the message is fully decoded
        return self.message

    def decode_pixel(self, coordinate: tuple, image):
        pixel = image.getpixel(coordinate)

        if image.mode == 'RGBA':
            pixel = pixel[:3]  # Ignore the alpha channel if present

        # Extract bits from each colour channel
        for colour in pixel:
            self.buff += (colour & 1) << (self.encoding_length - 1 - self.count)
            self.count += 1

            if self.count == self.encoding_length:
                self.bitab.append(chr(self.buff))  # Add decoded character to the list
                self.buff, self.count = 0, 0  # Reset buffer and count

                # Check if the message length has been found
                if self.bitab[-1] == ':' and self.limit is None:
                    if ''.join(self.bitab[:-1]).isdigit():
                        self.limit = int(''.join(self.bitab[:-1]))
                    else:
                        raise IndexError('Cannot decode')

        # Check if the entire message has been decoded
        if len(self.bitab) - len(str(self.limit)) - 1 == self.limit:
            self.message = ''.join(self.bitab)[len(str(self.limit)) + 1:]
            return True  # Signal that the message is complete
        else:
            return False
