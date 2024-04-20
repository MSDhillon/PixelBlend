from Image.basicImage import *
from Image.advancedImage import *
from Text.basicText import *
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image
import os
import cv2
from cryptography.fernet import Fernet, InvalidToken


class Main:
    def __init__(self, root):
        self.filename = None
        self.root = root
        self.root.title("PixelBlend")
        self.root.geometry("500x460")
        self.root.resizable(False, False)

        tk.Label(self.root, text="PixelBlend", width='500', height='2', font=('', 40)).pack()
        tk.Label(self.root, text="Steganography", width='500', height='0', font=('', 20)).pack()
        tk.Label(self.root, text='').pack()

        tabview = ctk.CTkTabview(self.root)
        tabview.pack()
        tabview.configure(width=250, height=250)
        tabview.add('Hide')
        tabview.add('Reveal')

        # HIDE BUTTONS
        hide_image_button = ctk.CTkButton(tabview.tab('Hide'), command=self.hide_image)
        hide_image_button.configure(text='Image')
        hide_image_button.grid(row=0, column=0, padx=20, pady=20)

        hide_video_button = ctk.CTkButton(tabview.tab('Hide'), command=self.com_soon)
        hide_video_button.configure(text='Video')
        hide_video_button.grid(row=1, column=0, padx=20, pady=20)

        hide_text_button = ctk.CTkButton(tabview.tab('Hide'), command=self.hide_text)
        hide_text_button.configure(text='Text')
        hide_text_button.grid(row=0, column=1, padx=20, pady=20)

        hide_audio_button = ctk.CTkButton(tabview.tab('Hide'), command=self.com_soon)
        hide_audio_button.configure(text='Audio')
        hide_audio_button.grid(row=1, column=1, padx=20, pady=20)

        # REVEAL BUTTONS
        reveal_image_button = ctk.CTkButton(tabview.tab('Reveal'), command=self.reveal_image)
        reveal_image_button.configure(text='Image')
        reveal_image_button.grid(row=0, column=0, padx=20, pady=20)

        reveal_video_button = ctk.CTkButton(tabview.tab('Reveal'), command=self.com_soon)
        reveal_video_button.configure(text='Video')
        reveal_video_button.grid(row=1, column=0, padx=20, pady=20)

        reveal_text_button = ctk.CTkButton(tabview.tab('Reveal'), command=self.reveal_text)
        reveal_text_button.configure(text='Text')
        reveal_text_button.grid(row=0, column=1, padx=20, pady=20)

        reveal_audio_button = ctk.CTkButton(tabview.tab('Reveal'), command=self.com_soon)
        reveal_audio_button.configure(text='Audio')
        reveal_audio_button.grid(row=1, column=1, padx=20, pady=20)

    def hide_image(self):
        root = tk.Toplevel(self.root)
        root.title('Hide in Image')
        root.geometry('700x520')
        root.resizable(False, False)
        tk.Label(root, text='Hide Text in Image', font=('', 40)).pack()

        global label1
        frame1 = tk.Frame(root, width=250, height=220, border=5, bg='black')
        frame1.place(x=50, y=100)
        label1 = tk.Label(frame1, bg='black')
        label1.place(x=0, y=0, width=240, height=210)

        def on_entry_click(event):
            if text1.get("1.0", "end-1c") == "Type your secret message here...":
                text1.delete("1.0", "end")

        def on_focus_out(event):
            if not text1.get("1.0", "end-1c"):
                text1.insert("1.0", "Type your secret message here...")

        frame2 = tk.Frame(root, width=320, height=220, border=5, bg='black')
        frame2.place(x=330, y=100)
        text1 = tk.Text(frame2)
        text1.place(x=0, y=0, width=310, height=210)
        text1.insert('1.0', 'Type your secret message here...')

        text1.bind('<FocusIn>', on_entry_click)
        text1.bind('<FocusOut>', on_focus_out)

        tk.Label(root, text='Encryption Key (Only for Basic)').place(x=420, y=350)
        frame3 = tk.Frame(root, width=355, height=25, border=2, bg='white')
        frame3.place(x=50, y=350)
        text2 = tk.Text(frame3)
        text2.place(x=0, y=0, width=350, height=20)
        text2.config(state='disabled')

        def upload_image():
            global filename
            filename = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select Image', filetypes=[('PNG Files', '*.png'), ('JPG Files', '*.jpg'), ('JPEG Files', '*.jpeg')])
            self.filename = filename
            if filename:
                print("Selected image:", filename)
                image = Image.open(filename)
                width, height = frame1.winfo_width(), frame1.winfo_height()
                image = image.resize((width, height), Image.LANCZOS)
                self.image = ImageTk.PhotoImage(image)
                label1.config(image=self.image)
                label1.image = self.image

        def encode_image():
            selected_level = encoding_level.get()
            message = text1.get("1.0", "end-1c")
            if self.filename is None:
                messagebox.showerror("Error", "Please upload the carrier image first.")
                return
            if message == 'Type your secret message here...':
                messagebox.showerror("Error", "Please enter the text to be embedded in the carrier image.")
                return
            if len(message) == 0:
                messagebox.showerror("Error", "Please enter the text to be embedded in the carrier image.")
                return
            if selected_level == 'Basic':
                self.filename = None
                key = Fernet.generate_key()
                cipher_suite = Fernet(key)
                message = cipher_suite.encrypt(message.encode())

                basicEncoder = BasicImageHide(filename, message.decode())
                encoded_image = basicEncoder.encode()

                text2.config(state='normal')
                text2.delete('1.0', 'end')
                text2.insert('1.0', key.decode())
                text2.config(state='disabled')

                save_filename = filedialog.asksaveasfilename(defaultextension='.png',
                                                             filetypes=[('PNG Files', '*.png')])
                if save_filename:
                    encoded_image.save(save_filename)
            elif selected_level == 'Advanced':
                self.filename = None
                advancedEncoder = AdvancedImageHide(filename, message)
                encoded_image = advancedEncoder.encode_image()
                save_filename = filedialog.asksaveasfilename(defaultextension='.png',
                                                             filetypes=[('PNG Files', '*.png')])
                if save_filename:
                    cv2.imwrite(save_filename, encoded_image)
            else:
                pass

        upload_image = tk.Button(root, text='Upload Image', command=upload_image, cursor='hand2')
        upload_image.place(x=50, y=450)
        encode_image = tk.Button(root, text='Encode Image', command=encode_image, cursor='hand2')
        encode_image.place(x=530, y=450)

        options = ['Basic', 'Advanced']
        encoding_level = ctk.CTkComboBox(root, values=options)
        encoding_level.place(x=50, y=400)
        root.mainloop()

    def reveal_image(self):
        root = tk.Toplevel(self.root)
        root.title('Extract from Image')
        root.geometry('700x520')
        root.resizable(False, False)
        tk.Label(root, text='Extract Text from Image', font=('', 40)).pack()

        global label1
        frame1 = tk.Frame(root, width=250, height=220, border=5, bg='black')
        frame1.place(x=50, y=100)
        label1 = tk.Label(frame1, bg='black')
        label1.place(x=0, y=0, width=240, height=210)

        frame2 = tk.Frame(root, width=320, height=220, border=5, bg='white')
        frame2.place(x=330, y=100)
        text1 = tk.Text(frame2)
        text1.place(x=0, y=0, width=310, height=210)
        text1.config(state='disabled')

        tk.Label(root, text='Encryption Key (Only for Basic)').place(x=420, y=350)
        frame3 = tk.Frame(root, width=355, height=25, border=2, bg='white')
        frame3.place(x=50, y=350)
        text2 = tk.Text(frame3)
        text2.place(x=0, y=0, width=350, height=20)

        def upload_image():
            global filename, text1
            filename = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select Image',
                                                  filetypes=[('PNG Files', '*.png'), ('JPG Files', '*.jpg'),
                                                             ('JPEG Files', '*.jpeg')])
            self.filename = filename
            if filename:
                print("Selected image:", filename)
                image = Image.open(filename)
                width, height = frame1.winfo_width(), frame1.winfo_height()
                image = image.resize((width, height), Image.LANCZOS)
                self.image = ImageTk.PhotoImage(image)
                label1.config(image=self.image)
                label1.image = self.image

        def decode_image():
            text1.config(state='normal')
            selected_level = decoding_level.get()
            if self.filename is None:
                messagebox.showerror("Error", "Please upload the carrier image first.")
                return
            if selected_level == 'Basic':
                key = text2.get("1.0", "end-1c")
                if not key:
                    messagebox.showerror("Error", 'Please enter the key to decript the secret message.')
                    return
                if len(key) == 0:
                    messagebox.showerror("Error", "Please enter the key to decript the secret message.")
                    return
                self.filename = None
                cipher_suite = Fernet(key)
                basicDecoder = BasicImageReveal(filename)
                try:
                    decoded_message = basicDecoder.decode()
                    if decoded_message:
                        decoded_message = cipher_suite.decrypt(decoded_message.encode()).decode()
                        text1.delete("1.0", "end")
                        text1.insert('1.0', decoded_message)
                        text1.config(state='disabled')
                except InvalidToken and ValueError:
                    messagebox.showerror("Error", "Invalid token: The provided key is incorrect.")
            elif selected_level == 'Advanced':
                self.filename = None
                advancedDecoder = AdvancedImageReveal(filename)
                decoded_message = advancedDecoder.get_decoded_message()
                if decoded_message:
                    text1.delete("1.0", "end")
                    text1.insert('1.0', decoded_message)
            else:
                pass
            text1.config(state='disabled')


        upload_image = tk.Button(root, text='Upload Image', command=upload_image, cursor='hand2')
        upload_image.place(x=50, y=450)
        decode_image = tk.Button(root, text='Decode Image', command=decode_image, cursor='hand2')
        decode_image.place(x=530, y=450)

        options = ['Basic', 'Advanced']
        decoding_level = ctk.CTkComboBox(root, values=options)
        decoding_level.place(x=50, y=400)
        root.mainloop()

    def hide_text(self):
        root = tk.Toplevel(self.root)
        root.title('Hide in Text')
        root.geometry('700x520')
        root.resizable(False, False)
        tk.Label(root, text='Hide Text in Text', font=('', 40)).pack()

        global text1
        frame1 = tk.Frame(root, width=285, height=220, border=5, bg='black')
        frame1.place(x=50, y=100)
        text1 = tk.Text(frame1)
        text1.place(x=0, y=0, width=275, height=210)
        text1.config(state='disabled')

        def on_entry_click(event):
            if text2.get("1.0", "end-1c") == "Type your secret message here...":
                text2.delete("1.0", "end")

        def on_focus_out(event):
            if not text2.get("1.0", "end-1c"):
                text2.insert("1.0", "Type your secret message here...")

        frame2 = tk.Frame(root, width=285, height=220, border=5, bg='white')
        frame2.place(x=360, y=100)
        text2 = tk.Text(frame2)
        text2.place(x=0, y=0, width=275, height=210)
        text2.insert('1.0', 'Type your secret message here...')
        text2.bind('<FocusIn>', on_entry_click)
        text2.bind('<FocusOut>', on_focus_out)

        def upload_text():
            global filename
            filename = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select Text File', filetypes=[('TXT Files', '*.txt')])
            self.filename = filename
            if filename:
                if not filename.lower().endswith('.txt'):
                    messagebox.showerror("Error", "Invalid file type. Please select a .txt file!")
                    return
                with open(filename, 'r') as f:
                    contents = f.read()
                    text1.config(state='normal')
                    text1.delete(1.0, tk.END)
                    text1.insert(tk.END, contents)
                    text1.config(state='disabled')

        def encode_file():
            selected_level = encoding_level.get()
            message = text2.get("1.0", "end-1c").strip()
            if self.filename is None:
                messagebox.showerror("Error", "Please upload the carrier file first.")
                return
            if message == 'Type your secret message here...':
                messagebox.showerror("Error", "Please enter the text to be embedded in the carrier file.")
                return
            if len(message) == 0:
                messagebox.showerror("Error", "Please enter the text to be embedded in the carrier file.")
                return
            if selected_level == 'Basic':
                self.filename = None
                print(message)
                BasicTextHide(message, filename)
            elif selected_level == 'Advanced':
                self.filename = None
                messagebox.showinfo('Coming Soon', 'Advanced text encoding coming soon')
            else:
                pass

        upload_textfile = tk.Button(root, text='Upload File', command=upload_text, cursor='hand2')
        upload_textfile.place(x=50, y=450)
        encode_textfile = tk.Button(root, text='Encode File', command=encode_file, cursor='hand2')
        encode_textfile.place(x=530, y=450)

        options = ['Basic', 'Advanced']
        encoding_level = ctk.CTkComboBox(root, values=options)
        encoding_level.place(x=50, y=400)
        root.mainloop()

    def reveal_text(self):
        root = tk.Toplevel(self.root)
        root.title('Extract from Text')
        root.geometry('700x520')
        root.resizable(False, False)
        tk.Label(root, text='Extract Text from Text', font=('', 40)).pack()

        global text1
        frame1 = tk.Frame(root, width=285, height=220, border=5, bg='black')
        frame1.place(x=50, y=100)
        text1 = tk.Text(frame1)
        text1.place(x=0, y=0, width=275, height=210)

        global text2
        frame2 = tk.Frame(root, width=285, height=220, border=5, bg='white')
        frame2.place(x=360, y=100)
        text2 = tk.Text(frame2)
        text2.place(x=0, y=0, width=275, height=210)
        text2.config(state='disabled')

        def upload_text():
            global filename
            filename = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select Text File', filetypes=[('TXT Files', '*.txt')])
            self.filename = filename
            if filename:
                if not filename.lower().endswith('.txt'):
                    messagebox.showerror("Error", "Invalid file type. Please select a .txt file!")
                    return
                with open(filename, 'r') as f:
                    contents = f.read()
                    text1.config(state='normal')
                    text1.delete(1.0, tk.END)
                    text1.insert(tk.END, contents)
                    text1.config(state='disabled')

        def decode_file():
            text2.config(state='normal')
            selected_level = decoding_level.get()
            if self.filename is None:
                messagebox.showerror("Error", "Please upload the carrier file first.")
                return
            if selected_level == 'Basic':
                self.filename = None
                textrevealer = BasicTextReveal(filename)
                decoded_message = textrevealer.final
                text2.delete(1.0, tk.END)
                text2.insert(tk.END, decoded_message)
                text2.config(state='disabled')
            elif selected_level == 'Advanced':
                self.filename = None
                messagebox.showinfo('Coming Soon', 'Advanced text encoding coming soon')
            else:
                pass

        upload_textfile = tk.Button(root, text='Upload File', command=upload_text, cursor='hand2')
        upload_textfile.place(x=50, y=450)
        decode_textfile = tk.Button(root, text='Decode File', command=decode_file, cursor='hand2')
        decode_textfile.place(x=530, y=450)

        options = ['Basic', 'Advanced']
        decoding_level = ctk.CTkComboBox(root, values=options)
        decoding_level.place(x=50, y=400)
        root.mainloop()

    def com_soon(self):
        messagebox.showinfo('Coming Soon', 'Encoding format coming soon')

if __name__ == '__main__':
    root = tk.Tk()
    Main(root)
    root.mainloop()
