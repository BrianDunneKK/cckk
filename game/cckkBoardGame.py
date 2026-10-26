import random
import string


class Board:
    def __init__(self, xsize=None, ysize=None):
        self.init_board(xsize, ysize)

    def init_board(self, xsize=None, ysize=None):
        self._pieces = []
        if ysize is None:
            ysize = xsize
        self._size = (xsize, ysize)
        if xsize is not None and ysize is not None:
            for y in range(0, ysize):
                row = []
                for x in range(0, xsize):
                    row.append(".")
                self._pieces.append(row)

    @property
    def xsize(self):
        return self._size[0]

    @property
    def ysize(self):
        return self._size[1]

    def valid_cell(self, x, y):
        if self.xsize is None or self.ysize is None:
            return False
        return x >= 0 and y >= 0 and x < self.xsize and y < self.ysize

    def calc_xcols_yrows(self, xcols, yrows, num, horiz):
        if num is not None and horiz is not None:
            if horiz:
                xcols = num
                yrows = 1
            else:
                xcols = 1
                yrows = num

        if xcols is None or xcols < 1:
            xcols = 1
        elif xcols >= self.xsize:
            xcols = self.xsize - 1
        if yrows is None or yrows < 1:
            yrows = 1
        elif yrows >= self.ysize:
            yrows = self.ysize - 1

        return (xcols, yrows)

    def get_piece(self, x, y):
        if self.valid_cell(x, y):
            return self._pieces[y][x]
        else:
            return None

    def is_piece(self, x, y):
        return self._pieces[y][x] != "."

    def is_code_single(self, x, y, code):
        if self.valid_cell(x, y):
            return self._pieces[y][x] == code
        else:
            return None

    def is_blank_single(self, x, y):
        return self.is_code_single(x, y, ".")

    def is_code(self, x, y, code, xcols=1, yrows=1, num=None, horiz=None):
        xcols, yrows = self.calc_xcols_yrows(xcols, yrows, num, horiz)

        all_code = True
        for i in range(xcols):
            for j in range(yrows):
                all_code = all_code and self.is_code_single(x + i, y + j, code)

        return all_code

    def is_blank(self, x, y, xcols=1, yrows=1, num=None, horiz=None):
        return self.is_code(x, y, ".", xcols, yrows, num, horiz)

    def test_pieces(self, xy_list, value="."):
        if value is None:
            x, y = xy_list[0]
            value = self.get_piece(x, y)
        found = True
        for xy in xy_list:
            found = found and self.is_code_single(xy[0], xy[1], value)
        return found

    def set_piece_single(self, x, y, code):
        if self.valid_cell(x, y):
            self._pieces[y][x] = code
            return code
        else:
            return None

    def set_piece(self, x, y, code, xcols=1, yrows=1, num=None, horiz=None):
        xcols, yrows = self.calc_xcols_yrows(xcols, yrows, num, horiz)
        for i in range(xcols):
            for j in range(yrows):
                self.set_piece_single(x + i, y + j, code)

    def clear_piece(self, x, y):
        return self.set_piece_single(x, y, ".")

    def clear_board(self):
        self.set_piece(0, 0, ".", self.xsize, self.ysize)

    def find(self, filter):
        # Filter options: "*" = All pieces, "." = Blank cells, Anything else = Cell contents
        piece_list = []
        for y in range(0, self.ysize):
            for x in range(0, self.xsize):
                if filter[0] == "*" and self.is_piece(x, y):
                    piece_list.append([x, y, self.get_piece(x, y)])
                elif filter[0] == "." and not self.is_piece(x, y):
                    piece_list.append([x, y, self.get_piece(x, y)])
                elif filter == self.get_piece(x, y):
                    piece_list.append([x, y, self.get_piece(x, y)])
        return piece_list

    def find_random_single(self, code="."):
        piece_list = self.find(code)
        return random.choice(piece_list)

    def find_random(self, code=".", xcols=1, yrows=1, num=None, horiz=None):
        if num is not None and horiz is None:
            horiz = random.choice([True, False])
        xcols, yrows = self.calc_xcols_yrows(xcols, yrows, num, horiz)

        attempts = 0
        found = False
        while not found and attempts < 1000:
            random_cell = self.find_random_single(code)
            found = self.is_code(random_cell[0], random_cell[1], code, xcols, yrows)
            attempts += 1
        if found:
            return (random_cell[0], random_cell[1], xcols, yrows)
        else:
            return None

    def set_random(self, code, xcols=1, yrows=1, num=None, horiz=None):
        cell = self.find_random(".", xcols, yrows, num, horiz)
        if cell is not None:
            self.set_piece(cell[0], cell[1], code, xcols=cell[2], yrows=cell[3])
        ret_dict = {
            "xpos": cell[0],
            "ypos": cell[1],
            "xcols": cell[2],
            "yrows": cell[3],
            "code": code,
        }
        return ret_dict

    @property
    def pieces(self):
        piece_list = []
        for y in range(0, self.ysize):
            for x in range(0, self.xsize):
                if self.is_piece(x, y):
                    piece_list.append([x, y, self.get_piece(x, y)])
        return piece_list

    def count_pieces(self, value):
        count = 0
        for y in range(0, self.ysize):
            for x in range(0, self.xsize):
                if self.get_piece(x, y) == value:
                    count += 1
        return count

    def count_blanks(self):
        return self.count_pieces(".")

    def board_to_str(self, inc_labels=False, rotate=False):
        board_str = ""
        if not rotate:
            cols = string.hexdigits[: self.ysize]
            rows = string.ascii_uppercase[: self.xsize]
        else:
            cols = string.ascii_uppercase[: self.xsize]
            rows = string.hexdigits[: self.ysize]
        cols = list(cols)
        rows = list(rows)
        if inc_labels:
            board_str += "    " + " ".join(cols) + "  \n"
            board_str += "  "
        if not rotate:
            board_str += "+" + "-" * self.xsize * 2 + "-+\n"
            for i in range(self.ysize):
                if inc_labels:
                    board_str += rows[i] + " "
                board_str += "|"
                for j in range(self.xsize):
                    board_str += " " + self._pieces[i][j]
                board_str += " |\n"
            if inc_labels:
                board_str += "  "
            board_str += "+" + "-" * self.xsize * 2 + "-+"
        else:
            board_str += "+" + "-" * self.ysize * 2 + "-+\n"
            for i in range(self.xsize):
                if inc_labels:
                    board_str += rows[i] + " "
                board_str += "|"
                for j in range(self.ysize):
                    board_str += " " + self._pieces[j][i]
                board_str += " |\n"
            if inc_labels:
                board_str += "  "
            board_str += "+" + "-" * self.ysize * 2 + "-+"
        return board_str

    def print_board(
        self, prefix=None, suffix=None, inc_labels=False, rotate=False, as_debug=False
    ):
        board_str = self.board_to_str(inc_labels=inc_labels, rotate=rotate)
        if not as_debug:
            if prefix is not None:
                print(prefix)
            print(board_str)
            if suffix is not None:
                print(suffix)
        else:
            if prefix is not None:
                cdkk.logger.debug(prefix)
            for str in board_str.split("\n"):
                cdkk.logger.debug(str)
            if suffix is not None:
                cdkk.logger.debug(suffix)

    def print_boards(
        board_list,
        prefix=None,
        suffix=None,
        inc_labels=False,
        rotate=False,
        spacer="        ",
    ):
        if len(board_list) == 1:
            board_list[0].print_board(prefix, suffix, inc_labels, rotate)
        else:
            print_str_list = None
            for board in board_list:
                board_str = board.board_to_str(inc_labels=inc_labels, rotate=rotate)
                board_str_list = board_str.split("\n")
                if print_str_list is None:
                    print_str_list = board_str_list.copy()
                else:
                    for i in range(len(print_str_list)):
                        print_str_list[i] = (
                            print_str_list[i] + spacer + board_str_list[i]
                        )

        if prefix is not None:
            print(prefix)
        print("\n".join(print_str_list))
        if suffix is not None:
            print(suffix)

    def a1_to_xy(a1_ref):
        yrow = ord(a1_ref.upper()[0]) - ord("A")
        xcol = int(a1_ref[1:])
        return (xcol, yrow)


# --------------------------------------------------


class GameManager:
    def __init__(self, num_players=None):
        super().__init__()
        self.game_init_context()
        self._game_over = False
        self._turn_num = 0

    @property
    def game_over(self):
        return self._game_over

    @property
    def game_in_progress(self):
        return not self._game_over

    def set_game_over(self, game_is_over=None):
        if game_is_over is not None:
            self._game_over = game_is_over

    @property
    def turn_num(self):
        return self._turn_num

    def next_turn(self):
        self._turn_num = self._turn_num + 1
        self.game_set_context("Turn", self.turn_num)
        return self.turn_num

    @property
    def game_full_context(self):
        return self._game_context

    def game_init_context(self, new_context=None):
        if new_context is None:
            self._game_context = {}
        else:
            self._game_context = new_context

    def game_get_context(self, attribute, default=None):
        if self._game_context is None:
            return default
        if attribute in self._game_context:
            return self._game_context[attribute]
        else:
            return default

    def game_set_context(self, attribute, value):
        self._game_context[attribute] = value
        return value

    def init_game(self):
        self.game_set_context("Turn", 0)

    def start_game(self):
        self.set_game_over(False)
        self._turn_num = 0

    def draw_game(self):
        pass

    def end_game(self):
        pass

    def process_input(self, input):
        dealt_with = False
        return dealt_with


# --------------------------------------------------


class GameManagerMP(GameManager):  # Multi-Player Game
    def __init__(self, num_players=None):
        super().__init__()
        self.mpg_current_player = 0  # Player = 1, 2, ...
        self.num_players = num_players
        self.mpg_player_codes = self.mpg_player_names = None

    def init_game(self):
        super().init_game()
        if self.num_players is not None:
            self.mpg_current_player = 1
            self.game_set_context("WinnerNum", None)

    def start_game(self):
        super().start_game()
        self.current_player = 1

    @property
    def num_players(self):
        return self._num_players

    @num_players.setter
    def num_players(self, new_num_players):
        self._num_players = new_num_players
        if new_num_players is not None:
            self.mpg_player_codes = [str(x + 1) for x in range(new_num_players)]
            self.mpg_player_names = [
                "Player {0}".format(x + 1) for x in range(new_num_players)
            ]

    @property
    def current_player(self):
        return self.mpg_current_player

    @current_player.setter
    def current_player(self, new_current_player):
        if new_current_player > 0 and new_current_player <= self.num_players:
            self.mpg_current_player = new_current_player
            self.game_set_context("CurrentPlayer", self.current_player)

    def player_name(self, player_num):
        return self.mpg_player_names[player_num - 1]

    def player_code(self, player_num):
        return self.mpg_player_codes[player_num - 1]

    def next_player(self):
        self.current_player = (self.current_player % self.num_players) + 1

    @property
    def current_player_code(self):
        return self.player_code(self.current_player)

    @property
    def current_player_name(self):
        return self.player_name(self.current_player)

    @property
    def winner_num(self):
        return self.game_get_context("WinnerNum")

    @winner_num.setter
    def winner_num(self, new_winner_num):
        self.game_set_context("WinnerNum", new_winner_num)
        self.set_game_over(new_winner_num is not None)

    @property
    def winner_code(self):
        if self.winner_num is None:
            return None
        elif self.winner_num == 0:
            return "Draw"
        else:
            return self.player_code(self.winner_num)

    @property
    def winner_name(self):
        if self.winner_num is None or self.winner_num == 0:
            return self.winner_code
        else:
            return self.player_name(self.winner_num)

    def set_player_names(self, player_names):
        num = min(self.num_players, len(player_names))
        for i in range(num):
            self.mpg_player_names[i] = player_names[i]

    def set_player_codes(self, player_codes):
        num = min(self.num_players, len(player_codes))
        for i in range(num):
            self.mpg_player_codes[i] = player_codes[i]

    def player_by_code(self, player_code):
        player_num = 0
        i = 1
        for p in self.mpg_player_codes:
            if p == player_code and player_num == 0:
                player_num = i
            else:
                i += 1
        return player_num


# --------------------------------------------------


class BoardGame(GameManagerMP, Board):
    def __init__(self, xsize=None, ysize=None, num_players=2):
        super().__init__()
        self.init_board(xsize, ysize)
        self.num_players = num_players

    def start_game(self):
        self.clear_board()
        super().start_game()

    def count_player_pieces(self, player_num):
        return self.count_pieces(self.player_code(player_num))

    def valid_play(self, col=None, row=None, check_if_blank=True):
        if col is None or row is None:
            move_is_valid = True
        else:
            move_is_valid = (
                self.game_in_progress
                and col >= 0
                and col < self.xsize
                and row >= 0
                and row < self.ysize
            )

            if check_if_blank:
                move_is_valid = move_is_valid and self.is_blank(col, row)

        return move_is_valid

    def calculate_play(self, col, row):
        return (col, row)

    def execute_play(self, col, row, code=None):
        if code is None:
            code = self.current_player_code
        self.set_piece(col, row, code)
        consequences = None
        return consequences

    def manage_consequences(self, col, row, consequences):
        pass

    def calculate_changes(self, c, r, consequences):
        changes = []
        changes.append([c, r, self.get_piece(c, r), "add"])
        return changes

    def check_game_over(self, player_num, col, row):
        # Return: Winner's number; 0 = Draw; None = No winner
        winner = None
        return winner

    def play_piece(self, col=0, row=0, context=None):
        if row is None:
            row = col // self.xsize
            col = col % self.xsize
        self.game_init_context(context)
        self.game_set_context("changes", None)

        c, r = (col, row)
        valid_move = self.valid_play(col, row)
        if valid_move:
            self.game_set_context("ValidMove", True)
            self.next_turn()
            c, r = self.calculate_play(col, row)
            consequences = self.execute_play(c, r)
            self.manage_consequences(c, r, consequences)
            self.game_set_context("changes", self.calculate_changes(c, r, consequences))
            p = self.current_player
            self.next_player()
            self.winner_num = self.check_game_over(p, c, r)
        else:
            p = None
            self.winner_num = None
            self.game_set_context("ValidMove", False)

        return self.game_full_context


# --------------------------------------------------


class Direction:
    def __init__(self, name, xstep, ystep, value):
        self.name = name
        self.xstep = xstep
        self.ystep = ystep
        self.value = value


class Directions:
    n = Direction("N", 0, -1, 1)
    ne = Direction("NE", 1, -1, 2)
    e = Direction("E", 1, 0, 4)
    se = Direction("SE", 1, 1, 8)
    s = Direction("S", 0, 1, 16)
    sw = Direction("SW", -1, 1, 32)
    w = Direction("W", -1, 0, 64)
    nw = Direction("NW", -1, -1, 128)

    all_dirs = [n, ne, e, se, s, sw, w, nw]


# --------------------------------------------------
