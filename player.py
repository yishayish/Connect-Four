import os
import signal
import socket
from utils import threaded

import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 150, 0)
RED = (204, 0, 0)
GREEN = (0, 153, 0)
BLUE = (0, 100, 255)
COLORS = {1: RED, 2: GREEN}

ROWS = 6
COLUMNS = 7
SQUARE_SIZE = 80

width = COLUMNS * SQUARE_SIZE
height = (ROWS + 1) * SQUARE_SIZE


class Client:

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = False
        try:
            self.socket.connect((host, port))
            print('connecting ...')
            self.connection = True
        except socket.error as err:
            print(err)

    def send(self, request):
        self.socket.send(str(request).encode())

    def receive(self):
        try:
            answer = self.socket.recv(1024)
            return eval(answer.decode())
        except:
            print('connection error \n player terminating')
            self.socket.close()
            os.kill(os.getpid(), signal.SIGABRT)


class Player:

    def __init__(self, host, port, computer=False):
        self.game_active = False
        self.my_turn = False
        self.game_over = False
        self.id = None
        self.opponent_id = None
        self.full_cols = set()
        self.cols = {i: ROWS - 1 for i in range(COLUMNS)}
        self.win = False
        self.lose = False
        self.four = []
        self.new_game_button_active = False
        self.against_computer = computer

        self.host = host
        self.port = port
        self.server_connection = Client(host, port)

        pygame.init()
        self.screen = pygame.display.set_mode((width, height))

    def manege_cols(self, col):
        self.cols[col] -= 1
        if self.cols[col] == -1:
            self.full_cols.add(col)

    def add_dot(self, col):
        if col not in self.full_cols:
            self.draw_circle_by_index(COLORS[self.id], col, self.cols[col])
            self.manege_cols(col)
            self.update_server(col)
            self.my_turn = False

    def draw_board(self):
        pygame.draw.rect(self.screen, BLUE, (0, SQUARE_SIZE, width, height - SQUARE_SIZE))
        for r in range(ROWS):
            for c in range(COLUMNS):
                self.draw_circle_by_index(BLACK, c, r)

    def draw_the_four(self,s=0):
        for r, c in self.four:
            self.draw_circle_by_index(ORANGE, c, r)
        pygame.time.wait(1000)
        color = COLORS[self.id] if self.win else COLORS[self.opponent_id]
        for r, c in self.four:
            self.draw_circle_by_index(color, c, r)
        pygame.time.wait(1000)
        if s<1:
            self.draw_the_four(s=s+1)


    @threaded
    def waiting(self):
        self.print_to_screen('       Waiting for another player ... ', WHITE)
        while not self.game_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
            if self.game_over:
                self.print_to_screen('NO GAME! try later', WHITE)
                pygame.time.wait(5000)
                quit()

    def start_game(self):
        if not self.server_connection.connection:
            print('There is no connection')
        else:
            req = {"new game": True}
            if self.against_computer:
                req['computer'] = True
            self.server_connection.send(req)
            self.waiting()

            replay = self.server_connection.receive()
            if not replay['new game']:
                self.game_over = True
            else:
                self.game_active = True
                self.draw_board()
                self.id = replay['id']
                self.opponent_id = replay['opponent']
                self.my_turn = replay['first']
                if not self.my_turn:
                    self.get_update()
                self.main_loop()

    def print_to_screen(self, msg, color):
        pygame.draw.rect(self.screen, BLACK, (0, 0, width, SQUARE_SIZE))
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        text_surface = font.render('    ' + msg, True, color)
        self.screen.blit(text_surface, dest=(0, SQUARE_SIZE / 3))
        pygame.display.update()

    def main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # self.quit()
                    os.kill(os.getpid(), signal.SIGABRT)
                if self.new_game_button_active:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x = width // 2 - SQUARE_SIZE
                        x2 = width // 2 - SQUARE_SIZE + 2 * SQUARE_SIZE
                        y = SQUARE_SIZE // 4
                        y2 = SQUARE_SIZE // 4 + SQUARE_SIZE // 2
                        if x < event.pos[0] < x2 and y < event.pos[1] < y2:
                            self.new_game_handler()
                elif self.game_over:
                    if self.win:
                        self.draw_the_four()
                        self.print_to_screen('Congratulations! you are the winner', WHITE)
                    elif self.lose:
                        self.draw_the_four()
                        self.print_to_screen('Unfortunately, you lost the game', WHITE)
                    else:
                        self.print_to_screen(f'GAME OVER. Player {self.opponent_id}'
                                             f' Abandoned The Game', WHITE)
                    # pygame.time.wait(50000)
                    self.new_game_button()
                    self.new_game_button_active = True

                elif not self.my_turn:
                    pygame.draw.rect(self.screen, BLACK, (0, 0, width, SQUARE_SIZE))
                    pygame.display.update()

                elif event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(self.screen, BLACK, (0, 0, width, SQUARE_SIZE))
                    pos_x = event.pos[0]
                    self.draw_circle(COLORS[self.id], pos_x, SQUARE_SIZE / 2)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    col = event.pos[0] // SQUARE_SIZE
                    self.add_dot(col)



    def draw_circle_by_index(self, color, c, r):
        x = c * SQUARE_SIZE + SQUARE_SIZE / 2
        y = (r + 1) * SQUARE_SIZE + SQUARE_SIZE / 2
        return self.draw_circle(color, x, y)

    def draw_circle(self, color, x, y):
        pygame.draw.circle(surface=self.screen,
                           color=color,
                           center=(x, y),
                           radius=SQUARE_SIZE / 2 - 5)
        pygame.display.update()

    def new_game_button(self):
        pygame.draw.rect(self.screen, GREEN,
                         (width // 2 - SQUARE_SIZE, SQUARE_SIZE // 4, 2 * SQUARE_SIZE, SQUARE_SIZE // 2))
        font = pygame.font.SysFont('arial', 20, bold=True, italic=True)
        text = font.render('New Game', True, BLACK)
        self.screen.blit(text, (width // 2 - SQUARE_SIZE + 30, SQUARE_SIZE // 4 + 10))
        pygame.display.update()

    def new_game_handler(self):
        # self.print_to_screen('gggg')
        self.__init__(self.host, self.port)
        self.start_game()

    @threaded
    def update_server(self, col):
        req = {"id": self.id, "column": col}
        self.server_connection.send(req)

        replay = self.server_connection.receive()
        self.game_over = self.win = replay["win"]
        if self.win:
            self.four = replay['four']
        if not self.game_over:
            self.get_update()

    @threaded
    def get_update(self):
        update = self.server_connection.receive()

        if 'abandoned' in update:
            self.game_over = True
            return

        color = COLORS[self.opponent_id]
        self.draw_circle_by_index(color, update["column"], update["row"])
        self.manege_cols(update["column"])
        self.my_turn = True
        self.game_over = self.lose = update['win']
        if self.lose:
            self.four = update['four']

    # @threaded
    # def quit(self):
    #     req = {"quit": True}
    #     self.server_connection.send(req)


if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 1236
    p = Player(HOST, PORT, computer=True)
    p.start_game()
