from tkinter import messagebox, filedialog


class BasicTextHide:
    def __init__(self, message_path: str, carrier_text_path):
        # Calculate how many word can be hidden based on the carrier text length
        self.word_count = self.get_carrier_word_count(carrier_text_path)
        self.max_insertable_words = int(self.word_count / 6)  # Assuming 2 bits per word
        print(f"Maximum insertable words: {self.max_insertable_words}")

        # Check if the message fits within the carrier text
        if len(message_path) > self.word_count:
            messagebox.showerror('Error', 'Message is too long. Reduce message size!')
        else:
            self.encode_text(message_path, carrier_text_path)

    @staticmethod
    def get_carrier_word_count(carrier_text_path):
        # Count the number of words in the carrier text file
        word_count = 0
        with open(carrier_text_path, 'r') as carrier_file:
            for line in carrier_file:
                word_count += len(line.split())
        return word_count

    def encode_text(self, message_path, carrier_text_path):
        # Encode text message into bits
        encoded_data = self._encode_message(message_path)

        save_path = filedialog.asksaveasfilename(defaultextension='.txt')

        # Embed the encoded data into the carrier text and save the result
        with open(carrier_text_path, 'r+') as carrier_file, \
             open(save_path, 'w+', encoding='utf-8') as encoded_file:
            self._embed_data_in_carrier(encoded_data, carrier_file, encoded_file)

        messagebox.showinfo('Success', 'Text has been encoded successfully!')

    @staticmethod
    def _encode_message(message):
        # Convert message into bits, add prefixes, apply XOR, and add end marker
        encoded_bits = ''

        for char in message:
            char_code = ord(char)
            if 32 <= char_code <= 64:
                prefix = '0011'  # Prefix for symbol range
                char_code += 48
            else:
                prefix = '0110'  # Prefix for number range
                char_code -= 48

            char_code ^= 170  # XOR with key
            encoded_bits += prefix + bin(char_code)[2:].zfill(8)

        encoded_bits += '111111111111'  # End marker
        return encoded_bits

    @staticmethod
    def _embed_data_in_carrier(encoded_data, carrier_file, encoded_file):
        # Define zero-width characters for embedding data
        zero_width_chars = {
            "00": u'\u200C', "01": u'\u202C', "11": u'\u202D', "10": u'\u200E'
        }
        carrier_words = carrier_file.read().split()

        # Embed 2 bits of encoded data per word using zero-width characters
        index = 0
        for i in range(0, len(encoded_data), 12):  # Assuming 6 words can hold 12 bits
            word = carrier_words[index]
            for j in range(6):
                bit_pair = encoded_data[i + j*2: i + j*2 + 2]  # Extract 2 bits
                word += zero_width_chars[bit_pair]
            encoded_file.write(word + ' ')
            index += 1

        # Write remaining carrier text without changes
        encoded_file.write(' '.join(carrier_words[index:]))


class BasicTextReveal:
    def __init__(self, file_path: str):
        # Dictionary to reverse zero-width character mapping
        zwc_reverse = {u'\u200C': "00", u'\u202C': "01", u'\u202D': "11", u'\u200E': "10"}
        # Initialize temporary variable to store extracted binary data
        self.temp = ''
        self.final = ''
        with open(file_path, 'r', encoding='utf-8') as encoded_file:  # Open the file for reading
            for line in encoded_file:
                for words in line.split():
                    curr_word = words  # Store the current word in variable curr_word
                    binary_extract = ''  # Initialize a variable to store extracted binary data from the word
                    for letter in curr_word:
                        if letter in zwc_reverse:  # Check if the letter is a zero-width character
                            # If yes, append the corresponding binary value to binary_extract
                            binary_extract += zwc_reverse[letter]
                    if binary_extract == '111111111111':
                        break
                    else:
                        self.temp += binary_extract
        self.decode_text()

    def decode_text(self):
        temp = self.temp  # Work on a local copy for potential efficiency

        # Loop through the extracted binary data in chunks of 12 bits
        for i in range(0, len(temp), 12):
            control_code = temp[i:i + 4]  # Extract the control code (first 4 bits)
            data = temp[i + 4:i + 12]  # Extract the data (next 8 bits)

            if control_code == '0110':
                decimal_data = self.binary_to_decimal(data)
                self.final += chr((decimal_data ^ 170) + 48)
            elif control_code == '0011':
                decimal_data = self.binary_to_decimal(data)
                self.final += chr((decimal_data ^ 170) - 48)

    @staticmethod
    def binary_to_decimal(binary):
        return int(binary, 2)
