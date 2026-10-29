# To Do: Add default style to app_config
# To Do: Change "GameOver" to "EndGame"
# To Do: msecs_per_image not implemented
# To Do: Change find_collisions to use SpriteGroup.collide()
# To Do: Delete Sprite_DynamicText
# To Do: Modify _load_image_from_file to use cckkImage. Delete?
# To Do: Delete load_animation???
# To Do: Move SpriteManager to cckkSpriteManager

import pygame
import pygame.gfxdraw
import uuid
from math import sin, cos
import cckk.game.cckkUtils as cckkUtils
import cckk.game.cckkColours as cckkColours

sprite_styles = {
    "Shape": {
        "fillcolour": "white",
        "outlinecolour": "black",
        "outlinewidth": 3,
        "altcolour": "black",
        "highlightcolour": "yellow",
        "shape": "Rectangle",
        "xpos": None,
        "ypos": None,
        "width": None,
        "height": None,
        "invisible": False,
    },
    "Invisible": {"fillcolour": None, "outlinecolour": None, "textsize": 36},
    "TextBox": {
        "textcolour": "black",
        "textsize": 36,
        "align_horiz": "C",
        "align_vert": "M",
        "textformat": "{0}",
    },
}
cckkColours.stylesheet.add_stylesheet(sprite_styles)

# stylesheet.style("Shape")


class Sprite(pygame.sprite.Sprite):
    DRAW_AS_REQD = 0
    DRAW_ALWAYS = 1
    DRAW_AFTER_CLEAR = 2

    def __init__(self, name="", style=None, filename=None):
        super().__init__()
        self._desc = {}
        self.set_config("name", name)
        self.set_config("class", self.__class__.__name__)
        self.set_config("uuid", uuid.uuid4())
        self.rect = cckkUtils.MovingRect()
        self._image = cckkUtils.cckkImage()
        self.event_on_click = None
        self.event_on_unclick = None
        self._draw_reqd = False
        self._game_active = None
        self._style = cckkColours.Style()
        self.update_style(style)
        self.load_image_from_file(filename)

    def get_config(self, attribute, no_value=None):
        if attribute in self._desc:
            return self._desc[attribute]
        else:
            return no_value

    def set_config(self, attribute, value):
        self._desc[attribute] = value

    def get_style(self, attribute, default=None):
        return self._style.get(attribute, default)

    def get_style_colour(self, attribute, default=None) -> tuple[int, int, int] | None:
        return self._style.get_rgb(attribute, default)

    def set_style(self, attribute, new_value):
        self._style[attribute] = new_value
        self._draw_reqd = True
        if attribute in ("xpos", "ypos", "width", "height"):
            self.style_to_pos_size()

    def update_style(self, *updated_styles):
        for s in updated_styles:
            if s is not None:
                self._style.update(s)
                for key in s:
                    if key in ("xpos", "ypos", "width", "height"):
                        self.style_to_pos_size()
        self._draw_reqd = True

    def style_to_pos_size(self):
        x = self.get_style("xpos")
        y = self.get_style("ypos")
        w = self.get_style("width")
        h = self.get_style("height")
        if x is not None:
            self.rect.left = x
        if y is not None:
            self.rect.top = y
        if w is not None:
            self.rect.width = w
        if h is not None:
            self.rect.height = h
        if w is not None or h is not None:
            self.image = self.create_surface()
            self._image_size_to_rect()

    @property
    def name(self):
        return self.get_config("name")

    @property
    def uuid(self):
        return self.get_config("uuid")

    @property
    def game_is_active(self):
        return self._game_active

    @property
    def image(self):
        return self._image.surface

    @image.setter
    def image(self, new_image):
        self._image.surface = new_image
        self._draw_reqd = True

    def _image_size_to_rect(self):
        self.rect.width = self.image.get_rect().width if self.image is not None else 0
        self.rect.height = self.image.get_rect().height if self.image is not None else 0

    @property
    def cckkimage(self):
        return self._image

    def _load_image_from_file(self, filename, crop=None, scale_to=None):
        img = cckkUtils.cckkImage()
        ret_image = image = pygame.image.load(img.image_path(filename)).convert_alpha()
        if crop is not None:
            # Crop the imported image by ... crop[left, right, top, bottom]
            crop_rect = image.get_rect()
            crop_rect.width = crop_rect.width - crop[0] - crop[1]
            crop_rect.left = crop[0]
            crop_rect.height = crop_rect.height - crop[2] - crop[3]
            crop_rect.top = crop[2]
            ret_image = pygame.Surface(crop_rect.size, pygame.SRCALPHA)
            ret_image.blit(image, (0, 0), crop_rect)
        if scale_to is not None:
            ret_image = pygame.transform.smoothscale(ret_image, scale_to)
        return ret_image

    def load_image(self):
        pass

    def load_image_from_file(
        self, filename, img_process=None, crop=None, scale_to=None, create_mask=True
    ):
        if filename is None:
            return

        if scale_to == "style":
            w = self.get_style("width")
            h = self.get_style("height")
            if w is None or h is None:
                scale_to = None
            else:
                scale_to = (w, h)

        self._image.load(
            filename, img_process=img_process, crop=crop, scale_to=scale_to
        )
        self._image_size_to_rect()
        if create_mask:
            self.create_mask()

    def load_image_from_spritesheet(
        self,
        spritesheet_filename,
        cols,
        rows,
        sprite_number,
        img_process=None,
        crop=None,
        scale_to=None,
        create_mask=True,
    ):
        if scale_to == "style":
            w = self.get_style("width")
            h = self.get_style("height")
            if w is None or h is None:
                scale_to = None
            else:
                scale_to = (w, h)

        img = cckkUtils.cckkImage()
        img.set_spritesheet(
            spritesheet_filename, cols, rows, img_process, crop=crop, scale_to=scale_to
        )
        self.image = img.spritesheet_image(sprite_number)
        self._image_size_to_rect()
        if create_mask:
            self.create_mask()

    def create_surface(self, width=None, height=None, per_pixel_alpha=True):
        # logger.debug("create_surface()")
        if width is None:
            width = self.rect.width
        if height is None:
            height = self.rect.height
        if per_pixel_alpha:
            return pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        else:
            return pygame.Surface((width, height)).convert()

    def add_image(self, image, dest=(0, 0)):
        return self.image.blit(image, dest) if self.image is not None else None

    def process_image(self, commands_values, **kwargs):
        self._image.process_list(commands_values, **kwargs)

    def setup_mouse_events(self, event_on_click, event_on_unclick=None):
        if type(event_on_click).__name__ == "Event" or event_on_click == None:
            self.event_on_click = event_on_click
        else:
            cckkUtils.logger.error(
                "Sprite.setup_mouse_events(): event_on_click must be of type Event"
            )
        if type(event_on_unclick).__name__ == "Event" or event_on_unclick == None:
            self.event_on_unclick = event_on_unclick
        else:
            cckkUtils.logger.error(
                "Sprite.setup_mouse_events(): event_on_unclick must be of type Event"
            )
        self.event_on_unclick = event_on_unclick

    def create_mask(self):
        self.mask = (
            pygame.mask.from_surface(self.image) if self.image is not None else None
        )

    def collide(self, sprite_group, collided=pygame.sprite.collide_mask):
        group2 = SpriteGroup("temp")
        for s in sprite_group:
            if s.image is not None:
                group2.add(s)

        return pygame.sprite.spritecollide(
            self, group2, dokill=False, collided=collided
        )

    def draw(self, draw_flag=DRAW_AS_REQD, clear_draw_reqd=True):
        if self.image is None or draw_flag == Sprite.DRAW_AFTER_CLEAR:
            self.image = self.create_surface()
            self._image_size_to_rect()
        if clear_draw_reqd:
            self._draw_reqd = False

    def update(self):
        super().update()
        if self.get_config("auto_move_physics", False):
            self.rect.move_physics()

    def slow_update(self):
        pass

    def start_game(self):
        self._game_active = True

    def end_game(self):
        self._game_active = False


# --------------------------------------------------


class Sprite_Animation(Sprite):
    def __init__(self, name=""):
        super().__init__(name)
        self._animations = {}
        self._anim_config = cckkUtils.Animation_Counter()
        self._anim_name = None

    def load_animation(
        self, set_name, file_format, count, count_from=1, crop=None, create_mask=True
    ):
        self._animations[set_name] = []
        for i in range(count_from, count_from + count):
            filename = file_format.format(i)
            self._animations[set_name].append(
                self._load_image_from_file(filename, crop)
            )

        self.image = self._animations[set_name][0]
        self._image_size_to_rect()
        if create_mask:
            self.create_mask()

    def load_spritesheet(
        self,
        set_name,
        spritesheet_filename,
        cols,
        rows,
        create_mask=True,
        set_anim=False,
        start=None,
        end=None,
        length=None,
        img_process=None,
    ):
        self._animations[set_name] = []
        if start is None:
            start = 0
        if end is None:
            if length is None:
                end = cols * rows
            else:
                end = start + length

        spritesheet = cckkUtils.cckkImage()
        spritesheet.set_spritesheet(
            spritesheet_filename, cols, rows, img_process=img_process
        )
        for i in range(start, end):
            self._animations[set_name].append(spritesheet.spritesheet_image(i))

        self.image = self._animations[set_name][0]
        self._image_size_to_rect()
        if create_mask:
            self.create_mask()

        if set_anim:
            self.set_animation(set_name)

    def set_animation(
        self, new_animation, mode=cckkUtils.ANIMATE_LOOP, loops_per_image=None
    ):
        if self._anim_name != new_animation and new_animation in self._animations:
            self._anim_name = new_animation
            self._anim_config.setup(
                len(self._animations[new_animation]),
                mode,
                loops_per_image if loops_per_image is not None else 1,
            )
            self._draw_reqd = True

    def draw(self, draw_flag=Sprite.DRAW_ALWAYS, clear_draw_reqd=True):
        super().draw(draw_flag, clear_draw_reqd=False)
        if self._draw_reqd or draw_flag > Sprite.DRAW_AS_REQD:
            anim_name = self._anim_name
            if anim_name is not None and anim_name != "":
                if self._anim_config.next_loop():
                    self.image = self._animations[anim_name][
                        self._anim_config.current_image
                    ]
        if clear_draw_reqd:
            self._draw_reqd = False

    def create_mask_anim(self, using_animation, using_frame):
        reset_animation = None
        reset_frame = None

        if self._anim_name != using_animation:
            reset_animation = self._anim_name
            reset_frame = self._anim_config.current_image
            self._anim_name = using_animation
            self._anim_config.current_image = using_frame
        elif using_frame != self._anim_config.index:
            reset_frame = self._anim_config.current_image
            self._anim_config.current_image = using_frame

        self.create_mask()

        if reset_animation is not None:
            self._anim_name = reset_animation
        if reset_frame is not None:
            self._anim_config.current_image = reset_frame


# --------------------------------------------------


class Sprite_Shape(Sprite):
    def __init__(self, name="", rect=None, style=None):
        super().__init__(
            name,
            style=cckkUtils.merge_dicts(cckkColours.stylesheet.style("Shape"), style),
        )
        self._pointlist = None
        self._pie_angles = None
        if rect is not None:
            self.rect.topleft = rect.topleft
            self.rect.size = rect.size
        self._draw_reqd = True

    @property
    def shape(self):
        return self.get_style("shape")

    @shape.setter
    def shape(self, new_shape):
        # Rectangle, Ellipse, Polygon, Arc
        self.set_style("shape", new_shape)

    @property
    def invisible(self):
        return self.get_style("invisible", False)

    @invisible.setter
    def invisible(self, new_invisible):
        self.set_style("invisible", new_invisible)
        self.draw(Sprite.DRAW_AFTER_CLEAR)

    def setup_polygon(self, pointlist):
        self._pointlist = pointlist.copy()
        self._draw_reqd = True

    def setup_pie(self, start_angle, stop_angle):
        self._pie_angles = [start_angle * 3.14159 / 180, stop_angle * 3.14159 / 180]
        x0 = self.rect.width / 2
        y0 = self.rect.height / 2

        ndiv = 360
        delta = (self._pie_angles[1] - self._pie_angles[0]) / ndiv
        angles = [self._pie_angles[0] + i * delta for i in range(ndiv + 1)]
        self._pointlist = [(x0, y0)] + [
            (
                x0 + self.rect.width / 2 * cos(theta),
                y0 - self.rect.width / 2 * sin(theta),
            )
            for theta in angles
        ]
        self._draw_reqd = True

    def create_canvas(self, width=None, height=None):
        self.image = self.create_surface(width, height, True)
        self._image_size_to_rect()
        self._draw_reqd = True

    def swap_colours(self):
        c = self.get_style("fillcolour")
        self.set_style("fillcolour", self.get_style("altcolour"))
        self.set_style("altcolour", c)
        self._draw_reqd = True

    def draw(self, draw_flag=Sprite.DRAW_AS_REQD, clear_draw_reqd=True):
        super().draw(draw_flag, clear_draw_reqd=False)
        if (self._draw_reqd or draw_flag > Sprite.DRAW_AS_REQD) and not self.invisible:
            draw_rect = self.rect.copy()
            draw_rect.topleft = (0, 0)
            fill_col = self.get_style_colour("fillcolour")
            line_col = self.get_style_colour("outlinecolour")

            if self.shape is not None and self.image is not None:
                if self.shape.lower() == "ellipse":
                    if fill_col is not None:
                        pygame.draw.ellipse(self.image, fill_col, draw_rect)
                    if line_col is not None:
                        olw = self.get_style("outlinewidth")
                        pygame.draw.ellipse(
                            self.image,
                            line_col,
                            draw_rect,
                            olw if olw is not None else 1,
                        )

                # elif self.shape.lower() == "arc":
                #     if (fill_col is not None):
                #         pygame.gfxdraw.pie(self.image, draw_rect.centerx, draw_rect.centery, draw_rect.width//2, self._arc_angles[0], self._arc_angles[1], (255,255,0))
                #     if (line_col is not None):
                #         pygame.draw.arc(self.image, line_col, draw_rect, self._arc_angles[0], self._arc_angles[1], self.get_style("outlinewidth"))

                elif self.shape.lower() == "polygon" or self.shape.lower() == "pie":
                    if self._pointlist is not None:
                        if fill_col is not None:
                            pygame.draw.polygon(self.image, fill_col, self._pointlist)
                        if line_col is not None:
                            olw = self.get_style("outlinewidth")
                            pygame.draw.polygon(
                                self.image,
                                line_col,
                                self._pointlist,
                                olw if olw is not None else 1,
                            )

                else:  # Rectangle
                    if fill_col is not None:
                        pygame.draw.rect(self.image, fill_col, draw_rect)
                    if line_col is not None:
                        olw = self.get_style("outlinewidth")
                        pygame.draw.rect(
                            self.image,
                            line_col,
                            draw_rect,
                            olw if olw is not None else 1,
                        )

        if clear_draw_reqd:
            self._draw_reqd = False


# --------------------------------------------------


class Sprite_TextBox(Sprite_Shape):
    def __init__(
        self, name_text="", rect=None, style=None, auto_size=False, name_is_text=True
    ):
        super().__init__(
            name_text,
            rect,
            style=cckkUtils.merge_dicts(cckkColours.stylesheet.style("TextBox"), style),
        )
        if name_is_text:
            self._text = name_text
        else:
            self._text = None
        self._font = None
        self._auto_size = auto_size
        if rect is not None:
            if rect.width > 0 and rect.height > 0:
                self._auto_size = False
        self._draw_reqd = True
        self.style_to_pos_size()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_text):
        self._text = new_text
        self._draw_reqd = True

    @property
    def text_format(self):
        return

    @text_format.setter
    def text_format(self, new_text_format):
        self.set_style("textformat", new_text_format)
        self._draw_reqd = True

    def set_text_format(self, new_text_format, *args):
        self.text_format = new_text_format
        text_fmt = self.get_style("textformat")
        if new_text_format is None:
            self.text = ""
        else:
            self.text = new_text_format.format(*args)

    def set_text(self, *args):
        text_fmt = self.get_style("textformat")
        if text_fmt is None:
            self.text = ""
        else:
            self.text = text_fmt.format(*args)

    @property
    def font(self):
        if self._font is None:
            ts = self.get_style("textsize")
            self._font = pygame.font.Font(None, ts if ts is not None else 12)
        return self._font

    def draw(self, draw_flag=Sprite.DRAW_AS_REQD, clear_draw_reqd=True):
        super().draw(draw_flag, clear_draw_reqd=False)
        if (self._draw_reqd or draw_flag > Sprite.DRAW_AS_REQD) and not self.invisible:
            tc = self.get_style_colour("textcolour")
            text_image = self.font.render(
                self.text, True, tc if tc is not None else (0, 0, 0)
            )
            text_rect = text_image.get_rect()

            if self._auto_size:
                self.image = self.create_surface(text_rect.width, text_rect.height)
                self._image_size_to_rect()
                super().draw(Sprite.DRAW_ALWAYS, clear_draw_reqd=False)

            if self.get_style("fillcolour") is None:
                self.image = self.create_surface()
                super().draw(Sprite.DRAW_ALWAYS, clear_draw_reqd=False)

            if self.get_style("align_horiz") == "L":
                text_rect.left = 0
            elif self.get_style("align_horiz") == "C":
                text_rect.centerx = int(self.rect.width / 2)
            elif self.get_style("align_horiz") == "R":
                text_rect.right = self.rect.width

            if self.get_style("align_vert") == "T":
                text_rect.top = 0
            elif self.get_style("align_vert") == "M":
                text_rect.centery = int(self.rect.height / 2)
            elif self.get_style("align_vert") == "B":
                text_rect.bottom = self.rect.height

            if self.image is not None:
                self.image.blit(text_image, text_rect)

        if clear_draw_reqd:
            self._draw_reqd = False


# --------------------------------------------------


class SpriteGroup(pygame.sprite.LayeredUpdates):
    def collide(
        self,
        sprite_group,
        dokilla=False,
        dokillb=False,
        collided=pygame.sprite.collide_mask,
    ):
        coll_dict = pygame.sprite.groupcollide(
            self, sprite_group, dokilla, dokillb, collided
        )
        return coll_dict

    def __init__(self, name, *sprites, **kwargs):
        super().__init__(*sprites, **kwargs)
        self._desc = {}
        self.set_config("name", name)
        self.rect = None

    def get_config(self, attribute, no_value=None):
        if attribute in self._desc:
            return self._desc[attribute]
        else:
            return no_value

    def set_config(self, attribute, value):
        self._desc[attribute] = value

    @property
    def name(self):
        return self.get_config("name")

    def draw_sprites(self, image):
        for s in self.sprites():
            s.image = image
            s.draw()


# --------------------------------------------------


class SpriteGridSet(SpriteGroup):
    def __init__(self, name, rect, xcols, yrows, margin=0):
        super().__init__(name)
        self.rect = rect
        self.xcols = xcols
        self.yrows = yrows
        self.margin = margin

    def add_shape_xy(self, sprite, x, y):
        w = (self.rect.width - (self.xcols - 1) * self.margin) / self.xcols
        h = (self.rect.height - (self.yrows - 1) * self.margin) / self.yrows
        l = self.rect.left + (self.rect.width * x) / self.xcols
        t = self.rect.top + (self.rect.height * y) / self.yrows
        sprite.rect = cckkUtils.cckkRect(l, t, w, h)
        sprite.set_config("xcol", x)
        sprite.set_config("yrow", y)
        self.add(sprite)

    def find_shape_xy(self, x, y):
        ret_sprite = None
        for s in self.sprites():
            if s.get_config("xcol") == x and s.get_config("yrow") == y:
                ret_sprite = s
        return ret_sprite


# --------------------------------------------------
