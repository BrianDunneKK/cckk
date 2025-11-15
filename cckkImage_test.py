import unittest
from cckk import cckkRectangle, cckkViewer, cckkImage


class test_cckkImage(unittest.TestCase):

    def test_cckkImage_colour_dict(self):
        self.assertTrue(cckkImage.def_colour_dict["r"] == (255, 0, 0))
        self.assertTrue(cckkImage.def_colour_dict["b"] == (0, 0, 255))
        self.assertFalse(cckkImage.def_colour_dict["g"] == (1, 2, 3))
        self.assertTrue(cckkImage.def_colour_dict["."] == None)
        self.assertTrue(cckkImage.reverse_colour_dict[(255, 0, 0)] == "r")
        self.assertTrue(cckkImage.reverse_colour_dict[(0, 255, 0)] == "g")
        self.assertTrue(cckkImage.reverse_colour_dict[(0, 0, 255)] == "b")
        self.assertTrue(cckkImage.reverse_colour_dict[None] == ".")

    def test_cckkImage_create_export(self):
        img_str = "rgb\ncym\nxw."
        img = cckkImage(imgStr=img_str)
        print("Before")
        print(img_str)
        print("-----")
        print("After")
        print(img.exportAsString())
        print("-----")
        self.assertTrue(img.exportAsString() == img_str)


if __name__ == "__main__":
    unittest.main()
