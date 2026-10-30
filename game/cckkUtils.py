# To Do: Add img_process options: relative & absolute
# To Do: Implement bounce_cor per limit, for x & y

import pygame
import math
from collections import deque
import random
import os
import readchar
import re

# --------------------------------------------------

import logging
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger()
# logger.critical('This is a critical message.')
# logger.error('This is an error message.')
# logger.warning('This is a warning message.')
# logger.info('This is an informative message.')
# logger.debug('This is a low-level debug message.')
# logger.setLevel(logging.DEBUG)
# logger.setLevel(logging.NOTSET)

# --------------------------------------------------


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        if dictionary is not None:
            result.update(dictionary)
    return result

# --------------------------------------------------

def read_single_key(match_pattern=None, as_upper=True, as_int=False):
    ret_code = None
    wait_for_key = True

    while wait_for_key:
        ch = msvcrt.getch().decode('ASCII')
        wait_for_key = False
        if match_pattern is not None:
            if re.match(match_pattern, ch):
                ret_code = ch
            else:
                wait_for_key = True
        else:
            ret_code = ch

    if as_int:
        ret_code = int(ret_code)
    elif as_upper:
        ret_code = ret_code.upper()

    return ret_code

def read_key(match_pattern=None, as_upper=True, as_int=False, multi_key=False):
    if not multi_key:
        return read_single_key(match_pattern, as_upper, as_int)
    else:
        more_keys = True
        ret_code = ""
        while more_keys:
            ch = read_single_key()
            if ch == '\r':
                more_keys = False
            elif match_pattern is not None:
                ret_code = ret_code + ch
                if re.match(match_pattern, ret_code):
                    more_keys = False

        if match_pattern is not None:
            if not re.match(match_pattern, ret_code):
                ret_code = None
        elif as_int:
            ret_code = int(ret_code)
        elif as_upper:
            ret_code = ret_code.upper()

        return ret_code

# --------------------------------------------------

# Sprite bounces on its ...
BOUNCE_LEFT = 1
BOUNCE_RIGHT = 2
BOUNCE_TOP = 4
BOUNCE_BOTTOM = 8
BOUNCE_VERTICAL = BOUNCE_LEFT + BOUNCE_RIGHT
BOUNCE_HORIZONTAL = BOUNCE_TOP + BOUNCE_BOTTOM

# Limit Types
LIMIT_KEEP_INSIDE = 1              # Keep inside the limits
LIMIT_KEEP_OUTSIDE = 2             # Keep outside the limits
# Overlap; compare top-left corners (destination)
LIMIT_OVERLAP = 4
LIMIT_COLLISION = 8                # Collision with another moving object
LIMIT_MOVE_TO = 16                 # Move towards the limit (e.g. magnet)

# Action at Limits
AT_LIMIT_X_HOLD_POS_X = 1          # At X limit, hold X position
AT_LIMIT_Y_HOLD_POS_Y = 2          # At Y limit, hold Y position
AT_LIMIT_X_CLEAR_VEL_X = 4         # At X limit, clear X velocity
AT_LIMIT_Y_CLEAR_VEL_Y = 8         # At Y limit, clear Y velocity
AT_LIMIT_XY_CLEAR_VEL_XY = 16      # At X or Y limit, clear X & Y velocities
AT_LIMIT_X_BOUNCE_X = 32           # At X limit, negate X velocity
AT_LIMIT_Y_BOUNCE_Y = 64           # At Y limit, negate Y velocity
AT_LIMIT_BOUNCE = 32+64            # At X/Y limit, negate X/Y velocity
AT_LIMIT_X_MOVE_TO_X = 128         # At X limit, move to X
AT_LIMIT_Y_MOVE_TO_Y = 256         # At Y limit, move to Y
AT_LIMIT_MOVE_TO_XY = 128+256      # At X/Y limit, move to X/Y
AT_LIMIT_X_DO_NOTHING = 512        # At X limit, do nothing
AT_LIMIT_Y_DO_NOTHING = 1024       # At Y limit, do nothing
AT_LIMIT_XY_DO_NOTHING = 512+1024  # At X & Y limit, do nothing
# At X/Y limit, hold X&Y positions and clear X & Y velocities
AT_LIMIT_STOP = 2048

# At Limit
AT_LIMIT_LEFT = 1
AT_LIMIT_RIGHT = 2
AT_LIMIT_TOP = 4
AT_LIMIT_BOTTOM = 8
AT_LIMIT_INSIDE_X = 16
AT_LIMIT_INSIDE_Y = 32

CONTROL_KEYBOARD = 1
CONTROL_MOUSE = 2
CONTROL_JOYSTICK = 4

# --------------------------------------------------

def rect_to_debug_str(r):
    return "Left-Top=({0},{1}), Width-Height=({2},{3})".format(r.left, r.top, r.width, r.height)

# --------------------------------------------------


class Physics_Motion:
    def __init__(self):
        self._position = [0, 0]
        self._velocity = [0.0, 0.0]
        self._acceleration = [0.0, 0.0]
        self.low_limit = 0.1

    @property
    def position_x(self):
        return self._position[0]

    @property
    def position_y(self):
        return self._position[1]

    @property
    def velocity_x(self):
        return self._velocity[0]

    @property
    def velocity_y(self):
        return self._velocity[1]

    @property
    def acceleration_x(self):
        return self._acceleration[0]

    @property
    def acceleration_y(self):
        return self._acceleration[1]

    @property
    def stopped(self):
        return (self.velocity_x == 0 and self.velocity_y == 0 and self.acceleration_x == 0 and self.acceleration_y == 0)

    @position_x.setter
    def position_x(self, new_position_x):
        self._position[0] = new_position_x

    @position_y.setter
    def position_y(self, new_position_y):
        self._position[1] = new_position_y

    @velocity_x.setter
    def velocity_x(self, new_velocity):
        if (abs(new_velocity) < self.low_limit):
            new_velocity = 0
        self._velocity[0] = new_velocity

    @velocity_y.setter
    def velocity_y(self, new_velocity):
        if (abs(new_velocity) < self.low_limit):
            new_velocity = 0
        self._velocity[1] = new_velocity

    @acceleration_x.setter
    def acceleration_x(self, new_acceleration):
        if (abs(new_acceleration) < self.low_limit):
            new_acceleration = 0
        self._acceleration[0] = new_acceleration

    @acceleration_y.setter
    def acceleration_y(self, new_acceleration):
        if (abs(new_acceleration) < self.low_limit):
            new_acceleration = 0
        self._acceleration[1] = new_acceleration


class Physics_Limit:
    def __init__(self, rect, limit_type, action, event=None):
        self.rect = rect.copy()
        self.limit_type = limit_type  # One of Limit Types
        self.action = action  # One of Actions at Limits
        self.event = event
        self.motion = None


class Physics:
    gravity = 9.81
    perfect_bounce = 1

    def __init__(self):
        self._init_motion = Physics_Motion()
        self._curr_motion = Physics_Motion()
        self._timers = [Timer(0, None, False), Timer(0, None, False)]
        self._moving = False
        self.rect_width = 0
        self.rect_height = 0
        self._multiplier = 50
        self._bounce_timer = Timer(0)
        self.bounce_cor = 0.8  # Coefficient of Restitution
        # Minimum time between dynamic bounces (secs)
        self.bounce_time_limit = 0.5
        self.negate_acc = 0.9
        self._limits = []

    @property
    def debug_str(self):
        return "Pos=({0:3.0f},{1:3.0f}), Vel=({2:5.1f},{3:5.1f}), Acc=({4:5.1f},{5:5.1f}), InitPos=({6:5.1f},{7:5.1f}), InitVel=({8:5.1f},{9:5.1f})".format(
            self.left, self.top, self.curr_vel_x, self.curr_vel_y, self.curr_acc_x, self.curr_acc_y,
            self.init_pos_x, self.init_pos_y, self.init_vel_x, self.init_vel_y)

    @property
    def init_pos_x(self):
        return self._init_motion.position_x

    @property
    def init_pos_y(self):
        return self._init_motion.position_y

    @property
    def init_vel_x(self):
        return self._init_motion.velocity_x

    @property
    def init_vel_y(self):
        return self._init_motion.velocity_y

    @property
    def curr_acc_x(self):
        return self._curr_motion.acceleration_x

    @property
    def curr_acc_y(self):
        return self._curr_motion.acceleration_y

    @property
    def curr_pos_x(self):
        return self._curr_motion.position_x

    @property
    def curr_pos_y(self):
        return self._curr_motion.position_y

    @property
    def curr_vel_x(self):
        return self._curr_motion.velocity_x

    @property
    def curr_vel_y(self):
        return self._curr_motion.velocity_y

    @property
    def speed(self):
        return math.hypot(self.curr_vel_x, self.curr_vel_y)

    @property
    def angle(self):
        if self.curr_vel_x == 0:
            return 0
        else:
            return math.degrees(math.atan(self.curr_vel_y / self.curr_vel_x))

    @property
    def angle_radians(self):
        if self.curr_vel_x == 0:
            return 0
        else:
            return math.atan(self.curr_vel_y / self.curr_vel_x)

    @property
    def stopped(self):
        return self._curr_motion.stopped

    @curr_pos_x.setter
    def curr_pos_x(self, new_pos_x):
        self._curr_motion.position_x = new_pos_x

    @curr_pos_y.setter
    def curr_pos_y(self, new_pos_y):
        self._curr_motion.position_y = new_pos_y

    @curr_vel_x.setter
    def curr_vel_x(self, new_vel_x):
        self._curr_motion.velocity_x = new_vel_x

    @curr_vel_y.setter
    def curr_vel_y(self, new_vel_y):
        self._curr_motion.velocity_y = new_vel_y

    @curr_acc_x.setter
    def curr_acc_x(self, new_acc_x):
        self._curr_motion.acceleration_x = new_acc_x

    @curr_acc_y.setter
    def curr_acc_y(self, new_acc_y):
        self._curr_motion.acceleration_y = new_acc_y

    @speed.setter
    def speed(self, new_speed):
        self.set_speed_angle(new_speed, self.angle)

    @angle.setter
    def angle(self, new_angle):
        self.set_speed_angle(self.speed, new_angle)

    @property
    def multiplier(self):
        return self._multiplier

    @multiplier.setter
    def multiplier(self, multiplier):
        self._multiplier = multiplier

    def set_velocity(self, vel_x=None, vel_y=None):
        if vel_x is not None:
            self._curr_motion.velocity_x = vel_x
            self._init_pvt_x()
        if vel_y is not None:
            self._curr_motion.velocity_y = vel_y
            self._init_pvt_y()

    def set_speed_angle(self, speed, angle):
        self.set_velocity(speed * math.cos(math.radians(angle)),
                          speed * math.sin(math.radians(angle)))

    def set_acceleration(self, xacceleration, yacceleration):
        self._curr_motion.acceleration_x = xacceleration
        self._curr_motion.acceleration_y = yacceleration

    def set_initial_position(self, xpos=None, ypos=None):
        if xpos is None:
            xpos = self.curr_pos_x
        if ypos is None:
            ypos = self.curr_pos_y
        self._init_motion.position_x = xpos
        self._init_motion.position_y = ypos

    def set_initial_velocity(self, xvel=None, yvel=None):
        if xvel is None:
            xvel = self.curr_vel_x
        if yvel is None:
            yvel = self.curr_vel_y
        self._init_motion.velocity_x = xvel
        self._init_motion.velocity_y = yvel

    def set_initial_acceleration(self, xacc=None, yacc=None):
        if xacc is None:
            xacc = self.curr_acc_x
        if yacc is None:
            yacc = self.curr_acc_y
        self._init_motion.acceleration_x = xacc
        self._init_motion.acceleration_y = yacc

    def stop_here_x(self):
        self._init_motion.position_x = self.curr_pos_x
        self._init_motion.velocity_x = 0
        self.curr_acc_x = 0

    def stop_here_y(self):
        self._init_motion.position_y = self.curr_pos_y
        self._init_motion.velocity_y = 0
        self.curr_acc_y = 0

    def _init_pvt_x(self, xpos=None, xvel=None):
        if xpos is None:
            xpos = self.curr_pos_x
        if xvel is None:
            xvel = self.curr_vel_x
        self._init_motion.position_x = xpos
        self._init_motion.velocity_x = xvel
        self._start_x_timer()

    def _init_pvt_y(self, ypos=None, yvel=None):
        if ypos is None:
            ypos = self.curr_pos_y
        if yvel is None:
            yvel = self.curr_vel_y
        self._init_motion.position_y = ypos
        self._init_motion.velocity_y = yvel
        self._start_y_timer()

    def _start_x_timer(self):
        self._timers[0].start()

    def _start_y_timer(self):
        self._timers[1].start()

    @property
    def x_timer_elapsed(self):
        return self._timers[0].time

    @property
    def y_timer_elapsed(self):
        return self._timers[1].time

    def add_limit(self, limit):
        self._limits.append(limit)

    def clear_limits(self):
        self._limits.clear()

    def _calculate_curr_motion(self, dx, dy, use_physics):
        if use_physics:
            self.set_initial_position(
                self.init_pos_x + dx, self.init_pos_y + dy)
            if (dx > 0 or dy > 0):
                self.apply_limits(self, use_curr_motion=False)

            tx = self.x_timer_elapsed
            self._curr_motion.position_x = self.init_pos_x + \
                int((self.init_vel_x * tx + 0.5 *
                     self.curr_acc_x * tx * tx) * self._multiplier)
            self._curr_motion.velocity_x = self.init_vel_x + self.curr_acc_x * tx
            self._curr_motion.acceleration_x = self.curr_acc_x

            ty = self.y_timer_elapsed
            self._curr_motion.position_y = self.init_pos_y + \
                int((self.init_vel_y * ty + 0.5 *
                     self.curr_acc_y * ty * ty) * self._multiplier)
            self._curr_motion.velocity_y = self.init_vel_y + self.curr_acc_y * ty
            self._curr_motion.acceleration_y = self.curr_acc_y
        else:
            self.set_initial_position(self.left + dx, self.top + dy)
            if (dx > 0 or dy > 0):
                self.apply_limits(self, use_curr_motion=False)
            self.curr_pos_x = self.init_pos_x
            self.curr_pos_y = self.init_pos_y

    def _test_limit(self, limit, use_curr_motion=True):
        if use_curr_motion:
            motion = self._curr_motion
        else:
            motion = self._init_motion

        at_limit_x = at_limit_y = 0

        # Calculate distance to limit
        left_to_limit_left = motion.position_x - limit.rect.left
        right_to_limit_left = (motion.position_x +
                               self.rect_width) - limit.rect.left
        left_to_limit_right = motion.position_x - limit.rect.right
        right_to_limit_right = (
            motion.position_x + self.rect_width) - limit.rect.right

        top_to_limit_top = motion.position_y - limit.rect.top
        bottom_to_limit_top = (motion.position_y +
                               self.rect_height) - limit.rect.top
        top_to_limit_bottom = motion.position_y - limit.rect.bottom
        bottom_to_limit_bottom = (
            motion.position_y + self.rect_height) - limit.rect.bottom

        centerx_to_limit_centerx = motion.position_x + \
            self.rect_width//2 - limit.rect.centerx
        centery_to_limit_centery = motion.position_y + \
            self.rect_height//2 - limit.rect.centery

        # Determine if at limit
        if limit.limit_type == LIMIT_KEEP_INSIDE:
            if left_to_limit_left <= 0:
                at_limit_x |= AT_LIMIT_LEFT
            if right_to_limit_right >= 0:
                at_limit_x |= AT_LIMIT_RIGHT
            if top_to_limit_top <= 0:
                at_limit_y |= AT_LIMIT_TOP
            if bottom_to_limit_bottom >= 0:
                at_limit_y |= AT_LIMIT_BOTTOM

        elif limit.limit_type == LIMIT_KEEP_OUTSIDE:
            if (right_to_limit_left >= 0) and (left_to_limit_left < 0) and (motion.position_y+self.rect_height >= limit.rect.top) and (motion.position_y <= limit.rect.bottom):
                at_limit_x |= AT_LIMIT_LEFT

            if (left_to_limit_right <= 0) and (right_to_limit_right > 0) and (motion.position_y+self.rect_height >= limit.rect.top) and (motion.position_y <= limit.rect.bottom):
                at_limit_x |= AT_LIMIT_RIGHT

            if (bottom_to_limit_top >= 0) and (top_to_limit_top < 0) and (motion.position_x+self.rect_width >= limit.rect.left) and (motion.position_x <= limit.rect.right):
                at_limit_y |= AT_LIMIT_TOP

            if (top_to_limit_bottom <= 0) and (bottom_to_limit_bottom > 0) and (motion.position_x+self.rect_width >= limit.rect.left) and (motion.position_x <= limit.rect.right):
                at_limit_y |= AT_LIMIT_BOTTOM

        elif limit.limit_type == LIMIT_OVERLAP:
            if abs(left_to_limit_left) <= abs(motion.velocity_x):
                at_limit_x |= AT_LIMIT_LEFT
            if abs(top_to_limit_top) <= abs(motion.velocity_y):
                at_limit_y |= AT_LIMIT_TOP

        elif limit.limit_type == LIMIT_MOVE_TO:
            if left_to_limit_right > 0:
                at_limit_x |= AT_LIMIT_RIGHT
            elif right_to_limit_left < 0:
                at_limit_x |= AT_LIMIT_LEFT
            elif abs(centerx_to_limit_centerx) < limit.rect.width:
                at_limit_x |= AT_LIMIT_INSIDE_X
            if top_to_limit_bottom > 0:
                at_limit_y |= AT_LIMIT_BOTTOM
            elif bottom_to_limit_top < 0:
                at_limit_y |= AT_LIMIT_TOP
            elif abs(centery_to_limit_centery) < limit.rect.height:
                at_limit_y |= AT_LIMIT_INSIDE_Y

        return (at_limit_x, at_limit_y)

    def _post_event_at_limit(self, limit, at_limit_x, at_limit_y, use_curr_motion=True):
        if (at_limit_x > 0 or at_limit_y > 0) and limit.event is not None and use_curr_motion:
            limit.event.at_limit_x = at_limit_x
            limit.event.at_limit_y = at_limit_y
            EventManager.post(limit.event)

    def _eval_action(self, action):
        if (action & AT_LIMIT_X_CLEAR_VEL_X) > 0 or (action & AT_LIMIT_X_BOUNCE_X) > 0:
            action |= AT_LIMIT_X_HOLD_POS_X

        if (action & AT_LIMIT_Y_CLEAR_VEL_Y) > 0 or (action & AT_LIMIT_Y_BOUNCE_Y) > 0:
            action |= AT_LIMIT_Y_HOLD_POS_Y

        if (action & AT_LIMIT_XY_CLEAR_VEL_XY) > 0:
            action |= AT_LIMIT_X_HOLD_POS_X
            action |= AT_LIMIT_Y_HOLD_POS_Y

        return action

    def _execute_action(self, limit, action, at_limit_x, at_limit_y, use_curr_motion=True):
        if use_curr_motion:
            motion = self._curr_motion
        else:
            # AT_LIMIT_X_HOLD_POS_X and AT_LIMIT_Y_HOLD_POS_Y only
            motion = self._init_motion

        # AT_LIMIT_X_HOLD_POS_X
        if (action & AT_LIMIT_X_HOLD_POS_X) > 0 and at_limit_x > 0:
            if limit.limit_type == LIMIT_KEEP_INSIDE:
                if (at_limit_x & AT_LIMIT_LEFT > 0):
                    motion.position_x = limit.rect.left
                if (at_limit_x & AT_LIMIT_RIGHT > 0):
                    motion.position_x = limit.rect.right - self.rect_width

            if limit.limit_type == LIMIT_KEEP_OUTSIDE:
                if (at_limit_x & AT_LIMIT_LEFT > 0):
                    motion.position_x = limit.rect.left - self.rect_width
                if (at_limit_x & AT_LIMIT_RIGHT > 0):
                    motion.position_x = limit.rect.right

            if limit.limit_type == LIMIT_OVERLAP:
                if (at_limit_x & AT_LIMIT_LEFT > 0) or (at_limit_x & AT_LIMIT_RIGHT > 0):
                    motion.position_x = limit.rect.left

        # AT_LIMIT_Y_HOLD_POS_Y
        if (action & AT_LIMIT_Y_HOLD_POS_Y) > 0 and at_limit_y > 0:
            if limit.limit_type == LIMIT_KEEP_INSIDE:
                if (at_limit_y & AT_LIMIT_TOP > 0):
                    motion.position_y = limit.rect.top
                if (at_limit_y & AT_LIMIT_BOTTOM > 0):
                    motion.position_y = limit.rect.bottom - self.rect_height

            if limit.limit_type == LIMIT_KEEP_OUTSIDE:
                if (at_limit_y & AT_LIMIT_TOP > 0):
                    motion.position_y = limit.rect.top - self.rect_height
                if (at_limit_y & AT_LIMIT_BOTTOM > 0):
                    motion.position_y = limit.rect.bottom

            if limit.limit_type == LIMIT_OVERLAP:
                if (at_limit_y & AT_LIMIT_TOP > 0) or (at_limit_y & AT_LIMIT_BOTTOM > 0):
                    motion.position_y = limit.rect.top

        # AT_LIMIT_X_CLEAR_VEL_X
        if (action & AT_LIMIT_X_CLEAR_VEL_X) > 0 and at_limit_x > 0:
            self.stop_here_x()

        # AT_LIMIT_Y_CLEAR_VEL_Y
        if (action & AT_LIMIT_Y_CLEAR_VEL_Y) > 0 and at_limit_y > 0:
            self.stop_here_y()

        # AT_LIMIT_XY_CLEAR_VEL_XY
        if (action & AT_LIMIT_XY_CLEAR_VEL_XY) > 0 and (at_limit_x > 0 or at_limit_y > 0):
            self.stop_here_x()
            self.stop_here_y()

        # AT_LIMIT_X_BOUNCE_X
        if (action & AT_LIMIT_X_BOUNCE_X) > 0 and at_limit_x > 0:
            self._init_pvt_x(
                self.curr_pos_x, self.curr_vel_x * -self.bounce_cor)

        # AT_LIMIT_Y_BOUNCE_Y
        if (action & AT_LIMIT_Y_BOUNCE_Y) > 0 and at_limit_y > 0:
            self._init_pvt_y(
                self.curr_pos_y, self.curr_vel_y * -self.bounce_cor)

        # AT_LIMIT_X_MOVE_TO_X
        if (action & AT_LIMIT_X_MOVE_TO_X) > 0:
            if (at_limit_x & AT_LIMIT_INSIDE_X) > 0:
                if abs(self.curr_vel_x) > 0:
                    self.curr_pos_x = limit.rect.centerx - self.rect_width//2
                    self.stop_here_x()
            if (at_limit_x & AT_LIMIT_LEFT) > 0:
                if self.curr_vel_x == 0:
                    self.curr_vel_x = abs(limit.motion.velocity_x)
                    self._init_pvt_x()
            if (at_limit_x & AT_LIMIT_RIGHT) > 0:
                if self.curr_vel_x == 0:
                    self.curr_vel_x = -abs(limit.motion.velocity_x)
                    self._init_pvt_x()

        # AT_LIMIT_Y_MOVE_TO_Y
        if (action & AT_LIMIT_Y_MOVE_TO_Y) > 0:
            if (at_limit_y & AT_LIMIT_INSIDE_Y) > 0:
                if abs(self.curr_vel_y) > 0:
                    self.curr_pos_y = limit.rect.centery - self.rect_height//2
                    self.stop_here_y()
            if (at_limit_y & AT_LIMIT_LEFT) > 0:
                if self.curr_vel_y == 0:
                    self.curr_vel_y = abs(limit.motion.velocity_y)
                    self._init_pvt_y()
            if (at_limit_y & AT_LIMIT_RIGHT) > 0:
                if self.curr_vel_y == 0:
                    self.curr_vel_y = -abs(limit.motion.velocity_y)
                    self._init_pvt_y()

        # AT_LIMIT_X_DO_NOTHING
        if (action & AT_LIMIT_X_DO_NOTHING) > 0:
            pass

        # AT_LIMIT_Y_DO_NOTHING
        if (action & AT_LIMIT_Y_DO_NOTHING) > 0:
            pass

        # AT_LIMIT_STOP
        if (action & AT_LIMIT_STOP) > 0 and (at_limit_x > 0 or at_limit_y > 0):
            self.stop_here_x()
            self.stop_here_y()

    def _apply_limit(self, limit, use_curr_motion=True):
        at_limit_x, at_limit_y = self._test_limit(limit, use_curr_motion)
        if (at_limit_x > 0 or at_limit_y > 0):
            self._post_event_at_limit(
                limit, at_limit_x, at_limit_y, use_curr_motion)
            action = self._eval_action(limit.action)
            self._execute_action(limit, action, at_limit_x,
                                 at_limit_y, use_curr_motion)

    def apply_limits(self, use_physics=False, use_curr_motion=True):
        if not use_physics:
            self.rect_width = self.width
            self.rect_height = self.height
        for limit in self._limits:
            self._apply_limit(limit, use_curr_motion)

    def dynamic_limit(self, limit):
        ret_val = True
        if limit.limit_type == LIMIT_KEEP_INSIDE or limit.limit_type == LIMIT_KEEP_OUTSIDE or limit.limit_type == LIMIT_OVERLAP:
            # To Do: Test
            at_limit_x, at_limit_y = self._test_limit(limit)
            if (at_limit_x > 0 or at_limit_y > 0):
                self._post_event_at_limit(limit, at_limit_x, at_limit_y)
                action = self._eval_action(limit.action)
                self._execute_action(limit, action, at_limit_x, at_limit_y)
            else:
                ret_val = False

        if limit.limit_type == LIMIT_COLLISION and limit.action == AT_LIMIT_BOUNCE and self._bounce_timer.time_left == 0:
            if limit.rect.centery != self.centery:  # Avoid divde by 0
                tangent_slope = (self.centerx - limit.rect.centerx) / \
                    (limit.rect.centery - self.centery)
                tangent_angle = math.degrees(math.atan(tangent_slope))
                self.angle = 2 * tangent_angle - self.angle
                self.go()
                self.move_physics()
                self._bounce_timer = Timer(self.bounce_time_limit)
                self._post_event_at_limit(limit, 1, AT_LIMIT_TOP)

        return ret_val

# --------------------------------------------------


class cckkRect(pygame.Rect):
    def overlap_xy(self, x: int, y:int) -> bool:
        return (x >= self.left and x <= self.right and y >= self.top and y <= self.bottom)

    def overlap_pos(self, pos: tuple[int, int]) -> bool:
        return self.overlap_xy(pos[0], pos[1])

    def size_delta(self, delta_width: int|float = 0, delta_height: int|float = 0) -> "cckkRect":
        return cckkRect(int(self.x - delta_width/2), int(self.y - delta_height/2), self.width + delta_width, self.height + delta_height)

    def size_factor(self, factor_width: int|float = 0, factor_height: int|float = 0) -> "cckkRect":
        return self.size_delta(self.width * factor_width, self.height * factor_height)


class MovingRect(cckkRect, Physics):
    def __init__(self):
        Physics.__init__(self)
        self.topleft = (0, 0)
        self.size = (0, 0)
        self._use_physics = False

    @property
    def use_physics(self):
        return self._use_physics

    @use_physics.setter
    def use_physics(self, new_use_physics):
        self._use_physics = new_use_physics

    def go(self):
        self.set_initial_position(self.left, self.top)
        self.set_initial_velocity()
        self.rect_width = self.width
        self.rect_height = self.height
        self._start_x_timer()
        self._start_y_timer()
        self._moving = not self.stopped
        self.use_physics = True

    def move_physics(self, dx=0, dy=0):
        # logger.debug("BEFORE: "+self.debug_str)
        self._calculate_curr_motion(dx, dy, self.use_physics)
        self.apply_limits(self.use_physics)
        self.left = self.curr_pos_x
        self.top = self.curr_pos_y
        # logger.debug("AFTER : "+self.debug_str)

    def move_to(self, pos_x=None, pos_y=None):
        if self.use_physics:
            self._init_pvt_x(xpos=pos_x)
            self._init_pvt_y(ypos=pos_y)
        else:
            if pos_x is not None:
                self.centerx = pos_x
            if pos_y is not None:
                self.centery = pos_y
        self._calculate_curr_motion(0, 0, self.use_physics)
        self.apply_limits(self.use_physics)
        self.left = self.curr_pos_x
        self.top = self.curr_pos_y

    def move_action(self, action=None, mx=1, my=1):
        dx = dy = 0
        if action == "MoveLeft": dx = -1
        elif action == "MoveRight": dx = 1
        elif action == "MoveUp": dy = -1
        elif action == "MoveDown": dy = 1
        dx = dx * mx
        dy = dy * my
        self.move_physics(dx, dy)


# --------------------------------------------------


class Timer():
    def __init__(self, timer_secs=0, timer_event=None, auto_start=True):
        self._timer_value = timer_secs * 1000.0
        self._start_time = pygame.time.get_ticks()
        self._stop_time = pygame.time.get_ticks()
        self._timer_event = timer_event
        self._running = auto_start
        if (auto_start):
            self.start()

    def start(self):
        self._start_time = pygame.time.get_ticks()
        self._running = True
        if self._timer_event != None:
            pygame.time.set_timer(self._timer_event, int(self._timer_value))

    def stop(self):
        self._stop_time = pygame.time.get_ticks()
        self._running = False
        self.stop_event()
        return (self._stop_time - self._start_time)/1000.0

    def stop_event(self):
        if self._timer_event != None:
            pygame.time.set_timer(self._timer_event, 0)

    def clear(self):
        self._start_time = pygame.time.get_ticks()
        self._stop_time = pygame.time.get_ticks()
        self._running = False

    @property
    def time(self):
        if self._running:
            time_now = pygame.time.get_ticks()
            return (time_now - self._start_time)/1000.0
        else:
            return 0

    @property
    def time_msecs(self):
        return int(self.time * 1000.0)

    @property
    def time_left(self):
        if self._running:
            time_now = pygame.time.get_ticks()
            time_left = self._timer_value - (time_now - self._start_time)
            time_left = max(time_left, 0)
            return time_left/1000.0
        else:
            return self._timer_value/1000.0

    def time_up(self, restart_if_expired=True):
        expired = (self.time_left == 0)
        if expired and restart_if_expired:
            self.start()
        return expired

    def extend_timer(self, increase_secs):
        self._timer_value = self._timer_value + increase_secs * 1000.0
        self.stop_event()
        self.start()

# --------------------------------------------------


class LoopTimer():
    def __init__(self, max_loops, auto_start=True):
        self._queue = deque([0] * max_loops, max_loops)
        self._timer = Timer(auto_start=auto_start)
        self._loop_counter = 0

    def start(self):
        self._timer.start()

    def append(self, loop_time=None):
        if loop_time is None:
            loop_time = self._timer.time_msecs
        self._queue.append(loop_time)
        self._timer.start()
        self._loop_counter = self._loop_counter + 1

    @property
    def msecs_per_loop(self):
        return sum(self._queue) / len(self._queue)

    @property
    def loops_per_sec(self):
        msecs = self.msecs_per_loop
        if msecs == 0:
            return 0
        else:
            return 1000.0 / self.msecs_per_loop

    @property
    def loops(self):
        return self._loop_counter

# --------------------------------------------------


EVENT_READ_KEYBOARD = pygame.USEREVENT
EVENT_SCROLL_GAME = pygame.USEREVENT + 1
EVENT_GAME_CONTROL = pygame.USEREVENT + 2
EVENT_GAME_FLOW = pygame.USEREVENT + 3
EVENT_GAME_TIMER_1 = pygame.USEREVENT + 4
EVENT_GAME_TIMER_2 = pygame.USEREVENT + 5
EVENT_NEXT_USER_EVENT = pygame.USEREVENT + 6

# Game Control Actions
#   e.action: StartGame, GameOver, ClearGameOver, QuitGame, Board, Pass, Hint, ClearHint, Print, Keyboard,
#             UpdateScore, KillSpriteUUID, MouseMotion, MouseLeftClick, MouseRightClick, MouseUnclick
#   e.info: Dictionary with additional event information, including:
#             pos   - Mouse position for MouseMotion, MouseLeftClick, MouseRightClick and MouseUnclick
#             value - Delta value for UpdateScore
#             key   - Name of key pressed

class EventManager:
    @staticmethod
    def info_to_str(e):
        strlist = []
        for k, v in e.info.items():
            strlist.append(str(k) + "=" + str(v))
        return ", ".join(strlist)

    @staticmethod
    def get():
        ev_list = pygame.event.get()
        return ev_list

    @staticmethod
    def post(e):
        if (e.type >= pygame.NUMEVENTS):
            logger.error("Max value for event type is {0}".format(e.type))

        if e.action != "MouseMotion":
            logger.debug("Post event: Type={0}, Action={1}, Info={2}".format(
                e.type, e.action, EventManager.info_to_str(e)))

        pygame.event.post(e)

    @staticmethod
    def create_event(event_type, action="", **info_items):
        if type(event_type).__name__ == "tuple":
            t, a = event_type
            return EventManager.create_event(t, a, info_items)
        else:
            info = {}
            for key, value in info_items.items():
                info[key] = value
            ev_dict = {"action": action, "info": info}
            e = pygame.event.Event(event_type, ev_dict)
            return e

    @staticmethod
    def gc_event(action, **info_items):
        return EventManager.create_event(EVENT_GAME_CONTROL, action, **info_items)

    @staticmethod
    def post_game_control(action, **info_items):
        # if (action == "StartGame" or action == "GameOver" or action == "Quit") and not("broadcast" in info_items):
        #     ev = EventManager.create_event(EVENT_GAME_CONTROL, action, broadcast=True, **info_items)
        #     logger.debug("Post (broadcast): " + action)
        # else:
        ev = EventManager.create_event(
            EVENT_GAME_CONTROL, action, **info_items)
        EventManager.post(ev)

    @staticmethod
    def is_broadcast(e):
        ret = False
        if "info" in e.dict:
            if "broadcast" in e.info:
                if e.info['broadcast']:
                    ret = True
        return ret

    @staticmethod
    def set_key_repeat(delay, interval):
        pygame.key.set_repeat(delay, interval)

    @staticmethod
    def disable_key_repeat():
        pygame.key.set_repeat()

    def __init__(self):
        self._keyboard = {}
        self._user_event = {}

    def keyboard_event(self, event_type, action):
        self._keyboard[event_type] = action

    def user_event(self, event_type, action):
        self._user_event[event_type] = action

    def event_map(self, key_event_map=None, user_event_map=None):
        if key_event_map is not None:
            for event_type, action in key_event_map.items():
                self.keyboard_event(event_type, action)
        if user_event_map is not None:
            for event_type, action in user_event_map.items():
                self.user_event(event_type, action)

    def event(self, e, ignore_keys=False):
        dealt_with = False
        action = None
        if e.type == pygame.MOUSEMOTION:
            action = "MouseMotion"
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:
                action = "MouseLeftClick"
            elif e.button == 3:
                action = "MouseRightClick"
        elif e.type == pygame.MOUSEBUTTONUP:
            action = "MouseUnclick"
        elif e.type == pygame.JOYAXISMOTION:
            action = "JoystickMotion"
        elif e.type == pygame.JOYBUTTONDOWN:
            action = "JoystickButtonDown"
        elif e.type == pygame.JOYBUTTONUP:
            action = "JoystickButtonUp"

        if action is not None and (e.type in [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION]):
            ev = EventManager.create_event(
                EVENT_GAME_CONTROL, action, pos=e.pos)
            EventManager.post(ev)
            dealt_with = True
        if action is not None and (e.type  == pygame.JOYAXISMOTION):
            axis = ""
            if   e.dict["axis"] == 0: axis = "X"
            elif e.dict["axis"] == 1: axis = "Y"
            elif e.dict["axis"] == 2: axis = "Z"
            ev = EventManager.create_event(
                EVENT_GAME_CONTROL, action, joy=e.dict["joy"], axis_num=e.dict["axis"], axis=axis, value=e.dict["value"])
            EventManager.post(ev)
            dealt_with = True
        if action is not None and (e.type in [pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]):
            ev = EventManager.create_event(
                EVENT_GAME_CONTROL, action, joy=e.dict["joy"], button=e.dict["button"])
            EventManager.post(ev)
            dealt_with = True

        if e.type == pygame.KEYDOWN and not dealt_with and not ignore_keys:
            for kb_k, kb_a in self._keyboard.items():
                if e.key == kb_k:
                    EventManager.post_game_control(kb_a)
                    dealt_with = True

        if e.type == EVENT_READ_KEYBOARD and ignore_keys:
            keys = pygame.key.get_pressed()
            for kb_k, kb_a in self._keyboard.items():
                if keys[kb_k]:
                    EventManager.post_game_control(kb_a)
            dealt_with = True

        if not dealt_with:
            for tim_t, tim_a in self._user_event.items():
                if e.type == tim_t:
                    EventManager.post_game_control(tim_a)
                    dealt_with = True

        return dealt_with

    def post_key_name(self, e):
        if e.type == pygame.KEYDOWN:
            try:
                key_name = "K_" + pygame.key.name(e.key)
                EventManager.post_game_control("Keyboard", key=key_name)
                return key_name
            except:
                return None

# --------------------------------------------------


class RandomQueue:
    def __init__(self, queue_len, min_val, max_val, max_change=20, max_change_rate=3, init_value=0):
        self._queue = deque([init_value] * queue_len, queue_len)
        self._min = min_val
        self._max = max_val
        self._max_change = max_change
        self._max_change_rate = max_change_rate
        self._next_value = 0
        self._next_change = 0

    @property
    def queue(self):
        return self._queue

    @property
    def next_value(self):
        return self._next_value

    @next_value.setter
    def next_value(self, new_value):
        self._next_value = new_value

    def append(self, dyn_max=-1):
        if dyn_max < 0:
            dyn_max = self._max

        self._queue.append(self._next_value)
        self._next_change = self._next_change + \
            random.randint(-self._max_change_rate, self._max_change_rate) * \
            random.randint(-self._max_change_rate, self._max_change_rate)
        self._next_change = max(self._next_change, -self._max_change)
        self._next_change = min(self._next_change, self._max_change)

        self._next_value = self._next_value + self._next_change
        if self._next_value < self._min:
            self._next_value = self._min
            self._next_change = max(self._next_change, 0)
        if self._next_value > min(self._max, dyn_max):
            self._next_value = min(self._max, dyn_max)
            self._next_change = min(self._next_change, 0)

# --------------------------------------------------


# Animation modes
ANIMATE_MANUAL = 1
ANIMATE_LOOP = 2
ANIMATE_SHUTTLE = 3
ANIMATE_ONCE = 4
ANIMATE_SHUTTLE_ONCE = 5
ANIMATE_REVERSE = 8  # Add to other modes


class Animation_Counter:
    def __init__(self):
        self.msecs_per_image = None
        self.setup(0, ANIMATE_LOOP, 10)

    def setup(self, total, mode, loops_per_image=10):
        self.total = total      # Total images
        self.loop = 0           # Loop counter
        if (mode & ANIMATE_REVERSE) == 0:
            self.mode = mode
            self.forward = True
            self.index = 0      # Image index
            self.step = 1
        if (mode & ANIMATE_REVERSE) > 0:
            self.mode = mode - ANIMATE_REVERSE
            self.forward = False
            self.index = total - 1
            self.step = -1
        if self.mode == ANIMATE_MANUAL:
            self.step = 0
            self.index = 0
        if loops_per_image is None:
            loops_per_image = 10
        self.loops_per_image = loops_per_image

    def next_loop(self):
        show_next_image = False
        self.loop += 1
        if (self.loop >= self.loops_per_image):
            self.loop = 0
            show_next_image = True
            self.next_image()
        return show_next_image

    @property
    def current_image(self):
        return self.index

    @current_image.setter
    def current_image(self, new_image):
        self.index = new_image

    def next_image(self):
        if self.mode == ANIMATE_MANUAL:
            if self.forward:
                self.index = min(self.index + 1, self.total - 1)
            else:
                self.index = max(self.index - 1, 0)
        else:
            self.index = self.index + self.step
        if self.index >= self.total:
            if self.mode == ANIMATE_LOOP:
                self.index = 0
            elif self.mode == ANIMATE_SHUTTLE:
                self.step = -1
                self.index = self.total - 2
            elif self.mode == ANIMATE_ONCE:
                self.index = self.total - 1
                self.step = 0
            elif self.mode == ANIMATE_SHUTTLE_ONCE:
                if self.forward:
                    self.step = -1
                    self.index = self.total - 2
                else:
                    self.index = self.total - 1
                    self.step = 0
        if self.index < 0:
            if self.mode == ANIMATE_LOOP:
                self.index = self.total - 1
            elif self.mode == ANIMATE_SHUTTLE:
                self.step = 1
                self.index = 1 if self.total > 1 else 0
            elif self.mode == ANIMATE_ONCE:
                self.index = 0
                self.step = 0
            elif self.mode == ANIMATE_SHUTTLE_ONCE:
                if self.forward:
                    self.index = 0
                    self.step = 0
                else:
                    self.step = 1
                    self.index = 1 if self.total > 1 else 0

    def prev_image(self):
        if self.mode == ANIMATE_MANUAL:
            if self.forward:
                self.index = max(self.index - 1, 0)
            else:
                self.index = min(self.index + 1, self.total - 1)

# --------------------------------------------------


class cckkImage:
    imagePath = None

    def __init__(self):
        super().__init__()
        self._surface = None
        self._surface_copy = None
        self._info_copy = None
        self._spritesheet = None
        self._ss_cols = 0
        self._ss_rows = 0
        self._ss_cell_width = 0
        self._ss_cell_height = 0
        self._ss_img_process = None

    @property
    def surface(self):
        return self._surface

    @surface.setter
    def surface(self, new_surface):
        self._surface = new_surface

    def image_path(self, filename):
        if self.imagePath is None:
            return filename
        else:
            return os.path.join(self.imagePath, filename)

    def create_copy(self, do_copy=True, info=None):
        if do_copy:
            self._surface_copy = self._surface.copy()
            self._info_copy = info

    def restore_copy(self, do_restore=True):
        if do_restore and self._surface_copy is not None:
            self._surface = self._surface_copy.copy()
        return self._info_copy

    def load(self, filename, img_process=None, crop=None, scale_to=None, set_copy=False):
        self.surface = image = pygame.image.load(
            self.image_path(filename)).convert_alpha()

        self.process_list(img_process, crop=crop, scale=scale_to)
        self.create_copy(set_copy)
        return self.surface

    def set_spritesheet(self, filename, cols, rows, img_process=None, crop=None, scale_to=None):
        self._spritesheet = pygame.image.load(
            self.image_path(filename)).convert_alpha()
        self._ss_cols = cols
        self._ss_rows = rows
        ss_width = self._spritesheet.get_rect().width
        ss_height = self._spritesheet.get_rect().height
        self._ss_cell_width = ss_width // cols
        self._ss_cell_height = ss_height // rows
        self._ss_img_process = (img_process, crop, scale_to)

    def spritesheet_image(self, sprite_number):
        x = self._ss_cell_width * (sprite_number % self._ss_cols)
        y = self._ss_cell_height * (sprite_number // self._ss_cols)
        rect = cckkRect(x, y, self._ss_cell_width, self._ss_cell_height)
        self.surface = self._spritesheet.subsurface(rect)
        self.process_list(self._ss_img_process[0], crop=self._ss_img_process[1], scale=self._ss_img_process[2])
        return self.surface

    def process(self, command, value):
        if command is None:
            return False
        
        if command == "crop" and value is not None:
            # Crop the image by ... value[left, right, top, bottom]
            crop_rect = self.surface.get_rect()
            crop_rect.width = crop_rect.width - value[0] - value[1]
            crop_rect.left = value[0]
            crop_rect.height = crop_rect.height - value[2] - value[3]
            crop_rect.top = value[2]
            curr_image = self.surface.copy()
            self.surface = pygame.Surface(crop_rect.size, pygame.SRCALPHA)
            self.surface.blit(curr_image, (0, 0), crop_rect)

        elif command == "scale" and value is not None:
            self.surface = pygame.transform.smoothscale(self.surface, value)

        elif command == "stretch" and value is not None:
            # Stretch the image by ... value[left, right, top, bottom]
            self.stretch_horiz(value[0], value[1])
            self.stretch_vert(value[2], value[3])

        elif command == "flip" and value is not None:
            flipx, flipy = value
            self.surface = pygame.transform.flip(self.surface, flipx, flipy)

        elif command == "rotate" and value is not None:
            if isinstance(value, tuple):
                do_crop = value[1] if len(value)>1 else True
                do_restore = value[2] if len(value)>2 else True
                value = value[0]
            else:
                do_crop = True
                do_restore = True

            self.restore_copy(do_restore)
            size = self.surface.get_rect().size
            self.surface = pygame.transform.rotate(self.surface, value)

            if do_crop:
                rot_size = self.surface.get_rect().size
                crop_x = int((rot_size[0] - size[0])/2)
                crop_y = int((rot_size[1] - size[1])/2)
                self.process("crop", [crop_x, crop_x, crop_y, crop_y])

            # Note:
            # Without do_crop, the size of the sprite surface will grow to
            # accommodate the rotated image. To maintain the same sprite size
            # and to rotate around the centre of the image:
            #   sprite.rect.size = size (return value from this function)
            #   sprite.rect.center = center (store sprite centre before rotating)

        return self.surface.get_rect().size

    def process_list(self, commands_values, **kwargs):
        cv_list = []
        for c, v in kwargs.items():
            cv_list.append((c,v))
        if commands_values is not None:
            if isinstance(commands_values, list):
                cv_list.extend(commands_values)
            else:
                cv_list.append(commands_values)

        for cv in cv_list:
            self.process(cv[0], cv[1])

    def stretch_horiz(self, stretch_left, stretch_right):
        stretch_rect = self.surface.get_rect()
        stretch_rect.width = stretch_rect.width + stretch_left + stretch_right
        curr_image = self.surface.copy()
        self.surface = pygame.Surface(stretch_rect.size, pygame.SRCALPHA)

        slice_rect = curr_image.get_rect()
        slice_rect.width = 1
        surf_lt = pygame.Surface(slice_rect.size, pygame.SRCALPHA)
        surf_lt.blit(curr_image, (0, 0), slice_rect)
        surf_lt = pygame.transform.smoothscale(surf_lt, (stretch_left, slice_rect.height))

        slice_rect.left = curr_image.get_rect().width - 1
        surf_rt = pygame.Surface(slice_rect.size, pygame.SRCALPHA)
        surf_rt.blit(curr_image, (0, 0), slice_rect)
        surf_rt = pygame.transform.smoothscale(surf_rt, (stretch_right, slice_rect.height))

        self.surface.blit(surf_lt, (0,0))
        self.surface.blit(curr_image, (stretch_left,0))
        self.surface.blit(surf_rt, (stretch_left+curr_image.get_rect().width,0))

    def stretch_vert(self, streth_up, streth_down):
        stretch_rect = self.surface.get_rect()
        stretch_rect.height = stretch_rect.height + streth_up + streth_down
        curr_image = self.surface.copy()
        self.surface = pygame.Surface(stretch_rect.size, pygame.SRCALPHA)

        slice_rect = curr_image.get_rect()
        slice_rect.height = 1
        surf_up = pygame.Surface(slice_rect.size, pygame.SRCALPHA)
        surf_up.blit(curr_image, (0, 0), slice_rect)
        surf_up = pygame.transform.smoothscale(surf_up, (slice_rect.width, streth_up))

        slice_rect.top = curr_image.get_rect().height - 1
        surf_dn = pygame.Surface(slice_rect.size, pygame.SRCALPHA)
        surf_dn.blit(curr_image, (0, 0), slice_rect)
        surf_dn = pygame.transform.smoothscale(surf_dn, (slice_rect.width, streth_down))

        self.surface.blit(surf_up, (0,0))
        self.surface.blit(curr_image, (0,streth_up))
        self.surface.blit(surf_dn, (0,streth_up+curr_image.get_rect().height))

# --------------------------------------------------


class StringLOL:
    # Multi-line string to list of lists of characters, with mirroring and mapping
    def __init__(self, ml_str, mirror_map=None):
        self._ml_str = ml_str
        self._lines = self._ml_str.splitlines()
        while "" in self._lines:
            self._lines.remove("")
        self._mirror_map = mirror_map
        self._lol = None
        self._mapped_lol = None

    def update_lol(self, x, y, new_ch):
        self._lol[y][x] = new_ch

    def transform(self, mirror_H, mirror_last_H, mirror_V, mirror_last_V, default_map=None):
        self._lol = []
        for l in self._lines:
            strList = list(l)
            if mirror_H:
                strList.extend(self.mirrorList(strList, mirror_last_H))
            self._lol.append(strList)
        if mirror_V:
            l = len(self._lol)
            if not mirror_last_V:
                l = l - 1
            for i in range(l-1, -1, -1):
                mapped_list = self.mapCharList(self._lol[i], 0, default_map)
                self._lol.append(mapped_list)
        return (self._lol)

    def mirrorList(self, strList, mirror_last_H):
        strList2 = strList.copy()
        if not mirror_last_H:
            strList2.pop()
        strList2.reverse()
        return self.mapCharList(strList2, 1)

    def mapCharList(self, the_list, map_index, default_map=None):
        mapped_list = []
        for ch in the_list:
            use_default = (self._mirror_map is None)
            if not use_default:
                if ch in self._mirror_map:
                    map_ch = self._mirror_map[ch][map_index]
                else:
                    use_default = True
            if use_default:
                if default_map is None:
                    map_ch = ch
                else:
                    map_ch = default_map
            mapped_list.append(map_ch)
        return mapped_list

    def map(self, string_map, default_map=None):
        self._mapped_lol = []
        for l in self._lol:
            map_l = []
            for ch in l:
                if ch in string_map:
                    map_ch = string_map[ch]
                else:
                    if default_map is None:
                        map_ch = ""
                    else:
                        map_ch = default_map
                map_l.append(map_ch)
            self._mapped_lol.append(map_l)
        return self._mapped_lol

    def map_as_list(self, string_map, default_map=None):
        return ([y for x in self.map(string_map, default_map) for y in x])

    def printLOL(self):
        for l in self._lol:
            print(''.join(l))


class GridMap(StringLOL):
    def __init__(self, grid_as_mlstr, mirror_map=None, mirror_H=False, mirror_last_H=False, mirror_V=False, mirror_last_V=False):
        super().__init__(grid_as_mlstr, mirror_map)
        self.transform(mirror_H, mirror_last_H, mirror_V, mirror_last_V)
        self._maps = {}

    def add_map(self, map_name, map_dict, default_map=None):
        self._maps[map_name] = self.map_as_list(map_dict, default_map)

    def grid_map(self, map_name):
        return self._maps[map_name]

    def grid_map_count(self, map_name, item=True):
        grid = self.grid_map(map_name)
        item_list = [x for x in grid if x == item]
        return len(item_list)

    @property
    def cols(self):
        return len(self._lol[0])

    @property
    def rows(self):
        return len(self._lol)

    @property
    def cols_rows(self):
        return (self.cols, self.rows)

    def cell_index(self, col, row):
        return (row * self.cols + col)

    def update_grid(self, grid_pos, grid_ch):
        self.update_lol(grid_pos[0], grid_pos[1], grid_ch)

    def find_nearest_item_R(self, grid, col, row, item=True):
        found = False
        xpos = col + 1
        while not found:
            found = (xpos >= self.cols)
            if not found:
                i = row * self.cols + xpos
                if i >= 0 and i < len(grid):
                    found = (grid[i] == item)
            if not found:
                xpos = xpos + 1

        return (xpos if found else -1)

    def find_nearest_item_L(self, grid, col, row, item=True):
        found = False
        xpos = col - 1
        while not found:
            found = (xpos < 0)
            if not found:
                i = row * self.cols + xpos
                if i >= 0 and i < len(grid):
                    found = (grid[i] == item)
            if not found:
                xpos = xpos - 1

        return (xpos if found else -1)

    def find_nearest_item_D(self, grid, col, row, item=True):
        found = False
        ypos = row + 1
        while not found:
            found = (ypos > self.rows)
            if not found:
                i = ypos * self.cols + col
                if i >= 0 and i < len(grid):
                    found = (grid[i] == item)
            if not found:
                ypos = ypos + 1

        return (ypos if found else -1)

    def find_nearest_item_U(self, grid, col, row, item=True):
        found = False
        ypos = row - 1
        while not found:
            found = (ypos < 0)
            if not found:
                i = ypos * self.cols + col
                if i >= 0 and i < len(grid):
                    found = (grid[i] == item)
            if not found:
                ypos = ypos - 1

        return (ypos if found else -1)

    def find_nearest_item(self, cell_pos, map_name, map_item=True):
        col = cell_pos[0]
        row = cell_pos[1]
        grid = self.grid_map(map_name)

        return {
            'R': self.find_nearest_item_R(grid, col, row, map_item),
            'L': self.find_nearest_item_L(grid, col, row, map_item),
            'D': self.find_nearest_item_D(grid, col, row, map_item),
            'U': self.find_nearest_item_U(grid, col, row, map_item)
        }

# --------------------------------------------------


class MoveOption:
    def __init__(self, move_dir, curr_dir, to_barrier=0, can_move=False):
        self.dir = move_dir
        self.can_move = can_move
        self._distance = {}
        self.set_distance("barrier", to_barrier)
        self.same_dir = (move_dir == curr_dir)
        self.is_turn = False
        if move_dir in ("U", "D") and curr_dir in ("L", "R"):
            self.is_turn = True
        if move_dir in ("L", "R") and curr_dir in ("U", "D"):
            self.is_turn = True
        self._score = None
        self.calc_score_fn = None

    @property
    def to_barrier(self):
        return self.distance("barrier", 0)

    def distance(self, target, not_found=None):
        if target in self._distance:
            return (self._distance[target])
        else:
            return (not_found)

    def set_distance(self, target, distance):
        self._distance[target] = distance
        return distance

    @property
    def score(self):
        if self.calc_score is None:
            return 0
        else:
            return self._score

    def calc_score(self, name):
        self._score = self.calc_score_fn(self, name)


def calc_move_option_score(mo, name):
    if mo.can_move:
        return 0
    else:
        return -1


class GridActor:
    def __init__(self, name, start_cell, speed, move_timer=None):
        self._name = name
        # cell_x, cell_y, cell_px, cell_py
        self._cell_pos = [None, None, None, None]
        self.set_cell(start_cell)
        self._curr_dir = self._next_dir = ""
        self._speed = speed
        self._timer = Timer(move_timer) if move_timer is not None else None
        self._barriers = None
        self._target_cell = None
        self._move_options = None
        self._choose_at_cell = None
        self._choose_at_time = Timer()
        self._chosen_dir = None
        self._history = {}
        self._history_last_call = (None, None)
        self.calc_score = calc_move_option_score

    @property
    def cell_pos(self):
        return self._cell_pos

    @property
    def cell(self):
        return ((self._cell_pos[0], self._cell_pos[1]))

    @property
    def cell_float(self):
        return ((self._cell_pos[0]+self._cell_pos[2]/100.0, self._cell_pos[1]+self._cell_pos[3]/100.0))

    def set_cell(self, next_col_row):
        col, row = next_col_row
        self._cell_pos = [col, row, 50, 50]

    @property
    def direction(self):
        return self._curr_dir

    @property
    def next_dir(self):
        return self._next_dir

    @direction.setter
    def direction(self, new_direction):
        if new_direction in ["U", "D", "L", "R"]:
            self._curr_dir = new_direction

    @next_dir.setter
    def next_dir(self, next_direction):
        if next_direction in ["U", "D", "L", "R"]:
            self._next_dir = next_direction

    def next_cell(self, dir):
        curr_cell = self.cell
        dx, dy = self._calc_dir(dir, False)
        return((curr_cell[0]+dx, curr_cell[1]+dy))

    def _calc_dir(self, dir, use_speed=True):
        # Convert dir string to dx, dy
        if dir == "R":
            dx, dy = 1, 0
        elif dir == "L":
            dx, dy = -1, 0
        elif dir == "D":
            dx, dy = 0, 1
        elif dir == "U":
            dx, dy = 0, -1
        else:
            dx, dy = 0, 0

        if use_speed:
            dx = dx * self._speed
            dy = dy * self._speed

        return (dx, dy)

    def set_grid_info(self, new_barriers=None, new_target_cell=None):
        self._barriers = new_barriers
        self._target_cell = new_target_cell

    def _can_move(self):
        if self._barriers is None:
            return True

        x, y, px, py = self.cell_pos

        dir_ok = {"R": True, "L": True, "D": True, "U": True}

        # Check if barrier is too close
        if px >= 50:
            dir_ok["R"] = ((x+1) < self._barriers["R"]
                           ) and (py > 35 and py < 65)
        if px <= 50:
            dir_ok["L"] = ((x-1) > self._barriers["L"]
                           ) and (py > 35 and py < 65)
        if py >= 50:
            dir_ok["D"] = ((y+1) < self._barriers["D"]
                           ) and (px > 35 and px < 65)
        if py <= 50:
            dir_ok["U"] = ((y-1) > self._barriers["U"]
                           ) and (px > 35 and px < 65)

        return dir_ok

    def _add_cell_history(self):
        if self._history_last_call == self.cell:
            pass
        else:
            self._history_last_call = self.cell
            if self.cell in self._history:
                self._history[self.cell] += 1
            else:
                self._history[self.cell] = 1

    def _cell_history(self, cell):
        ret = 0
        if cell in self._history:
            ret = self._history[cell]
        return ret

    def move_to(self, cell_pos=None, new_dir=None):
        if cell_pos is not None:
            self.set_cell(cell_pos)
            self._add_cell_history()

        if new_dir is not None:
            self.next_dir = new_dir

    def move_dir(self, change_dir=False):
        if change_dir:
            dir = self.next_dir
        else:
            dir = self.direction
        do_move = (dir != '')

        if do_move:
            dir_ok = self._can_move()

            if dir_ok[dir]:
                self.direction = dir
            else:
                do_move = False

        if do_move and self._timer is not None:
            do_move = self._timer.time_up()

        if do_move:
            x, y, px, py = self.cell_pos
            dx, dy = self._calc_dir(dir)

            if dx != 0:
                py = 50
            if dy != 0:
                px = 50

            x = x + (px + dx)/100.0
            y = y + (py + dy)/100.0

            self._cell_pos[0] = math.floor(x)
            self._cell_pos[1] = math.floor(y)
            self._cell_pos[2] = round((x - self._cell_pos[0]) * 100)
            self._cell_pos[3] = round((y - self._cell_pos[1]) * 100)

            self._add_cell_history()

        if change_dir and do_move:
            self._next_dir = ""

        return do_move

    def list_move_options(self):
        if self._barriers is None:
            return None

        x, y, px, py = self.cell_pos

        self._move_options = {
            "R": MoveOption("R", self.direction, self._barriers["R"] - x - 1),
            "L": MoveOption("L", self.direction, x - self._barriers["L"] - 1),
            "D": MoveOption("D", self.direction, self._barriers["D"] - y - 1),
            "U": MoveOption("U", self.direction, y - self._barriers["U"] - 1)}

        self._move_options["R"].set_distance(
            "target", self._target_cell[0] - x - 1)
        self._move_options["L"].set_distance(
            "target", x - self._target_cell[0] - 1)
        self._move_options["D"].set_distance(
            "target", self._target_cell[1] - y - 1)
        self._move_options["U"].set_distance(
            "target", y - self._target_cell[1] - 1)

        for mo_key, mo_value in self._move_options.items():
            self._move_options[mo_key].can_move = (mo_value.to_barrier > 0)

            if mo_key in ("R", "L") and (py <= 35 or py >= 65):
                self._move_options[mo_key].can_move = False
            if mo_key in ("D", "U") and (px <= 35 or px >= 65):
                self._move_options[mo_key].can_move = False

            next_cell = self.next_cell(mo_key)
            self._move_options[mo_key].next_cell_history = self._cell_history(
                next_cell)

            self._move_options[mo_key].calc_score_fn = self.calc_score
            self._move_options[mo_key].calc_score(self._name)

        return self._move_options.values()

    def pick_move_option(self):
        max_score = 0
        for mo in self._move_options.values():
            if mo.score > max_score:
                max_score = mo.score

        max_options = [x for x in self._move_options.values()
                       if x.score == max_score]
        chosen = random.sample(max_options, 1)
        next_dir = chosen[0].dir

        return self.choose(next_dir)

    def choose_move(self, delay=0):
        if self.cell == self._choose_at_cell:   # or self.since_last_choice < delay:
            return self._chosen_dir

        px = self.cell_pos[2]
        py = self.cell_pos[3]
        if (px <= 35 or px >= 65 or py <= 35 or py >= 65):
            return self._chosen_dir

        self.list_move_options()
        return self.pick_move_option()

    def choose(self, chosen_dir):
        px = self.cell_pos[2]
        py = self.cell_pos[3]
        if (px > 35 and px < 65 and py > 35 and py < 65):
            self._chosen_dir = chosen_dir
            self._choose_at_cell = self.cell
            self._choose_at_time.start()

        return chosen_dir

    @property
    def since_last_choice(self):
        return self._choose_at_time.time_msecs


# --------------------------------------------------

class GridMaze(GridMap):
    def move_options(self, col_row, direction=None, barrier_map="barrier", barrier_item=True):
        nearest = self.find_nearest_item(col_row, barrier_map, barrier_item)
        for opt_dir, opt_nearest in nearest.items():
            is_turn = (direction in ["U", "D"] and opt_dir in ["R", "L"]) or (
                direction in ["L", "R"] and opt_dir in ["U", "D"])
            # option = MoveOption()
        return nearest

# --------------------------------------------------

class cckkJoystick:
    def __init__(self, joystick_name=None, joystick_number=None):
        self._joystick = None
        self.limits = None
        self.obj_size = (0,0)
        self.steps = None

        if joystick_name is not None or joystick_number is not None:
            pygame.joystick.init()
            joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
            if joystick_name is not None:
                for j in joysticks:
                    if j.get_name() == joystick_name:
                        self._joystick = j
            elif joystick_number is not None:
                if joystick_number < pygame.joystick.get_count():
                    self._joystick = joysticks[joystick_number]

        if self._joystick is not None:
            self._joystick.init()

    def update_event(self, ev):
        if ev.action == "JoystickMotion" and self._joystick is not None and self.limits is not None:
            val = ev.info["value"]
            if self.steps is not None and self.steps != 0:
                val = ev.info["value"] = round(val * self.steps, 0) / self.steps
            pos = 0
            if ev.info["axis"] == "X":
                pos = self.limits.centerx + ((self.limits.width - self.obj_size[0])/2) * val
            if ev.info["axis"] == "Y":
                pos = self.limits.centery + ((self.limits.height - self.obj_size[1])/2) * val
            ev.info["pos"] = pos
        return ev

# --------------------------------------------------

