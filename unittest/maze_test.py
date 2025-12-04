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

        # Set up the Sense HAT
        cckk_hat = cckkSenseHatGame(images=[img_green,img_red,img_maze])
        cckk_hat.sense = cckkSenseHatEmu()

        cond = cckkCondition(unless_overlap=["maze"])
        cckk_hat.move_img("maze_green", -1, 0, keep_within=True, condition=cond)
        cckk_hat.align_to_img(img_name = "maze_green", keep_img_name = "maze")
        cckk_hat.update_pixels()

        self.assertEqual(img_green.pos, (0,1))


if __name__ == "__main__":
    unittest.main()

