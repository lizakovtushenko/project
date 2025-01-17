# import modules
import pygame
import random
import copy
import time
# set colors
SEA_COLOR = (0, 137, 171)
BROWN = (89, 61, 32)
LIGHT_BROWN = (123, 95, 66)
LIGHTER_BROWN = ()
WHITE = (255,255,255)
num = 3
# set block/margins size
block_size = 50
left_margin = 5 * block_size
upper_margin = 2 * block_size
# size of the window
size = (left_margin + 30 * block_size, upper_margin + 15 * block_size)
LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
pygame.init()

screen = pygame.display.set_mode(size)
pygame.display.set_caption("SEA FIGHT")
img = pygame.image.load("images/sea1.png")
img2 = pygame.image.load("images/sea2.png")

# set font size according to the block size
font_size = int(block_size / 1.5)
#pygame.font.SysFont() — создаёт объект Font из системных шрифтов
font = pygame.font.SysFont('Arial', font_size)
game_over_font_size = 3 * block_size
game_over_font = pygame.font.SysFont('Arial', game_over_font_size)

# data for computer
computer_available_to_fire_set = {(x, y)
                                  for x in range(16, 26) for y in range(1, 11)}
around_last_computer_hit_set = set()
dotted_set_for_computer_not_to_shoot = set()
hit_blocks_for_computer_not_to_shoot = set()
last_hits_list = []
###################

hit_blocks = set()
dotted_set = set()
destroyed_computer_ships = []


#    Class to draw the grids and add title, numbers and letters to them
class Grid:
    """
    Attributes:
        title (str): Players' name to be displayed on the top of his grid
        offset (int): Where the grid starts (in number of blocks)
                ( 0 for computer and 15 for human)
    """

    def __init__(self, title, offset):

        self.title = title
        self.offset = offset
        self.__draw_grid()
        self.__add_nums_letters_to_grid()
        self.__sign_grid()

#  draws two grids for both players
    def __draw_grid(self):
        for i in range(11):
            # Horizontal lines
            pygame.draw.line(screen, BROWN, (left_margin + self.offset * block_size, upper_margin + i * block_size),
                             (left_margin + (10 + self.offset) * block_size, upper_margin + i * block_size), 3)
            # Vertical lines
            pygame.draw.line(screen, BROWN, (left_margin + (i + self.offset) * block_size, upper_margin),
                             (left_margin + (i + self.offset) * block_size, upper_margin + 10 * block_size), 3)

#   Draws numbers, letters for both grids
    def __add_nums_letters_to_grid(self):
        for i in range(10):
            num_ver = font.render(str(i + 1), True, BROWN)
            letters_hor = font.render(LETTERS[i], True, BROWN)
            num_ver_width = num_ver.get_width()
            num_ver_height = num_ver.get_height()
            letters_hor_width = letters_hor.get_width()

            # Numbers (vertical)
            screen.blit(num_ver, (left_margin - (block_size // 2 + num_ver_width // 2) + self.offset * block_size,
                                  upper_margin + i * block_size + (block_size // 2 - num_ver_height // 2)))
            # Letters (horizontal)
            screen.blit(letters_hor, (left_margin + i * block_size + (block_size // 2 -
                                                                      letters_hor_width // 2) + self.offset * block_size,
                                      upper_margin + 10 * block_size))

#        puts players' names above the grids
    def __sign_grid(self):
        player = font.render(self.title, True, BROWN)
        sign_width = player.get_width()
        screen.blit(player, (left_margin + 5 * block_size - sign_width // 2 +
                             self.offset * block_size, upper_margin - block_size // 2 - font_size))

#     creates buttons and prints explanatory message for them
class Button:
    """
    Attributes:
        __title (str): Button's name (title)
        __message (str): explanatory message to print on screen
        __x_start (int): horizontal offset where to start drawing button
        __y_start (int): vertical offset where to start drawing button
        rect_for_draw (tuple of four ints): button's rectangle to be drawn
        rect (pygame Rect): pygame Rect object
        __rect_for_button_title (tuple of two ints): rectangle within button to print text in it
        __color (tuple): color of button
    """

    def __init__(self, x_offset, button_title, message_to_show):
        self.__title = button_title
        self.__title_width, self.__title_height = font.size(self.__title)
        self.__message = message_to_show
        self.__button_width = self.__title_width + block_size
        self.__button_height = self.__title_height + block_size
        self.__x_start = x_offset
        self.__y_start = upper_margin + 10 * block_size + self.__button_height
        self.rect_for_draw = self.__x_start, self.__y_start, self.__button_width, self.__button_height
        self.rect = pygame.Rect(self.rect_for_draw)
        self.__rect_for_button_title = self.__x_start + self.__button_width / 2 - \
                                       self.__title_width / 2, self.__y_start + \
                                       self.__button_height / 2 - self.__title_height / 2
        self.__color = BROWN
#    draws button as a rectangle
    def draw_button(self, color=None):
        if not color:
            color = self.__color
        pygame.draw.rect(screen, color, self.rect_for_draw)
        text_to_blit = font.render(self.__title, True, WHITE)
        screen.blit(text_to_blit, self.__rect_for_button_title)

#   draws button as a rectangle with changable color
    def change_color_on_hover(self):
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            self.draw_button(LIGHT_BROWN)

#   prints explanatory message next to button
    def print_message_for_button(self):
        message_width, message_height = font.size(self.__message)
        rect_for_message = self.__x_start / 2 - message_width / \
                           2, self.__y_start + self.__button_height / 2 - message_height / 2
        text = font.render(self.__message, True, WHITE)
        screen.blit(text, rect_for_message)

# randomly create all player's ships on a grid
class AutoShips:
    def __init__(self, offset):
        """
        Parameters:
        offset (int): Where the grid starts (in number of blocks)
                (typically 0 for computer and 15 for human)
        available_blocks (set of tuples): coordinates of all blocks
                that are avaiable for creating ships (updated every time a ship is created)
        ships_set (set of tuples): all blocks that are occupied by ships
        ships (list of lists): list of all individual ships (as lists)"""

        self.offset = offset
        self.available_blocks = {(x, y) for x in range(
            1 + self.offset, 11 + self.offset) for y in range(1, 11)}
        #Список всех отдельных кораблей, представленных в виде списков координат.
        self.ships_set = set()
        self.ships = self.__populate_grid()
        self.orientation = None
        self.direction = None


#    Randomly chooses horizontal or vertical type of a ship
    def __create_start_block(self, available_blocks):
#     Randomly chooses horizontal or vertical type of a ship(int: 0=horizontal (change x), 1=vertical (change y))
        self.orientation = random.randint(0, 1)
#     Randomly chooses direction (from the start block) - straight or reverse(-1 is left or down, 1 is right or up)
        self.direction = random.choice((-1, 1))
#       Randomly chooses a block from which to start creating a ship.
        x, y = random.choice(tuple(available_blocks))
        return x, y, self.orientation, self.direction


    def __create_ship(self, number_of_blocks, available_blocks):
        """
        Creates a ship of given length (number_of_blocks) starting from the start block
        returned by the previous method, using type of ship and direction (changing it
        if going outside of grid) returned by previous method.
        Checks if the ship is valid (not adjacent to other ships and within the grid)
        and adds it to the list of ships.
        Args:
            number_of_blocks (int): length of a needed ship
            available_blocks (set): free blocks for creating ships
        Returns:
                list: a list of tuples with a new ship's coordinates
        """
        ship_coordinates = []
        x, y, self.orientation, self.direction = self.__create_start_block(
            available_blocks)
        for _ in range(number_of_blocks):
            ship_coordinates.append((x, y))
            if not self.orientation:
                self.direction, x = self.__get_new_block_for_ship(
                    x, self.direction, self.orientation, ship_coordinates)
            else:
                self.direction, y = self.__get_new_block_for_ship(
                    y, self.direction, self.orientation, ship_coordinates)
        if self.__is_ship_valid(ship_coordinates):
            return ship_coordinates
        return self.__create_ship(number_of_blocks, available_blocks)

    def __get_new_block_for_ship(self, coor, direction, orientation, ship_coordinates):
        """
        Checks if new individual blocks that are being added to a ship in the previous method
                are within the grid, otherwise changes the direction.
        Args:
            coor (int): x or y coordinate to increment/decrement
            direction (int): 1 or -1
            orientation (int): 0 or 1
            ship_coordinates (list): coordinates of unfinished ship
        Returns:
            direction (int): straight or reverse
            incremented/decremented coordinate of the last/first block in a ship under construction (int)
        """
        self.direction = direction
        self.orientation = orientation
        if (coor <= 1 - self.offset * (self.orientation - 1) and self.direction == -1) or (
                coor >= 10 - self.offset * (self.orientation - 1) and self.direction == 1):
            self.direction *= -1
            return self.direction, ship_coordinates[0][self.orientation] + self.direction
        else:
            return self.direction, ship_coordinates[-1][self.orientation] + self.direction

    def __is_ship_valid(self, new_ship):
        """
        Check if all of a ship's coordinates are within the available blocks set.
        Args:
            new_ship (list): list of tuples with a newly created ship's coordinates
        Returns:
            bool: True or False
        """
        ship = set(new_ship)
        return ship.issubset(self.available_blocks)

    def __add_new_ship_to_set(self, new_ship):
        """
        Adds all blocks in a ship's list to the ships_set
        Args:
            new_ship (list): list of tuples with a newly created ship's coordinates
        """
        self.ships_set.update(new_ship)

    def __update_available_blocks_for_creating_ships(self, new_ship):
        """
        Removes all blocks occupied by a ship and around it from the available blocks set
        Args:
            new_ship ([type]): list of tuples with a newly created ship's coordinates
        """
        for elem in new_ship:
            for k in range(-1, 2):
                for m in range(-1, 2):
                    if self.offset < (elem[0] + k) < 11 + self.offset and 0 < (elem[1] + m) < 11:
                        self.available_blocks.discard(
                            (elem[0] + k, elem[1] + m))

    def __populate_grid(self):
        """
        Creates needed number of each type of ships by calling the create_ship method.
                Adds every ship to the ships list, ships_set and updates the available blocks.
        Returns:
            list: the 2d list of all ships
        """
        ships_coordinates_list = []
        for number_of_blocks in range(4, 0, -1):
            for _ in range(5 - number_of_blocks):
                new_ship = self.__create_ship(
                    number_of_blocks, self.available_blocks)
                ships_coordinates_list.append(new_ship)
                self.__add_new_ship_to_set(new_ship)
                self.__update_available_blocks_for_creating_ships(new_ship)
        return ships_coordinates_list


# ===========Shooting section==============


def computer_shoots(set_to_shoot_from):
    """
    Randomly chooses a block from available to shoot from set
    """
    pygame.time.delay(500)
    computer_fired_block = random.choice(tuple(set_to_shoot_from))
    computer_available_to_fire_set.discard(computer_fired_block)
    return computer_fired_block


def check_hit_or_miss(fired_block, opponents_ships_list, computer_turn, opponents_ships_list_original_copy,
                      opponents_ships_set):
    """
    Checks whether the block that was shot at either by computer or by human is a hit or a miss.
    Updates sets with dots (in missed blocks or in diagonal blocks around hit block) and 'X's
    (in hit blocks).
    Removes destroyed ships from the list of ships.
    """
    for elem in opponents_ships_list:
        diagonal_only = True
        if fired_block in elem:
            # This is to put dots before and after a destroyed ship
            # and to draw computer's destroyed ships (which are hidden until destroyed)
            ind = opponents_ships_list.index(elem)
            if len(elem) == 1:
                diagonal_only = False
            update_dotted_and_hit_sets(
                fired_block, computer_turn, diagonal_only)
            elem.remove(fired_block)
            # This is to check who loses - if ships_set is empty
            opponents_ships_set.discard(fired_block)
            if computer_turn:
                last_hits_list.append(fired_block)
                update_around_last_computer_hit(fired_block, True)
            # If the ship is destroyed
            if not elem:
                update_destroyed_ships(
                    ind, computer_turn, opponents_ships_list_original_copy)
                if computer_turn:
                    last_hits_list.clear()
                    around_last_computer_hit_set.clear()
                else:
                    # Add computer's destroyed ship to the list to draw it (computer ships are hidden)
                    destroyed_computer_ships.append(computer.ships[ind])
            return True
    add_missed_block_to_dotted_set(fired_block)
    if computer_turn:
        update_around_last_computer_hit(fired_block, False)
    return False


def update_destroyed_ships(ind, computer_turn, opponents_ships_list_original_copy):
    """
    Adds blocks before and after a ship to dotted_set to draw dots on them.
    Adds all blocks in a ship to hit_blocks set to draw 'X's within a destroyed ship.
    """
    ship = sorted(opponents_ships_list_original_copy[ind])
    for i in range(-1, 1):
        update_dotted_and_hit_sets(ship[i], computer_turn, False)


def update_around_last_computer_hit(fired_block, computer_hits):
    """
    Updates around_last_computer_hit_set (which is used to choose for computer to fire from) if it
    hit the ship but not destroyed it). Adds to this set vertical or horizontal blocks around the
    block that was last hit. Then removes those block from that set which were shot at but missed.
    around_last_computer_hit_set makes computer choose the right blocks to quickly destroy the ship
    instead of just randomly shooting at completely random blocks.
    """
    global around_last_computer_hit_set, computer_available_to_fire_set
    if computer_hits and fired_block in around_last_computer_hit_set:
        around_last_computer_hit_set = computer_hits_twice()
    elif computer_hits and fired_block not in around_last_computer_hit_set:
        computer_first_hit(fired_block)
    elif not computer_hits:
        around_last_computer_hit_set.discard(fired_block)

    around_last_computer_hit_set -= dotted_set_for_computer_not_to_shoot
    around_last_computer_hit_set -= hit_blocks_for_computer_not_to_shoot
    computer_available_to_fire_set -= around_last_computer_hit_set
    computer_available_to_fire_set -= dotted_set_for_computer_not_to_shoot


def computer_first_hit(fired_block):
    """
    Adds blocks above, below, to the right and to the left from the block hit
    by computer to a temporary set for computer to choose its next shot from.
    Args:
        fired_block (tuple): coordinates of a block hit by computer
    """
    x_hit, y_hit = fired_block
    if x_hit > 16:
        around_last_computer_hit_set.add((x_hit - 1, y_hit))
    if x_hit < 25:
        around_last_computer_hit_set.add((x_hit + 1, y_hit))
    if y_hit > 1:
        around_last_computer_hit_set.add((x_hit, y_hit - 1))
    if y_hit < 10:
        around_last_computer_hit_set.add((x_hit, y_hit + 1))


def computer_hits_twice():
    """
    Adds blocks before and after two or more blocks of a ship to a temporary list
    for computer to finish the ship faster.
    Returns:
        set: temporary set of blocks where potentially a human ship should be
        for computer to shoot from
    """
    last_hits_list.sort()
    new_around_last_hit_set = set()
    for i in range(len(last_hits_list) - 1):
        x1 = last_hits_list[i][0]
        x2 = last_hits_list[i + 1][0]
        y1 = last_hits_list[i][1]
        y2 = last_hits_list[i + 1][1]
        if x1 == x2:
            if y1 > 1:
                new_around_last_hit_set.add((x1, y1 - 1))
            if y2 < 10:
                new_around_last_hit_set.add((x1, y2 + 1))
        elif y1 == y2:
            if x1 > 16:
                new_around_last_hit_set.add((x1 - 1, y1))
            if x2 < 25:
                new_around_last_hit_set.add((x2 + 1, y1))
    return new_around_last_hit_set


def update_dotted_and_hit_sets(fired_block, computer_turn, diagonal_only=True):
    """
    Puts dots in center of diagonal or all around a block that was hit (either by human or
    by computer). Adds all diagonal blocks or all-around chosen block to a separate set
    block: hit block (tuple)
    """
    global dotted_set
    x, y = fired_block
    a = 15 * computer_turn
    b = 11 + 15 * computer_turn
    # Adds a block hit by computer to the set of his hits to later remove
    # them from the set of blocks available for it to shoot from
    hit_blocks_for_computer_not_to_shoot.add(fired_block)
    # Adds hit blocks on either grid1 (x:1-10) or grid2 (x:16-25)
    hit_blocks.add(fired_block)
    # Adds blocks in diagonal or all-around a block to repsective sets
    for i in range(-1, 2):
        for j in range(-1, 2):
            if (not diagonal_only or i != 0 and j != 0) and a < x + i < b and 0 < y + j < 11:
                add_missed_block_to_dotted_set((x + i, y + j))
    dotted_set -= hit_blocks


def add_missed_block_to_dotted_set(fired_block):
    """
    Adds a fired_block to the set of missed shots (if fired_block is a miss then) to then draw dots on them.
    Also needed for computer to remove these dotted blocks from the set of available blocks for it to shoot from.
    """
    dotted_set.add(fired_block)
    dotted_set_for_computer_not_to_shoot.add(fired_block)


# ===========DRAWING SECTION==============

def draw_ships(ships_coordinates_list):
    """
    Draws rectangles around the blocks that are occupied by a ship
    Args:
        ships_coordinates_list (list of tuples): a list of ships's coordinates
    """
    for elem in ships_coordinates_list:
        ship = sorted(elem)
        x_start = ship[0][0]
        y_start = ship[0][1]
        # Horizontal and 1block ships
        ship_width = block_size * len(ship)
        ship_height = block_size
        # Vertical ships
        if len(ship) > 1 and ship[0][0] == ship[1][0]:
            ship_width, ship_height = ship_height, ship_width
        x = block_size * (x_start - 1) + left_margin
        y = block_size * (y_start - 1) + upper_margin
        pygame.draw.rect(
            screen, BROWN, ((x, y), (ship_width, ship_height)), width=block_size // 10)


def draw_from_dotted_set(dotted_set_to_draw_from):
    """
    Draws dots in the center of all blocks in the dotted_set
    """
    for elem in dotted_set_to_draw_from:
        pygame.draw.circle(screen, BROWN, (block_size * (
                elem[0] - 0.5) + left_margin, block_size * (elem[1] - 0.5) + upper_margin), block_size // 6)


def draw_hit_blocks(hit_blocks_to_draw_from):
    """
    Draws 'X' in the blocks that were successfully hit either by computer or by human
    """
    for block in hit_blocks_to_draw_from:
        x1 = block_size * (block[0] - 1) + left_margin
        y1 = block_size * (block[1] - 1) + upper_margin
        pygame.draw.line(screen, BROWN, (x1, y1),
                         (x1 + block_size, y1 + block_size), block_size // 6)
        pygame.draw.line(screen, BROWN, (x1, y1 + block_size),
                         (x1 + block_size, y1), block_size // 6)

def show_message_at_rect_center(message, rect, which_font=font, color=WHITE):
    """
    Prints message to screen at a given rect's center.
    Args:
        message (str): Message to print
        rect (tuple): rectangle in (x_start, y_start, width, height) format
        which_font (pygame font object, optional): What font to use to print message. Defaults to font.
        color (tuple, optional): Color of the message. Defaults to RED.
    """
    message_width, message_height = which_font.size(message)
    message_rect = pygame.Rect(rect)
    x_start = message_rect.centerx - message_width / 2
    y_start = message_rect.centery - message_height / 2
    background_rect = pygame.Rect(
        x_start - block_size / 2, y_start, message_width + block_size, message_height)
    message_to_blit = which_font.render(message, True, color)
    screen.fill(SEA_COLOR, background_rect)
    screen.blit(message_to_blit, (x_start, y_start))

def show_final_message_at_rect_center(message, rect, which_font=font, color=WHITE):
    """
    Prints message to screen at a given rect's center.
    Args:
        message (str): Message to print
        rect (tuple): rectangle in (x_start, y_start, width, height) format
        which_font (pygame font object, optional): What font to use to print message. Defaults to font.
        color (tuple, optional): Color of the message. Defaults to RED.
    """
    message_width, message_height = which_font.size(message)
    message_rect = pygame.Rect(rect)
    x_start = message_rect.centerx - message_width / 2
    y_start = message_rect.centery - message_height / 2
    background_rect = pygame.Rect(
        x_start - block_size / 2, y_start, message_width + block_size, message_height)
    message_to_blit = which_font.render(message, True, color)
    screen.fill(BROWN, background_rect)
    screen.blit(message_to_blit, (x_start, y_start))



def ship_is_valid(ship_set, blocks_for_manual_drawing):
    """
    Checks if ship is not touching other ships
    Args:
        ship_set (set): Set with tuples of new ships' coordinates
        blocks_for_manual_drawing (set): Set with all used blocks for other ships, including all blocks around ships.

    Returns:
        Bool: True if ships are not touching, False otherwise.
    """
    return ship_set.isdisjoint(blocks_for_manual_drawing)


def check_ships_numbers(ship, num_ships_list):
    """
    Checks if a ship of particular length (1-4) does not exceed necessary quantity (4-1).

    Args:
        ship (list): List with new ships' coordinates
        num_ships_list (list): List with numbers of particular ships on respective indexes.

    Returns:
        Bool: True if the number of ships of particular length is not greater than needed,
            False if there are enough of such ships.
    """
    return (5 - len(ship)) > num_ships_list[len(ship) - 1]


def update_used_blocks(ship, method):
    for block in ship:
        for i in range(-1, 2):
            for j in range(-1, 2):
                method((block[0] + i, block[1] + j))


computer = AutoShips(0)
computer_ships_working = copy.deepcopy(computer.ships)

auto_button_place = left_margin + 17 * block_size
manual_button_place = left_margin + 20 * block_size
how_to_create_ships_message = "Как вы хотите создать корабли? Нажмите кнопку"
auto_button = Button(auto_button_place, "АВТО", how_to_create_ships_message)
manual_button = Button(manual_button_place, "ВРУЧНУЮ",
                       how_to_create_ships_message)
undo_message = "Для отмены последнего корабля нажмите кнопку"
undo_button_place = left_margin + 12 * block_size
undo_button = Button(undo_button_place, "ОТМЕНА", undo_message)


def main():
    ships_creation_not_decided = True
    ships_not_created = True
    drawing = False
    game_over = False
    computer_turn = False
    start = (0, 0)
    ship_size = (0, 0)

    rect_for_grids = (0, 0, size[0], upper_margin + 12 * block_size)
    rect_for_messages_and_buttons = (
        0, upper_margin + 11 * block_size, size[0], 5 * block_size)
    message_rect_for_drawing_ships = (undo_button.rect_for_draw[0] + undo_button.rect_for_draw[2], upper_margin + 11 * block_size, size[0] - (
            undo_button.rect_for_draw[0] + undo_button.rect_for_draw[2]), 4 * block_size)
    message_rect_computer = (left_margin - 2 * block_size, upper_margin +
                             11 * block_size, 14 * block_size, 4 * block_size)
    message_rect_human = (left_margin + 15 * block_size, upper_margin +
                          11 * block_size, 10 * block_size, 4 * block_size)
    message_rect_for_warnings = (500, -500, 1000, -800)



    human_ships_to_draw = []
    human_ships_set = set()
    used_blocks_for_manual_drawing = set()
    num_ships_list = [0, 0, 0, 0]
    screen.fill(SEA_COLOR)



    while ships_creation_not_decided:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                ships_creation_not_decided = False
                ships_not_created = False
            # If AUTO button is pressed - create human ships automatically
            elif event.type == pygame.MOUSEBUTTONDOWN and auto_button.rect.collidepoint(mouse):
                print("Clicked AUTO!", event.pos)
                human = AutoShips(15)
                human_ships_to_draw = human.ships
                human_ships_working = copy.deepcopy(human.ships)
                human_ships_set = human.ships_set
                ships_creation_not_decided = False
                ships_not_created = False
            elif event.type == pygame.MOUSEBUTTONDOWN and manual_button.rect.collidepoint(mouse):
                ships_creation_not_decided = False
        screen.blit(img2,(0,0))
        screen.blit(img2, (500,0))
        computer_grid = Grid("МОРЕ ПРОТИВНИКА", 0)
        human_grid = Grid("ВАШЕ МОРЕ", 15)
        auto_button.draw_button()
        manual_button.draw_button()
        auto_button.change_color_on_hover()
        manual_button.change_color_on_hover()
        auto_button.print_message_for_button()
        pygame.display.update()
        screen.fill(SEA_COLOR, rect_for_messages_and_buttons)

    while ships_not_created:
        screen.blit(img2,(0,0))
        screen.blit(img2, (500,0))
        computer_grid = Grid("МОРЕ ПРОТИВНИКА", 0)
        human_grid = Grid("ВАШЕ МОРЕ", 15)
        undo_button.draw_button()
        undo_button.print_message_for_button()
        undo_button.change_color_on_hover()
        mouse = pygame.mouse.get_pos()
        if not human_ships_to_draw:
            undo_button.draw_button(LIGHTER_BROWN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ships_not_created = False
                game_over = True
            elif undo_button.rect.collidepoint(mouse) and event.type == pygame.MOUSEBUTTONDOWN:
                if human_ships_to_draw:
                    screen.fill(SEA_COLOR, message_rect_for_drawing_ships)
                    deleted_ship = human_ships_to_draw.pop()
                    num_ships_list[len(deleted_ship) - 1] -= 1
                    update_used_blocks(
                        deleted_ship, used_blocks_for_manual_drawing.discard)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                x_start, y_start = event.pos
                start = x_start, y_start
                ship_size = (0, 0)
            elif drawing and event.type == pygame.MOUSEMOTION:
                x_end, y_end = event.pos
                end = x_end, y_end
                ship_size = x_end - x_start, y_end - y_start
            elif drawing and event.type == pygame.MOUSEBUTTONUP:
                x_end, y_end = event.pos
                drawing = False
                ship_size = (0, 0)
                start_block = ((x_start - left_margin) // block_size + 1,
                               (y_start - upper_margin) // block_size + 1)
                end_block = ((x_end - left_margin) // block_size + 1,
                             (y_end - upper_margin) // block_size + 1)
                if start_block > end_block:
                    start_block, end_block = end_block, start_block
                temp_ship = []
                if 15 < start_block[0] < 26 and 0 < start_block[1] < 11 and 15 < end_block[0] < 26 and 0 < end_block[
                    1] < 11:
                    screen.fill(SEA_COLOR, message_rect_for_drawing_ships)
                    if start_block[0] == end_block[0] and (end_block[1] - start_block[1]) < 4:
                        for block in range(start_block[1], end_block[1] + 1):
                            temp_ship.append((start_block[0], block))
                    elif start_block[1] == end_block[1] and (end_block[0] - start_block[0]) < 4:
                        for block in range(start_block[0], end_block[0] + 1):
                            temp_ship.append((block, start_block[1]))
                    else:
                        show_message_at_rect_center(
                            "КОРАБЛЬ СЛИШКОМ БОЛЬШОЙ!", message_rect_for_drawing_ships)
                else:
                    show_message_at_rect_center(
                        "КОРАБЛЬ ЗА ПРЕДЕЛАМИ СЕТКИ!", message_rect_for_drawing_ships)
                if temp_ship:
                    temp_ship_set = set(temp_ship)
                    if ship_is_valid(temp_ship_set, used_blocks_for_manual_drawing):
                        if check_ships_numbers(temp_ship, num_ships_list):
                            num_ships_list[len(temp_ship) - 1] += 1
                            human_ships_to_draw.append(temp_ship)
                            human_ships_set |= temp_ship_set
                            update_used_blocks(
                                temp_ship, used_blocks_for_manual_drawing.add)
                        else:
                            show_message_at_rect_center(
                                f"УЖЕ ДОСТАТОЧНО {len(temp_ship)}-ПАЛУБНЫХ КОРАБЛЕЙ", message_rect_for_drawing_ships)
                    else:
                        show_message_at_rect_center(
                            "КОРАБЛИ ПРИКАСАЮТСЯ!", message_rect_for_drawing_ships)
            if len(human_ships_to_draw) == 10:
                ships_not_created = False
                human_ships_working = copy.deepcopy(human_ships_to_draw)
                screen.fill(SEA_COLOR, rect_for_messages_and_buttons)
        pygame.draw.rect(screen, BROWN, (start, ship_size), 3)
        draw_ships(human_ships_to_draw)
        pygame.display.update()

    while not game_over:
        draw_ships(destroyed_computer_ships)
        draw_ships(human_ships_to_draw)
        if not (dotted_set | hit_blocks):
            show_message_at_rect_center(
                "ИГРА НАЧАЛАСЬ! ВАШ ХОД!", message_rect_computer)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif not computer_turn and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if (left_margin < x < left_margin + 10 * block_size) and (
                        upper_margin < y < upper_margin + 10 * block_size):
                    fired_block = ((x - left_margin) // block_size + 1,
                                   (y - upper_margin) // block_size + 1)
                    computer_turn = not check_hit_or_miss(fired_block, computer_ships_working, False, computer.ships,
                                                          computer.ships_set)
                    draw_from_dotted_set(dotted_set)
                    draw_hit_blocks(hit_blocks)
                    screen.fill(SEA_COLOR, message_rect_computer)
                    show_message_at_rect_center(
                        f"ВАШ ПОСЛЕДНИЙ ХОД: {LETTERS[fired_block[0] - 1] + str(fired_block[1])}",
                        message_rect_computer, color=WHITE)
                else:
                    show_message_at_rect_center(
                        "ВЫСТРЕЛ ЗА ПРЕДЕЛЫ СЕТКИ!", message_rect_computer)

        if computer_turn:
            set_to_shoot_from = computer_available_to_fire_set
            if around_last_computer_hit_set:
                set_to_shoot_from = around_last_computer_hit_set
            fired_block = computer_shoots(set_to_shoot_from)
            computer_turn = check_hit_or_miss(
                fired_block, human_ships_working, True, human_ships_to_draw, human_ships_set)
            show_message_at_rect_center(
                f"ПОСЛЕДНИЙ ХОД ПРОТИВНИКА: {LETTERS[fired_block[0] - 16] + str(fired_block[1])}",
                message_rect_human, color=WHITE)


        draw_from_dotted_set(dotted_set)
        draw_hit_blocks(hit_blocks)


        if not computer.ships_set:
            show_final_message_at_rect_center(
                "ВЫ ВЫИГРАЛИ!", (0, 0, size[0], size[1]), game_over_font)
        if not human_ships_set:
            show_final_message_at_rect_center(
                "ВЫ ПРОИГРАЛИ!", (0, 0, size[0], size[1]), game_over_font)

        pygame.display.update()


main()
pygame.quit()
