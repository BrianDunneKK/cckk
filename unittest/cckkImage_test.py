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
        self.assertTrue(img.exportAsString() == img_str)

    def test_cckkImage_pixel(self):
        img_str = "rgb\ncym\nxw."
        img = cckkImage(imgStr=img_str)
        self.assertTrue(img.pixel(0,0) == (255,0,0))  # r

    def test_cckkImage_overlap(self):
        img1_str = "rgb\nc..\nxw."
        img2_str = "rgb\ncym\nxw."
        img1 = cckkImage(imgStr=img1_str)
        img2 = cckkImage(imgStr=img2_str)
        
        imgb_str = "rgb\ncym\nxw."  # Both image
        imgt_str = "rgb\nc..\nxw."  # Top image only
        img_overlap_b = img1.overlap(img2, top_only=False)
        img_overlap_t = img1.overlap(img2, top_only=True)
        self.assertTrue(img_overlap_b.exportAsString() == imgb_str)
        self.assertTrue(img_overlap_t.exportAsString() == imgt_str)
        
        print("-----")
        print(img1.exportAsString())
        print("-----")
        print(img2.exportAsString())
        print("-----")
        img2.move(1,0)
        img_overlap12 = img1.overlap(img2)
        img_overlap21 = img2.overlap(img1)
        self.assertTrue(img_overlap12.exportAsString() == "gb\ncy\nww")
        self.assertTrue(img_overlap21.exportAsString() == "rg\ncy\nxw")

        img2.move(0,1)
        img_overlap12 = img1.overlap(img2)
        img_overlap21 = img2.overlap(img1)
        print(img_overlap12.str())
        print("-----")
        print(img_overlap12.exportAsString())
        print("-----")
        print(img_overlap21.exportAsString())
        print("-----")
        self.assertTrue(img_overlap12.exportAsString() == "gb\nxw")


if __name__ == "__main__":
    unittest.main()
