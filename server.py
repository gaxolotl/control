import socket
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Remote Control Server")

        # GUI elements
        self.log_text = ScrolledText(root, state='disabled', height=20, width=70)
        self.log_text.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.command_entry = tk.Entry(root, width=50)
        self.command_entry.grid(row=1, column=0, padx=10, pady=5)

        self.send_button = tk.Button(root, text="Send Command", command=self.send_command)
        self.send_button.grid(row=1, column=1, padx=10, pady=5)

        # Network components
        self.server_socket = None
        self.client_socket = None
        self.client_address = None
        self.is_running = False

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.yview(tk.END)
        self.log_text.config(state='disabled')

    def send_command(self):
        if self.client_socket:
            command = self.command_entry.get()
            if command.strip():
                try:
                    self.client_socket.send(command.encode())
                    if command.lower() == "exit":
                        self.log_message("[INFO] Closing connection with client.")
                        self.client_socket.close()
                        self.client_socket = None
                        return
                    self.log_message(f"[SERVER] Sent: {command}")
                except Exception as e:
                    self.log_message(f"[ERROR] Failed to send command: {e}")
            self.command_entry.delete(0, tk.END)

    def handle_client(self):
        try:
            self.log_message(f"[NEW CONNECTION] Connected to {self.client_address}")
            while True:
                response = self.client_socket.recv(4096).decode()
                if not response:
                    break
                self.log_message(f"[CLIENT] {response}")
        except Exception as e:
            self.log_message(f"[ERROR] Connection lost: {e}")
        finally:
            self.client_socket.close()
            self.client_socket = None
            self.log_message("[INFO] Client disconnected.")

    def start_server(self):
        self.is_running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", 9999))
        self.server_socket.listen(1)
        self.log_message("[LISTENING] Server started on 0.0.0.0:9999")

        while self.is_running:
            try:
                self.client_socket, self.client_address = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, daemon=True)
                client_thread.start()
            except Exception as e:
                self.log_message(f"[ERROR] Server error: {e}")

    def start(self):
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        server_thread.start()

    def stop(self):
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    app.start()
    root.mainloop()
