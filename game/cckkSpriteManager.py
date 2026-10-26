import pygame
import cckk.game.cckkUtils as cckkUtils
import cckk.game.cckkSprite as cckkSprite
import cckk.game.cckkSpriteExtra as cckkSpriteExtra
import cckk.game.cckkApp as cckkApp

# --------------------------------------------------


class SpriteManager(pygame.sprite.LayeredUpdates):
    def __init__(self, name, **sm_config):
        super().__init__()
        self.name = name
        self._game_active = False

        self._sm_config = {}
        for key, value in sm_config.items():
            self.set_config(key, value)

        if self.get_config("control_type") is None:
            self.set_config("control_type", cckkUtils.CONTROL_KEYBOARD+cckkUtils.CONTROL_MOUSE)

    @property
    def game_is_active(self):
        return self._game_active

    @property
    def player(self):
        player = self.get_config("player")
        if player is not None:
            return player
        else:
            return self.get_config("Player")

    @property
    def use_keyboard(self):
        return ((self.get_config("control_type") & cckkUtils.CONTROL_KEYBOARD) > 0)

    @property
    def use_mouse(self):
        return ((self.get_config("control_type") & cckkUtils.CONTROL_MOUSE) > 0)

    @property
    def use_joystick(self):
        return ((self.get_config("control_type") & cckkUtils.CONTROL_JOYSTICK) > 0)

    def get_config(self, attribute, default=None):
        try:
            return self._sm_config.get(attribute, default)
        except AttributeError:
            return default

    def set_config(self, attribute, value):
        self._sm_config[attribute] = value

    def get_app_config(self, attribute, default=None):
        app = self.get_config("cdkkApp", None)
        if app is not None:
            return app.get_config(attribute, default)
        else:
            return default

    @property
    def app_boundary(self):
        app = self.get_config("cdkkApp", None)
        if app is None:
            app = cckkApp._cdkkApp
        if app is not None:
            return app.boundary
        else:
            return None

    def draw(self, surface):
        for s in self.sprites():
            s.draw()  # Ask each sprite to draw its image attribute and update rect
        super().draw(surface)

    def sprite(self, name):
        ret_sprite = None
        for s in self.sprites():
            if s.name == name:
                ret_sprite = s
        return ret_sprite

    def find_sprites_by_desc(self, attr1, value1, attr2=None, value2=None):
        ret_sprites = []
        for s in self.sprites():
            found = (s.get_config(attr1) == value1)
            if found and attr2 is not None and value2 is not None:
                found = (s.get_config(attr2) == value2)
            if found:
                ret_sprites.append(s)
        return ret_sprites

    def find_sprites_by_name(self, name):
        return self.find_sprites_by_desc("name", name)

    def find_sprite_by_uuid(self, uuid):
        result = self.find_sprites_by_desc("uuid", uuid)
        if len(result) == 0:
            return None
        else:
            return result[0]

    def kill_uuid(self, uuid):
        found = False
        if uuid is not None:
            s = self.find_sprite_by_uuid(uuid)
            if s is not None:
                found = True
                s.kill()
        return found

    def kill_sprites_by_desc(self, attr1, value1, attr2=None, value2=None):
        sprites = self.find_sprites_by_desc(attr1, value1, attr2, value2)
        for s in sprites:
            s.kill()
        return len(sprites)

    def find_collisions(self):
        sprite_dict = pygame.sprite.groupcollide(self, self, False, False)
        self_collisions = []
        for spr in sprite_dict:
            sprite_dict[spr].remove(spr)
            if len(sprite_dict[spr]) == 0:
                self_collisions.append(spr)

        for spr in self_collisions:
            sprite_dict.pop(spr)

        sprite_collisions = []
        for spr, spr_list in sprite_dict.items():
            sprite_collisions.append((spr, spr_list[0].rect))

        return sprite_collisions

    def find_click(self, x, y, click_event=True):
        sprite_str = ""
        for s in self.sprites():
            if s.rect.collidepoint(x, y) and sprite_str == "":
                if s.event_on_click != None and click_event:
                    sprite_str = s.name
                    ev = s.event_on_click
                    ev.pos = x, y
                    cckkUtils.EventManager.post(ev)
                elif s.event_on_unclick != None and not click_event:
                    sprite_str = s.name
                    ev = s.event_on_unclick
                    ev.pos = x, y
                    cckkUtils.EventManager.post(ev)
        return sprite_str

    def event(self, e):
        dealt_with = False
        if e.type == cckkUtils.EVENT_GAME_CONTROL:
            if e.action == "MouseLeftClick" or e.action == "MouseUnclick":
                x, y = e.info['pos']
                sprite_str = self.find_click(
                    x, y, (e.action == "MouseLeftClick"))
                dealt_with = (sprite_str != "")
            elif e.action == "KillSpriteUUID":
                dealt_with = self.kill_uuid(e.info['uuid'])
        return dealt_with

    def cleanup(self):
        pass

    def slow_update(self):
        for s in self.sprites():
            s.slow_update()

    def start_game(self):
        self._game_active = True
        for s in self.sprites():
            s.start_game()

    def end_game(self):
        for s in self.sprites():
            s.end_game()
        self._game_active = False

# --------------------------------------------------


class SM_Scoreboard(SpriteManager):
    def __init__(self, game_time=None, limits=None, score_style=None, timer_style=None, fps_style=None, gameover_style=None, name="Scoreboard Manager"):
        super().__init__(name)
        if limits is None:
            limits = self.app_boundary

        default_style = {"fillcolour": None,
                         "outlinecolour": None, "align_horiz": "L"}
        score_style = cckkUtils.merge_dicts(default_style, score_style)
        timer_style = cckkUtils.merge_dicts(default_style, timer_style)
        fps_style = cckkUtils.merge_dicts(default_style, {"invisible": True}, fps_style)

        self._score_value = 0
        self.score_text = cckkSprite.Sprite_TextBox(
            "Score", cckkUtils.cckkRect(70, 10, 200, 40), score_style)
        self.score_text.set_text_format("Score: {0}", self._score_value)
        self.add(self.score_text)

        self._game_time = 0
        self.game_time = game_time
        self.timer_text = cckkSprite.Sprite_TextBox("Time Left", cckkUtils.cckkRect(
            limits.width - 250, 10, 200, 40), timer_style)
        self.timer_text.set_text_format("Time Left: {0:0.1f}",
                                        self.time_left)
        self.add(self.timer_text)

        self.fps_text = cckkSprite.Sprite_TextBox("FPS", cckkUtils.cckkRect(
            limits.centerx-100, 10, 200, 40), fps_style)
        self.fps_text.set_text_format("FPS: {0:4.1f}", 0)
        self.add(self.fps_text)

        self.game_over = cckkSpriteExtra.Sprite_GameOver(limits, gameover_style)

    @property
    def score(self):
        return self._score_value

    @score.setter
    def score(self, new_score):
        self._score_value = new_score
        self.score_text.set_text(self.score)

    @property
    def game_time(self):
        return self._game_time

    @game_time.setter
    def game_time(self, new_game_time):
        self._game_time = new_game_time
        if new_game_time is not None:
            self._timer = cckkUtils.Timer(self.game_time, cckkUtils.EVENT_GAME_TIMER_1,
                                auto_start=False)
        else:
            self._timer = None

    @property
    def time_left(self):
        if self._timer is None:
            return 0
        else:
            return self._timer.time_left

    def set_fps(self, new_fps):
        self.fps_text.set_text(new_fps)

    def event(self, e):
        dealt_with = super().event(e)
        if not dealt_with and e.type == cckkUtils.EVENT_GAME_CONTROL:
            dealt_with = True
            if e.action == "UpdateScore":
                self.score = self.score + e.info['score']
            elif e.action == "IncreaseTime":
                if self._timer is not None:
                    self._timer.extend_timer(e.info["increment"])
            elif e.action == "ClearGameOver":
                self.clear_game_over()
            else:
                dealt_with = False
        return dealt_with

    def slow_update(self):
        if self.game_is_active:
            self.timer_text.set_text(self.time_left)
            app = self.get_config("cdkkApp", None)
            self.set_fps(app.loops_per_sec)

    def start_game(self):
        super().start_game()
        self.score = 0
        if self._timer is not None:
            self._timer.start()
        self.timer_text.set_text(self.time_left)
        self.clear_game_over()

    def end_game(self):
        self.add(self.game_over)
        if self.time_left < 0.25:
            self.timer_text.set_text(0)
        self.set_fps(0)
        super().end_game()

    def clear_game_over(self):
        self.remove(self.game_over)

# --------------------------------------------------


class SM_SplashScreen(SpriteManager):
    def __init__(self, limits, display_time, filename):
        super().__init__("Splash Screen Manager")
        splash = cckkSprite.Sprite(name="Splash Screen")
        splash.load_image_from_file(filename)
        splash.rect.center = limits.center
        self.add(splash)
        self._splash_displayed = True
        self._clear_timer = cckkUtils.Timer(display_time, cckkUtils.EVENT_GAME_FLOW)

    def clear_splash(self):
        self.empty()
        self._splash_displayed = False

        if self.get_app_config("auto_start") == True:
            logger.warning(
                'Splash Screen Manager will not work as auto_start is set to True.')

    def start_game(self):
        super().start_game()
        self.clear_splash()

    def event(self, e):
        dealt_with = super().event(e)
        if not dealt_with and e.type == cckkUtils.EVENT_GAME_FLOW:
            if self._splash_displayed:
                self.clear_splash()
                dealt_with = True
        return dealt_with

# --------------------------------------------------
