import pygame
import cckk.game.cckkUtils as cckkUtils
import cckk.game.cckkSprite as cckkSprite
import cckk.game.cckkColours as cckkColours

sprite_extra_styles = {
    "Label": {"fillcolour": None, "outlinecolour": None, "textsize": 36},
    "DynamicText": {"outlinecolour": None, "textsize": 36},
    "Button": {"fillcolour": "gray80", "outlinecolour": "black", "textsize": 36},
    "GameOver": {
        "textcolour": "red3",
        "textsize": 72,
        "fillcolour": "yellow1",
        "outlinecolour": "red3",
        "outlinewidth": 5,
        "width": 400,
        "height": 100,
    },
    "BoardGame_Board": {
        "fillcolour": "black",
        "outlinecolour": None,
        "altcolour": "white",
        "highlightcolour": "violetred1",
        "outlinewidth": 3,
    },
    "BoardGame_Piece": {"outlinecolour": None, "shape": "Ellipse", "piecemargin": 20},
    "ImageGrid": {"fillcolour": "black"},
}
cckkColours.stylesheet.add_stylesheet(sprite_extra_styles)


### --------------------------------------------------


class Sprite_Background(cckkSprite.Sprite):
    def __init__(self, filename, rect, name=""):
        super().__init__(name)
        self.load_image_from_file(filename, scale_to=rect.size)
        self.rect.topleft = (0, 0)


### --------------------------------------------------


class Sprite_Label(cckkSprite.Sprite_TextBox):
    def __init__(self, name_text="", rect=None, style=None):
        super().__init__(
            name_text,
            rect,
            style=cckkUtils.merge_dicts(cckkColours.stylesheet.style("Label"), style),
            auto_size=True,
            name_is_text=True,
        )


### --------------------------------------------------


class Sprite_DynamicText(cckkSprite.Sprite_TextBox):
    def __init__(self, name_text="", rect=None, style=None):
        super().__init__(
            name_text,
            rect,
            style=cckkUtils.merge_dicts(
                cckkColours.stylesheet.style("DynamicText"), style
            ),
            auto_size=False,
        )


### --------------------------------------------------


class Sprite_Button(cckkSprite.Sprite_TextBox):
    def __init__(
        self,
        name_text,
        rect=None,
        event_on_click=None,
        event_on_unclick=None,
        style=None,
    ):
        super().__init__(
            name_text,
            rect,
            style=cckkUtils.merge_dicts(cckkColours.stylesheet.style("Button"), style),
            auto_size=False,
            name_is_text=True,
        )
        self.setup_mouse_events(event_on_click, event_on_unclick)


### --------------------------------------------------


class Sprite_GameOver(cckkSprite.Sprite_TextBox):
    def __init__(self, rect, style=None):
        super().__init__(
            "Game Over",
            rect,
            style=cckkUtils.merge_dicts(
                cckkColours.stylesheet.style("GameOver"), style
            ),
            auto_size=False,
        )
        self.style_to_pos_size()
        self.rect.center = rect.center


### --------------------------------------------------


class Sprite_Grid(cckkSprite.Sprite):
    def __init__(self, name="Grid", style=None):
        super().__init__(
            name,
            style=cckkUtils.merge_dicts(
                cckkColours.stylesheet.style("Invisible"), style
            ),
        )
        self._rows = self._cols = 0
        self._cell0 = pygame.Rect(0, 0, 0, 0)
        self._xsize = self._ysize = 0

    @property
    def rows(self):
        return self._rows

    @property
    def cols(self):
        return self._cols

    @property
    def cell_size(self):
        return (self._xsize, self._ysize)

    def setup_grid(self, cols_rows, xsize_ysize, event_on_click=None):
        xsize, ysize = xsize_ysize
        if ysize is None:
            ysize = xsize
        self._xsize = xsize
        self._ysize = ysize

        cols, rows = cols_rows
        if rows is None:
            rows = cols
        self._cols = cols
        self._rows = rows

        self.rect.width = xsize * cols
        self.rect.height = ysize * rows
        self._cell0 = cckkUtils.cckkRect(0, 0, xsize, ysize)

        self.image = self.create_surface()
        self.event_on_click = event_on_click

    def cell_rect(self, col, row, relative=False):
        x = col * self._cell0.width
        y = row * self._cell0.height
        if not relative:
            x = x + self.rect.left
            y = y + self.rect.top
        return cckkUtils.cckkRect(x, y, self._cell0.width, self._cell0.height)

    def find_cell(self, x_y, allow_outside=False):
        x, y = x_y
        col = (x - self.rect.left) // self._cell0.width
        row = (y - self.rect.top) // self._cell0.height
        if self.rect.collidepoint(x, y) or allow_outside:
            return (col, row)
        else:
            return (-1, -1)

    def find_cellp(self, x_y, allow_outside=False):
        x, y = x_y
        col, row = self.find_cell(x_y, True)
        cell = self.cell_rect(col, row)
        px = 100.0 * (x - cell.left) / cell.width
        py = 100.0 * (y - cell.top) / cell.height
        if self.rect.collidepoint(x, y) or allow_outside:
            return [col, row, px, py]
        else:
            return [-1, -1, 0, 0]

    def find_cell_centre(self, x_y, allow_outside=False):
        cellp = self.find_cellp(x_y, allow_outside)
        px = cellp[2]
        py = cellp[3]

        if px > 35 and px < 65 and py > 35 and py < 65:
            return (cellp[0], cellp[1])
        else:
            return (-1, -1)


### --------------------------------------------------


class Sprite_BoardGame_Board(Sprite_Grid):
    def __init__(self, name="Board", style=None):
        super().__init__(
            name,
            style=cckkUtils.merge_dicts(
                cckkColours.stylesheet.style("BoardGame_Board"), style
            ),
        )

    def setup_board_grid(self, xsize, cols, event_on_click=None, rows=None, ysize=None):
        super().setup_grid((cols, rows), (xsize, ysize), event_on_click)

        img = None
        img_file = self.get_style("fillimage")
        if img_file is not None:
            img = cckkUtils.cckkImage()
            img.load(img_file, scale_to=self.cell_size)

        for i in range(0, self.cols):
            for j in range(0, self.rows):
                r = self.cell_rect(i, j, True)
                if (i + j) % 2 == 0:
                    col = self.get_style_colour("fillcolour")
                else:
                    col = self.get_style_colour("altcolour")
                    if col is None:
                        col = self.get_style_colour("fillcolour")
                if col is not None and self.image is not None:
                    pygame.draw.rect(self.image, col, r)
                if img is not None and self.image is not None:
                    self.image.blit(img.surface, r)
                line_col = self.get_style_colour("outlinecolour")
                line_w = self.get_style("outlinewidth", 1)
                if line_col is not None and self.image is not None:
                    pygame.draw.rect(self.image, line_col, r, line_w)

    def highlight_cells(self, cell_list, highlight_on=True):
        for c in cell_list:
            r = self.cell_rect(c[0], c[1], True)
            if highlight_on:
                col = self.get_style_colour("highlightcolour")
            else:
                col = self.get_style_colour("fillcolour")
            if col is not None and self.image is not None:
                pygame.draw.rect(self.image, col, r)
            line_col = self.get_style_colour("outlinecolour")
            if line_col != None and self.image is not None:
                pygame.draw.rect(
                    self.image, line_col, r, self.get_style("outlinewidth", 1)
                )


### --------------------------------------------------


class Sprite_BoardGame_Piece(cckkSprite.Sprite_Shape):
    def __init__(self, name, board, col=0, row=0, style=None):
        super().__init__(
            name,
            style=cckkUtils.merge_dicts(
                cckkColours.stylesheet.style("BoardGame_Piece"), style
            ),
        )
        self._row = row
        self._col = col
        self._board = board
        self._cell = self._board.cell_rect(0, 0)
        self._cell.topleft = (0, 0)
        self.set_pos()
        self.create_canvas()

    def reduce_cell(self, percentage):
        r = self._cell
        r = self._cell.inflate(
            -int(r.width * (percentage / 100.0)), -int(r.height * (percentage / 100.0))
        )
        return r

    def set_pos(self, col=None, row=None):
        if col is not None:
            self._col = col
        if row is not None:
            self._row = row
        r = self._board.cell_rect(self._col, self._row)
        self.rect.topleft = r.topleft
        self.rect.size = r.size

    def draw(self, draw_flag=cckkSprite.Sprite.DRAW_AS_REQD, clear_draw_reqd=True):
        if self._draw_reqd or draw_flag:
            self._draw_reqd = False
            fill_col = self.get_style_colour("fillcolour")
            line_col = self.get_style_colour("outlinecolour")
            line_width = self.get_style("outlinewidth", 1)
            margin = self.get_style("piecemargin")

            if self.get_style("shape") == "Ellipse":
                r = self.reduce_cell(margin)
                if fill_col is not None and self.image is not None:
                    pygame.draw.ellipse(self.image, fill_col, r)
                if line_col is not None and self.image is not None:
                    pygame.draw.ellipse(self.image, line_col, r, line_width)
            if self.get_style("shape") == "Rectangle":
                r = self.reduce_cell(margin)
                if fill_col is not None and self.image is not None:
                    pygame.draw.rect(self.image, fill_col, r)
                if line_col is not None and self.image is not None:
                    pygame.draw.rect(self.image, line_col, r, line_width)
            self.set_pos()

        if clear_draw_reqd:
            self._draw_reqd = False

    def flip(self):
        self.swap_colours()


### --------------------------------------------------


class Sprite_ImageGrid(Sprite_Grid):
    def __init__(self, name="Grid", style=None):
        super().__init__(
            name,
            style=cckkUtils.merge_dicts(
                cckkColours.stylesheet.style("Invisible"),
                cckkColours.stylesheet.style("ImageGrid"),
                style,
            ),
        )

    def setup_image_grid(self, spritesheet, sprites):
        img = cckkUtils.cckkImage()
        img.set_spritesheet(
            spritesheet[0], spritesheet[1], spritesheet[2], scale_to=self.cell_size
        )
        if self.image is not None:
            for i in range(0, self.rows):
                for j in range(0, self.cols):
                    img.spritesheet_image(sprites[i * self.cols + j])
                    r = self.cell_rect(j, i, True)
                    self.image.blit(img.surface, r)


### --------------------------------------------------


class Sprite_ImageGridActor(cckkSprite.Sprite_Animation, cckkUtils.GridActor):
    def __init__(self, name, start_cell, cell0, speed=1, move_timer=None):
        cckkUtils.GridActor.__init__(self, name, start_cell, speed, move_timer)
        cckkSprite.Sprite_Animation.__init__(self, name)
        self._image_dir = None
        self._cell0 = cell0
        self.load_image()
        self.image_dir = "R"
        self.move_to(start_cell)

    @property
    def centre(self):
        return self.rect.center

    @property
    def direction(self):
        return self._curr_dir

    @direction.setter
    def direction(self, new_direction):
        if new_direction in ["U", "D", "L", "R"]:
            self._curr_dir = self.image_dir = new_direction

    @property
    def image_dir(self):
        return self._image_dir

    @image_dir.setter
    def image_dir(self, new_direction):
        if new_direction in ["U", "D", "L", "R"] and self._image_dir != new_direction:
            self._image_dir = new_direction
            self.set_animation(self.name + new_direction, cckkUtils.ANIMATE_SHUTTLE, 2)
            self._draw_reqd = True

    def _update_image_pos(self):
        col, row = self.cell_float
        self.rect.centerx = self._cell0.left + col * self._cell0.width
        self.rect.centery = self._cell0.top + row * self._cell0.height

    def move_dir(self, change_dir=False):
        if super().move_dir(change_dir):
            self._update_image_pos()

    def move_to(self, cell_pos=None, new_dir=None):
        super().move_to(cell_pos, new_dir)
        self._update_image_pos()
        self.image_dir = new_dir


### --------------------------------------------------
