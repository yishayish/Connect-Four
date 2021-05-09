"""
start game:
{"new game":True} -> {"new game": True, "id": <>, "opponent": <> "first": <True, False>}, {"new game": <False>}

make move:
{"id": <>, "column" <0..6>} -> {"move": <True, False>, "row": <0..5>, "column" <0..6>, "win": <True,False>}

opponent move:
-> {"row": <0..5>, "column" <0..6>, "win": <True,False>}
-> {"quit": True}

"""
import random
import socket
from threading import Thread, Lock
from game import ConnectDotsGame
from utils import threaded
import Engine

from pyngrok import ngrok

HOST = '127.0.0.1'
PORT = 1236


class Server:

    def __init__(self, debug=False, external=False):
        self.game_over = False
        self.game_active = False
        self.players = {1: None, 2: None}
        self.turn = None
        self.game = None
        self.engine = False
        self.debug = debug
        self.external = external
        self.lock = Lock()

    def debugging(self, *msg):
        if self.debug:
            print(*msg)

    @staticmethod
    def check_connection(conn):
        conn.setblocking(0)
        result = conn.send
        if not result:
            return False
        else:
            conn.setblocking(1)
            return True

    def handle_client(self, conn):
        request = conn.recv(1024)
        parser = eval(request.decode())
        # self.debugging('data', parser)
        if "new game" not in parser:
            return
        with self.lock:
            if not self.game_active:
                if not self.players[1] or not self.check_connection(self.players[1]):
                    if 'computer' in parser:
                        return self.play_against_computer(conn)
                    self.players[1] = conn
                    self.debugging('Player 1 set')
                    if self.players[2]:  # TODO
                        self.start_game()
                else:
                    self.players[2] = conn
                    self.debugging('Player 2 set')
                    self.start_game()
            else:
                conn.send(str({"new game": False}).encode())
                conn.close()

    def start_game(self):
        self.game_over = False
        self.game = ConnectDotsGame()
        self.turn = random.randrange(1, 3)

        ans = {"new game": True, "id": 1, "opponent": 2, "first": self.turn == 1}
        self.players[1].send(str(ans).encode())

        if not self.engine:
            ans = {"new game": True, "id": 2, "opponent": 1, "first": self.turn == 2}
            self.players[2].send(str(ans).encode())
            self.game_active = True
            self.manege_player(1)
            self.manege_player(2)

        else:
            self.players[2].first = self.turn == 2
            self.manege_player(1)
            if self.turn == 2:
                self.menage_computer_turn()

    def socket(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.bind((HOST, PORT))
        soc.listen()
        if self.external:
            public_url = ngrok.connect(PORT, 'tcp').public_url
            print(f' * ngrok tunnel  {public_url}  ->  http://127.0.0.1:{PORT} ')

        self.debugging(f'Waiting for connection ... in http://127.0.0.1:{PORT} ')
        while True:
            conn, address = soc.accept()
            self.debugging('connection from', address)
            t = Thread(target=self.handle_client, args=(conn,))
            t.start()

    @threaded
    def manege_player(self, player_name):
        while True:
            if self.game_over:
                quit()
            if self.turn != player_name:
                continue
            self.debugging(f'Waiting to Player {player_name} to make move')
            conn = self.players[player_name]
            try:
                req = conn.recv(1024)
                self.debugging(f'get {req} from {player_name}')
                parser = eval(req.decode())
                col = parser['column']
                if not self.game.is_validate_location(col):
                    ans = {"move": False}
                    conn.send(str(ans).encode())
                else:
                    row, col, win = self.game.add_disc(col)
                    self.update_move(row, col, win, player_name)

                    if win:
                        self.debugging(player_name, 'won', self.game.four_in_row)
                        self.game_over = True
                        self.clean()
                    else:
                        self.turn = 2 if self.turn == 1 else 1

            except Exception as e:
                # raise e # TODO
                self.debugging(e)
                self.debugging(f'Player {player_name} disconnected')
                self.abandoned(player_name)
                self.clean()

    def abandoned(self, player_name):
        if self.engine:
            return
        msg = {"abandoned": True}
        opponent = 2 if player_name == 1 else 1
        try:
            self.players[opponent].send(str(msg).encode())
        except (AttributeError, ConnectionResetError):
            self.debugging(f'Player {opponent} also disconnected')

    def update_move(self, row, col, win, player_name):
        ans = {"move": True, "row": row, "column": col, "win": win}
        if win:
            ans['four'] = self.game.four_in_row
        self.players[player_name].send(str(ans).encode())

        if self.engine:
            if win:
                return self.clean()
            return self.update_computer(col)

        ans = {"row": row, "column": col, "win": win}
        if win:
            ans['four'] = self.game.four_in_row
        opponent = 2 if player_name == 1 else 1
        self.players[opponent].send(str(ans).encode())

    def clean(self):
        self.game_active = False
        self.players = {1: None, 2: None}
        self.turn = None
        self.game = None



    @threaded
    def menage_computer_turn(self):
        col = self.players[2].make_move()
        row, col, win = self.game.add_disc(col)
        ans = {"row": row, "column": col, "win": win}
        if win:
            ans['four'] = self.game.four_in_row
        self.players[1].send(str(ans).encode())

        if win:
            self.game_over = True
            self.clean()
        else:
            self.turn = 1

    @threaded
    def update_computer(self, col):
        self.players[2].opponent_move(col)
        self.menage_computer_turn()

    def run(self):
        t_server = Thread(target=self.socket)
        t_server.start()
        t_server.join()

    def play_against_computer(self, conn):
        self.engine = True
        self.players[1] = conn
        self.players[2] = Engine.EnginePlayer()
        self.start_game()


if __name__ == '__main__':
    s = Server(debug=True)
    s.run()
