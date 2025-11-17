import unittest
from cckk import cckkImage, cckkRectangle


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

    def test_cckkImage_create_from_pixel(self):
        img = cckkImage()
        img.createFromPixel(4, 3)
        self.assertEqual(img.exportAsString(), "....\n....\n....")

        img.createFromPixel(3, 4, pixel=(0, 255, 0))
        self.assertEqual(img.exportAsString(), "ggg\nggg\nggg\nggg")

    def test_cckkImage_properties(self):
        img0 = cckkImage()
        self.assertEqual(img0.xcols, 0)
        self.assertEqual(img0.yrows, 0)
        self.assertEqual(img0.xpos, 0)
        self.assertEqual(img0.ypos, 0)

        img_str = "rgb\ncym\nxw."
        img = cckkImage(imgStr=img_str)
        self.assertTrue(img.pixelAsString(0,0) == "x")
        self.assertTrue(img.pixelAsString(1,1) == "y")
        self.assertTrue(img.pixelAsString(2,2) == "b")
        self.assertTrue(img.pixelAsString(2,0) == ".")
        self.assertTrue(img.pixelAsString(0,2) == "r")
        self.assertEqual(img.xcols, 3)
        self.assertEqual(img.yrows, 3)
        self.assertEqual(img.xpos, 0)
        self.assertEqual(img.ypos, 0)

    def test_cckkImage_pixels(self):
        img_str = "rg.\n.cy\nxw."
        img = cckkImage(imgStr=img_str)
        expected_pixels = [
            (255, 0, 0), (0, 255, 0), None,
            None, (0, 255, 255), (255, 255, 0),
            (0, 0, 0), (255, 255, 255), None
        ]
        self.assertEqual(img.pixels, expected_pixels)
        
    def test_cckkImage_set_pixel(self):
        img = cckkImage()
        img.createFromPixel(4, 3)
        self.assertEqual(img.exportAsString(), "....\n....\n....")
        img.setPixel(0, 0, pixel=(255, 0, 0))
        img.setPixel(1, 0, pixel=(0, 255, 0))
        img.setPixel(2, 1, pixel=(0, 0, 255))
        self.assertEqual(img.exportAsString(), "....\n..b.\nrg..")

    def test_cckkImage_get_rect(self):
        img_str = "rgb\ncym\nxw."
        img = cckkImage(imgStr=img_str)
        sub_rect = cckkRectangle(1, 1, 2, 2)
        self.assertEqual(img.getSubImage(sub_rect).exportAsString(), "b")
        sub_rect = cckkRectangle(2, 2, 1, 1)
        self.assertEqual(img.getSubImage(sub_rect).exportAsString(), "gb\nym")
        sub_rect = cckkRectangle(1, 2, 2, 1)
        self.assertEqual(img.getSubImage(sub_rect).exportAsString(), "b\nm")

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
        
        img2.move(1,0)
        img_overlap12 = img1.overlap(img2)
        img_overlap21 = img2.overlap(img1)
        self.assertTrue(img_overlap12.exportAsString() == "gb\ncy\nww")
        self.assertTrue(img_overlap21.exportAsString() == "rg\ncy\nxw")

        img2.move(0,1)
        img_overlap12 = img1.overlap(img2)
        img_overlap21 = img2.overlap(img1)
        self.assertTrue(img_overlap12.exportAsString() == "gb\nxw")

        img2.moveTo(-1,-1)
        img_overlap12 = img1.overlap(img2)
        img_overlap21 = img2.overlap(img1)
        self.assertTrue(img_overlap12.exportAsString() == "cb\nxw")
        self.assertTrue(img_overlap21.exportAsString() == "gb\nym")


if __name__ == "__main__":
    unittest.main()
