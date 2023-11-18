import socket
import threading
from tqdm import tqdm
import math
from time import sleep
from concurrent.futures import ThreadPoolExecutor
import os
from fernet import Fernet
import pickle
import warnings
import tkinter as tk
from tkinter import ttk
import time
import re
import sys
import tqdm
import pickle
warnings.filterwarnings("ignore", category=FutureWarning)

input_text = "0"


class FileTransferGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Transfer")
        self.geometry("500x500")
        self.resizable(width=False, height=False)
        self.create_widgets()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object
        self.host = socket.gethostname()  # Get local machine name
        self.port = 49157  # Reserve a port for your service.
        self.halt_event = threading.Event()
        self.halt_var = tk.StringVar()
        
    def create_widgets(self):
        #Progress Bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress.grid(row=0, column=0, padx=10, pady=10, sticky="sw")

        # Connect Button
        self.connect_button = tk.Button(self, text="Connect", command=self.connect_to_server, width=10, height=2, font=("Arial", 12))
        self.connect_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.server_status = tk.Label(self, text="Client2 Not Active", fg="red", font=("Arial", 12))
        self.server_status.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        # Output Message Box
        self.output_text = tk.Text(self, height=22, width=59, wrap="word")
        self.output_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        scrollbar = tk.Scrollbar(self, command=self.output_text.yview)
        scrollbar.grid(row=1, column=1, sticky="nes")

        self.output_text.config(yscrollcommand=scrollbar.set)
        
        # Input Box and Submit Button
        self.input_box = tk.Entry(self, width=60)
        self.input_box.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        
        self.submit_button = tk.Button(self, text="Submit", command=self.submit_input, width=8, height=1, font=("Arial", 12))
        self.submit_button.grid(row=2, column=1, padx=10, pady=10)
    
    def submit_input(self):
        # Submit Input Code
        global input_text
        input_text = self.input_box.get()
        self.halt_var.set(input_text)
        self.halt_event.set()
        # self.no1 = input_text
        self.input_box.delete(0, tk.END)
        
    def connect_to_server(self):
        self.server_status.config(text="Client2 is Active", fg="green")
        self.s.connect((self.host, 49151))
        password = self.s.recv(1024).decode("ascii")
        self.halt_event.clear()
        while not self.halt_event.is_set():
            self.output_text.insert(tk.END, password)
            self.update()  # Update the GUI to show the prompt
            self.wait_variable(self.halt_var)
        msg = self.halt_var.get()
        self.output_text.insert(tk.END, msg)
        self.s.send(msg.encode("ascii"))
        msg1=self.s.recv(1024).decode("ascii")
        
        if(msg1 == "False"):
            print("Password is incorrect !! Try again later")
            self.output_text.insert(tk.END, "\nPassword is incorrect !! Try again later")
        else:
            print("Connection established successfully with server!!...")
            self.output_text.insert(tk.END, "\nConnection established successfully with server!!...")
            def sendData(file):
                self.s.send(file)
                
            print("\nWhat do you want from the server")
            self.output_text.insert(tk.END, "\nWhat do you want from the server")
            self.halt_event.clear()
            while not self.halt_event.is_set():
                self.output_text.insert(tk.END, "\n1.Download File\n2.Upload File\nEnter an option:")
                self.update()  # Update the GUI to show the prompt
                self.wait_variable(self.halt_var)

            Answer = self.halt_var.get()
            self.output_text.insert(tk.END, Answer)
            print(Answer)
                
            if Answer == "1":
                
                mssg = "download"
                self.s.send(mssg.encode())
                data=self.s.recv(1024)
                print(pickle.loads(data))
                download_data = pickle.loads(data)
                self.output_text.insert(tk.END, "\n")
                download_text = ' '.join(download_data)
                self.output_text.insert(tk.END, download_text + "\n")
                self.halt_event.clear()
                while not self.halt_event.is_set():
                    self.output_text.insert(tk.END, "\nEnter Filename to Download from server : ")
                    self.update()  # Update the GUI to show the prompt
                    self.wait_variable(self.halt_var)
                FileName = self.halt_var.get()
                self.output_text.insert(tk.END, FileName)
                Data = "Temp"
                # flag=False
                
                self.s.send(FileName.encode())
                SEPARATOR="|"
                details = self.s.recv(1024).decode('ascii')
                file_n, file_s, file_size = details.split(SEPARATOR)
                file_s = int(file_s)
                file_size = int(file_size)
        
                with open("t_" + file_n, "wb") as fw:
                    byte_read = self.s.recv(file_s)
                    fw.write(byte_read)

                keys = open("t_key.key", "rb").read()
                with open(FileName, "wb") as f:
                    while True:
                # read 1024 bytes from the socket (receive)
                        bytes_read = self.s.recv(1024)
                        if not bytes_read:
                            print("\nFile recieved sent for decrypting.....")
                            self.output_text.insert(tk.END, "\nFile recieved sent for decrypting.....")
                            self.s.close()
                            f.close()
                            self.decrypt(FileName, keys)
                            break
                        f.write(bytes_read)
                    f.close()
                
            elif Answer == "2":
                mssg = "upload"
                self.s.send(mssg.encode())
                print(os.listdir("./"))
                self.output_text.insert(tk.END, '\n Client2> Files in the System :\n' + str(os.listdir("./")))
                self.halt_event.clear()
                self.update() # Update the GUI to show the prompt
                while not self.halt_event.is_set():
                    self.output_text.insert(tk.END, "\nEnter Filename to Upload On server : ")
                    self.update()  # Update the GUI to show the prompt
                    self.wait_variable(self.halt_var)
                FileName = self.halt_var.get()
                self.output_text.insert(tk.END, "\n" + FileName + " is selected to upload.")
                self.s.send(FileName.encode())
                # flag=False
                
                while True:
                    no = int(self.s.recv(1024).decode())
                    print(no, " Bytes is to be sent.")
                    self.output_text.insert(tk.END, "\n" + str(no) + " Bytes is to be sent.")
                    self.halt_event.clear()
                    while not self.halt_event.is_set():
                        self.output_text.insert(tk.END, "\nEnter 'OK' if okay else enter 'NO':")
                        self.update()  # Update the GUI to show the prompt
                        self.wait_variable(self.halt_var)
                    res = self.halt_var.get()
                    self.s.send(res.encode())
                    resp = self.s.recv(1024)
                    if resp.decode() == "OK":
                        break
                
                dataList = []
                UploadFile = open("./" + FileName, "rb")
                Read = UploadFile.read()
                x = math.ceil(sys.getsizeof(Read) / (no-10))
                
                ones, twos, threes, fours = "", "", "", ""
                deli = 0
                if x < 100:
                    ones = str(0)
                    twos = ""
                    deli = 5
                    self.s.send("5".encode())
                elif x < 1000:
                    ones = str(00)
                    twos = str(0)
                    threes = ""
                    deli = 6
                    self.s.send("6".encode())
                elif x < 10000:
                    ones = str(000)
                    twos = str(00)
                    threes = str(0)
                    fours = ""
                    deli = 7
                    self.s.send("7".encode())
                
                Read = UploadFile.read(no-deli)
                i = 1
                while Read:
                    string = ""
                    if i < 10:
                        string = ones + "%d&/-" % i
                    elif 10 <= i < 100:
                        string = twos + "%d&/-" % i
                    elif 100 <= i < 1000:
                        string = threes + "%d&/-" % i
                    elif 1000 <= i < 10000:
                        string = fours + "%d&/-" % i
                    by = bytes(string, 'utf-8')
                    dataList.append(by + Read)
                    Read = UploadFile.read(no-deli)
                    i += 1
                    break
                
                executor = ThreadPoolExecutor(8)
                print("Sending...")
                self.output_text.insert(tk.END, "\nSending...")
                # print(type(tqdm))
                tqdm.tqdm(executor.map(sendData, dataList))
                sleep(2)
                print("Done Sending")
                self.progress["value"] = self.progress["maximum"]
                self.output_text.insert(tk.END, "\nDone Sending")
                UploadFile.close()
            self.s.close()
            # sys.exit()     

    def decrypt(self, filename, key):
        print("Decrypting...")
        self.output_text.insert(tk.END, "\nDecrypting...")
        f = Fernet(key)
        with open(filename, "rb") as fr:
            # read the encrypted data
            encrypted_data = fr.read()
        # decrypt data
        decrypted_data = f.decrypt(encrypted_data)
        # write the original file
        with open(filename, "wb") as fl:
            fl.write(decrypted_data)

        print("Finished")
        self.output_text.insert(tk.END, "\nFinished")
        self.update()  # Update the GUI
        time.sleep(2)
        sys.exit()
if __name__ == "__main__":
    app = FileTransferGUI()
    app.mainloop()
