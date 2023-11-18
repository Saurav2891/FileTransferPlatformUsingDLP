import subprocess
import tkinter as tk
from tkinter import ttk
import time
import socket
import threading
import os
import re
import tqdm
import io
import sys
from time import sleep
import pickle
from fernet import Fernet
from pynput.keyboard import Key, Controller
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

def encrypt(filename, filename_encrpt, keys):
     f = Fernet(keys)
     with open(filename, "rb") as file:
         # read all file data
         file_data = file.read()
     # encrypt data
     encrypted_data = f.encrypt(file_data)
     # write the encrypted file
     with open(filename_encrpt, "wb") as file:
         file.write(encrypted_data)

input_text = "0"

class FileTransferGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Transfer")
        self.geometry("500x500")
        self.resizable(width=False, height=False)
        self.create_widgets()
        self.host = ''
        self.port = 49151
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # the SO_REUSEADDR flag tells the kernel to
        self.s.bind((self.host, self.port))
        self.halt_event = threading.Event()
        self.halt_var = tk.StringVar()
        
    def create_widgets(self):
        #Progress Bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress.grid(row=0, column=0, padx=10, pady=10, sticky="sw")
        # Start Button
        self.start_button = tk.Button(self, text="Start", command=self.listen, width=10, height=2, font=("Arial", 12))
        self.start_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Server Status Label
        self.server_status = tk.Label(self, text="Server is not running", fg="red", font=("Arial", 12))
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
        
    def listen(self):
        # Start Server Code
        self.server_status.config(text="Server is running", fg="green")
        self.output_text.insert(tk.END, "Server started\n")
        self.s.listen(5)  #max 5 client connections r allowed
        threading.Thread(target=self.listen_thread).start()

    def listen_thread(self):
        while True:
            c, addr = self.s.accept()
            c.settimeout(60)
            threading.Thread(target=self.listenToClient, args=(c, addr)).start()

    def listenToClient(self, c, addr):
        print('\nServer> Client Requested :', addr)
        self.output_text.insert(tk.END, '\nServer> Client Requested :' + str(addr))
        c.send("\nEnter the password :".encode("ascii"))
        pswd=c.recv(1024).decode('ascii')
        if pswd != "pswrd123":
                print("Server> Password entered by the client is incorrect!!")
                self.output_text.insert(tk.END, '\nServer> Password entered by the client is incorrect!!')
                c.send("False".encode("ascii"))
                
        else:
                print("Password is correct !! Connection established with the client")
                self.output_text.insert(tk.END, '\nPassword is correct !! Connection established with the client')
                c.send("True".encode("ascii"))
            
                list1=[]
                data = c.recv(1024)
            
                if data.decode() == "download":
                    FileFound = 0   
            
                    print(os.listdir("./"))  # Shows all the files at server side
                    self.output_text.insert(tk.END, '\nServer> Files in the Server :\n' + str(os.listdir("./")))
                    list1=os.listdir("./")
                    data=pickle.dumps(list1)
                    c.send(data)
                    
                    FileName = c.recv(1024)
                    print("\nServer> Client wants to download :",FileName)
                    self.output_text.insert(tk.END, '\nServer> Client wants to download :' + str(FileName))
                    print("Server> Checking the list of files ...")
                    self.output_text.insert(tk.END, '\nServer> Checking the list of files ...')
                    for file in os.listdir("./"):
                        
                        if file == FileName.decode():
                            
                            FileFound = 1
                            break
            
                    if FileFound == 0:
                        print("Server> File Not Found in the Server!!")
                        self.output_text.insert(tk.END, '\nServer> File Not Found in the Server!!')
            
                    else:
                        print("Server> File Found in the Server!!")
                        self.output_text.insert(tk.END, '\nServer> File Found in the Server!!')
                        file_name = FileName.decode()
                        upfile = FileName.decode()
                        # file_size = os.path.getsize(upfile)
                        file_size = os.path.getsize(os.path.join(os.getcwd(), upfile))
                        SEPARATOR="|"
                        gen_key = Fernet.generate_key()
                
                        with open("key.key", "wb") as key_file:
                            key_file.write(gen_key)
                    
                        file_name1 = "key.key"
                        # file_size1 = os.path.getsize(file_name1)
                        file_size1 = os.path.getsize(os.path.join(os.getcwd(), file_name1))
                
                        c.send(f"{file_name1}{SEPARATOR}{file_size1}{SEPARATOR}{file_size}".encode('ascii'))
                        with open(file_name1, "rb") as f: ##sending the key file
                            bytes_read = f.read()

                            if bytes_read:
                                c.sendall(bytes_read)
                        f.close()
                        key = open("key.key", "rb").read()
                
                        file_name_encrypt = "encrypt_" + file_name
                        print("Encrypting and sending!!!")
                        self.output_text.insert(tk.END, '\nEncrypting and sending!!!')
                        print("Please wait for few seconds.")
                        self.output_text.insert(tk.END, '\nPlease wait for few seconds.')
                        # size = os.path.getsize('key.key')
                        size = os.path.getsize(os.path.join(os.getcwd(), 'key.key'))
                        encrypt(file_name, file_name_encrypt, key)
                        progress = tqdm.tqdm(range(file_size), f"Sending {upfile}", unit="B", unit_scale=True,
                                      unit_divisor=1024)
                        self.progress.configure(maximum=file_size)
                        

                        UploadFile = open("./" + file_name_encrypt, "rb")
                        
                        for _ in progress:
                            Read = UploadFile.read(1024)
                            while Read:
                                c.send(Read)      # sends 1KB
                                Read = UploadFile.read(1024)
                           # update the progress bar
                            progress.update(len(Read))
                        
                        for i in progress:
                            time.sleep(0.01)
                            self.progress_value = i
                            self.progress['value'] = i+1
                            self.progress.update()
                            self.progress_msg = f"\nSending file: {i/file_size:.0%} {i+1:.1f}/{file_size:.1f} bytes"
                            self.output_text.insert(tk.END, self.progress_msg+'\n')
                            self.output_text.yview(tk.END)
                            self.update()
                        
                        if "{i/file_size:.0%}" != "100%" :
                            final_progress_msg = f"\nSending file: 100% {file_size:.1f}/{file_size:.1f} bytes"
                            self.output_text.insert(tk.END, final_progress_msg+'\n')
                            self.output_text.yview(tk.END)
                            self.update()
                    
                        print("\nServer> File Sent Successfully!!")
                        self.output_text.insert(tk.END, '\nServer> File Sent Successfully!!')
                        UploadFile.close()
                        c.close()
         
                
                elif data.decode() == "upload":
                            FileName = c.recv(1024)
                            
                            print("Server> Client wants to upload :",FileName)
                            self.output_text.insert(tk.END, '\nServer> Client wants to upload :' + str(FileName))
                            downfile = FileName.decode()
                
                            while True:
                                # self.output_text.insert(tk.END, '\nServer> Enter the number of bytes to be sent: ')
                                self.halt_event.clear()
                                while not self.halt_event.is_set():
                                    self.output_text.insert(tk.END, '\nServer> Enter the number of bytes to be sent: ')
                                    self.update()  # Update the GUI to show the prompt
                                    self.wait_variable(self.halt_var)  # Wait for input
                                no = self.halt_var.get()
                                self.output_text.insert(tk.END, f"{input_text}\n")
                                
                                c.send(no.encode())
                                res = c.recv(1024)
                                if res.decode() == "OK":
                                    c.send("OK".encode())
                                    break
                                c.send("NO".encode())
                
                            deli = int(c.recv(1024))
                
                            no = int(no)
                
                            DownloadFile = open(downfile, "wb")
                            Data = c.recv(no) 
                            i = 1
                            li = []
                            print("Server> Receiving File...")
                            self.output_text.insert(tk.END, '\nServer> Receiving File...')
                            while Data:
                                li.append(Data)
                                Data = c.recv(no)
                                i = i + 1
                
                            dict = {}
                            for i in li:
                                try:
                                    x = re.match(b"(.*)&/-(.*)", i)
                                    id = int(x.group(1).decode(encoding="utf-8"))
                                    data = i[deli:]
                                    dict[id] = data
                                except:
                                    print(i, "Error")
                                    self.output_text.insert(tk.END, '\n' + str(i) + 'Error')
                
                            keys = list(dict.keys())
                            keys.sort()
                
                            for k in keys:
                                DownloadFile.write(dict[k])
                
                            print("Server> File Received Successfully!!")
                            self.output_text.insert(tk.END, '\nServer> File Received Successfully!!')
                            DownloadFile.close()
                            c.close()
        
    def submit_input(self):
        # Submit Input Code
        global input_text
        input_text = self.input_box.get()
        self.halt_var.set(input_text)
        self.halt_event.set()
        # self.no1 = input_text
        self.input_box.delete(0, tk.END)

if __name__ == "__main__":
    app = FileTransferGUI()
    app.mainloop()
