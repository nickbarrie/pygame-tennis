import socket
import pickle

class NetworkManager:
    def __init__(self, port=5555, ip=""):
        self.port = port
        self.ip = ip
        self.client = None
        self.server_process = None
        self.player_id = 0  # Player's ID (0 or 1 for multiplayer)

    def set_port(self, port):
        self.port = int(port)

    def set_ip(self, ip):
        self.ip = ip

    def host_game(self):
        # Start the server as a subprocess
        import subprocess
        self.server_process = subprocess.Popen(["python", "server.py", str(self.port)])

    def stop_server(self):
        # Terminate the server subprocess
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()

    def connect_to_server(self, game_state):
        """ Connect to the multiplayer server """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = self.ip
        if game_state == "HOST":
            ip = socket.gethostbyname(socket.gethostname())  # Get local IP if hosting

        print(f"Connecting to {ip}:{self.port}")
        self.client.connect((ip, int(self.port)))  # Connect to the server
        self.player_id = pickle.loads(self.client.recv(2048))  # Receive player ID from the server
        print(f"Connected to the server as player {self.player_id}")
        return self.player_id

    def send_player_data(self, player_data):
        """ Send player data to the server """
        self.client.sendall(pickle.dumps(player_data))

    def receive_game_state(self):
        """ Receive the updated game state from the server """
        data = b""
        while True:
            part = self.client.recv(2048)
            data += part
            if len(part) < 2048:
                break  # Break if the last packet is smaller than the buffer size
        try:
            return pickle.loads(data)
        except Exception as e:
            print(f"Error receiving game state: {e}")
            return None
