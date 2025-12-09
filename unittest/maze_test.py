import unittest
from cckk import cckkImage, cckkViewer, cckkAction, cckkCondition, cckkColourDict, cckkSenseHatGame, cckkSenseHatEmu


class test_maze(unittest.TestCase):

    def test_cckkAction_id(self):
        str_maze = """
################
#..............#
#.###########.##
#.######.......#
#.#########.####
#.######......##
#.#.##...#######
#.#....####...##
#.#.#..####.#.##
#.#.#.#####.#.##
..#.#.......#..#
##############.#
...............#
################
"""
        col_dict = cckkColourDict(update_dict={ "#": (0,0,128) })
        img_maze = cckkImage(imgStr = str_maze, name = "maze", colour_dict = col_dict)
        img_green = cckkImage(imgA = [(0,255,0)], name="maze_green", pos=(0,1))
        img_red = cckkImage(imgA = [(255,0,0)], name="maze_red", pos=(0,3))
        img_blue = cckkImage(imgA = [(0,255,0)], name="maze_blue", pos=(0,1))

        # Set up the Sense HAT
        cckk_hat = cckkSenseHatGame(images=[img_green,img_red,img_blue,img_maze])
        cckk_hat.sense = cckkSenseHatEmu()

        cond = cckkCondition(unless_overlap=["maze"], keep_within_assoc=True)
        cckk_hat.move_img("maze_green", -1, 0, condition=cond)
        cckk_hat.align_to_img(img_name = "maze_green", keep_img_name = "maze")
        cckk_hat.update_pixels()

        self.assertEqual(img_green.pos, (0,1))

        for i in range(14):
            cckk_hat.move_img("maze_green", 1, 0, condition=cond)
            self.assertEqual(img_green.pos, (i+1,1))

        cckk_hat.move_img("maze_green", 1, 0, condition=cond)
        self.assertEqual(img_green.pos, (14,1))  # Can't move any furhter right

        cckk_hat.move_img("maze_green", 0, 2, condition=cond)
        self.assertEqual(img_green.pos, (14,3))

        cckk_hat.move_img("maze_green", 1, 0, condition=cond)
        self.assertEqual(img_green.pos, (14,3))  # Can't move right

        cckk_hat.move_img("maze_green", 0, 1, condition=cond)
        self.assertEqual(img_green.pos, (14,3))  # Can't move up

        cckk_hat.move_img("maze_green", -1, 0, condition=cond)
        self.assertEqual(img_green.pos, (13,3))  # Can move right

        ##########

        cond = cckkCondition(unless_overlap=["maze"], keep_within_assoc=True)
        cckk_hat.move_img("maze_blue", -1, 0, condition=cond)
        self.assertEqual(img_blue.pos, (0,1))

        for i in range(14):
            cckk_hat.move_img("maze_blue", 1, 0, condition=cond)
            self.assertEqual(img_blue.pos, (i+1,1))

        cckk_hat.move_img("maze_blue", 1, 0, condition=cond)
        self.assertEqual(img_blue.pos, (14,1))  # Can't move any furhter right

        cckk_hat.move_img("maze_blue", 0, 2, condition=cond)
        self.assertEqual(img_blue.pos, (14,3))

        cckk_hat.move_img("maze_blue", 1, 0, condition=cond)
        self.assertEqual(img_blue.pos, (14,3))  # Can't move right

        cckk_hat.move_img("maze_blue", 0, 1, condition=cond)
        self.assertEqual(img_blue.pos, (14,3))  # Can't move up

        cckk_hat.move_img("maze_blue", -1, 0, condition=cond)
        self.assertEqual(img_blue.pos, (13,3))  # Can move right





if __name__ == "__main__":
    unittest.main()

