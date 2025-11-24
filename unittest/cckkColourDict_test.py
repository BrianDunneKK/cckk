import unittest
from cckk import cckkColourDict


class test_cckkColourDict(unittest.TestCase):

    def test_cckkColourDict_def_colour_dict(self):
        self.assertTrue(cckkColourDict.def_colour_dict["r"] == (255, 0, 0))
        self.assertTrue(cckkColourDict.def_colour_dict["b"] == (0, 0, 255))
        self.assertFalse(cckkColourDict.def_colour_dict["g"] == (1, 2, 3))
        self.assertTrue(cckkColourDict.def_colour_dict["."] == None)

    def test_cckkColourDict_colour_dict(self):
        col_dict = cckkColourDict()
        self.assertTrue(col_dict.dict["r"] == (255, 0, 0))
        self.assertTrue(col_dict.dict["b"] == (0, 0, 255))
        self.assertFalse(col_dict.dict["g"] == (1, 2, 3))
        self.assertTrue(col_dict.dict["."] == None)
        self.assertEqual(col_dict.get("g"), (0, 255, 0))
        self.assertEqual(col_dict.get("@"), None)

        self.assertTrue(col_dict.reverse_dict[(255, 0, 0)] == "r")
        self.assertTrue(col_dict.reverse_dict[(0, 255, 0)] == "g")
        self.assertTrue(col_dict.reverse_dict[(0, 0, 255)] == "b")
        self.assertTrue(col_dict.reverse_dict[None] == ".")
        self.assertEqual(col_dict.getRGB((0, 0, 255)), "b")
        self.assertEqual(col_dict.getRGB((1, 2, 3)), "?")

    def test_cckkColourDict_update_dict(self):
        dict2 = {
            "g": (128, 128, 128),  # Grey
            "*": (22,33,44)
        }
        col_dict = cckkColourDict(update_dict=dict2)
        self.assertEqual(col_dict.get("r"), (255, 0, 0))
        self.assertEqual(col_dict.get("g"), (128,128,128))
        self.assertEqual(col_dict.get("*"), (22,33,44))
        self.assertEqual(col_dict.getRGB((22,33,44)), "*")
        self.assertEqual(col_dict.getRGB((1, 2, 3)), "?")


if __name__ == "__main__":
    unittest.main()
