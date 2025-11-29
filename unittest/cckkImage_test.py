import unittest
from cckk import cckkImage, cckkRectangle


class test_cckkImage(unittest.TestCase):

    def test_cckkImage_create_export(self):
        img_str = "rgb\ncym\nxw."
        img = cckkImage(imgStr=img_str)
        self.assertEqual(img.export_as_string(), img_str)

    def test_cckkImage_create_from_pixel(self):
        img = cckkImage()
        img.create_from_pixel(4, 3)
        self.assertEqual(img.export_as_string(), "....\n....\n....")

        img.create_from_pixel(3, 4, pixel=(0, 255, 0))
        self.assertEqual(img.export_as_string(), "ggg\nggg\nggg\nggg")

    def test_cckkImage_properties(self):
        img0 = cckkImage()
        self.assertEqual(img0.xcols, 0)
        self.assertEqual(img0.yrows, 0)
        self.assertEqual(img0.xpos, 0)
        self.assertEqual(img0.ypos, 0)

        img_str = "rgb\ncym\nxw."
        img = cckkImage(imgStr=img_str)
        self.assertTrue(img.pixel_as_string(0,0) == "x")
        self.assertTrue(img.pixel_as_string(1,1) == "y")
        self.assertTrue(img.pixel_as_string(2,2) == "b")
        self.assertTrue(img.pixel_as_string(2,0) == ".")
        self.assertTrue(img.pixel_as_string(0,2) == "r")
        self.assertEqual(img.xcols, 3)
        self.assertEqual(img.yrows, 3)
        self.assertEqual(img.xpos, 0)
        self.assertEqual(img.ypos, 0)

    def test_cckkImage_move(self):
        img = cckkImage()
        img.move_to(3,5)
        self.assertEqual(img.xpos, 3)
        self.assertEqual(img.ypos, 5)

        pos = (4,6)
        img.move_to(pos)
        self.assertEqual(img.xpos, pos[0])
        self.assertEqual(img.ypos, pos[1])

        img.move(3,5)
        self.assertEqual(img.xpos, 7)
        self.assertEqual(img.ypos, 11)

        dxdy = (-3,-2)
        img.move(dxdy)
        self.assertEqual(img.xpos, 4)
        self.assertEqual(img.ypos, 9)

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
        img.create_from_pixel(4, 3)
        self.assertEqual(img.export_as_string(), "....\n....\n....")
        img.setPixel(0, 0, pixel=(255, 0, 0))
        img.setPixel(1, 0, pixel=(0, 255, 0))
        img.setPixel(2, 1, pixel=(0, 0, 255))
        self.assertEqual(img.export_as_string(), "....\n..b.\nrg..")

    def test_cckkImage_get_rect(self):
        img_str = "rgb\ncym\nxw."
        img = cckkImage(imgStr=img_str)
        sub_rect = cckkRectangle(1, 1, 2, 2)
        self.assertEqual(img.get_sub_image(sub_rect).export_as_string(), "b")
        sub_rect = cckkRectangle(2, 2, 1, 1)
        self.assertEqual(img.get_sub_image(sub_rect).export_as_string(), "gb\nym")
        sub_rect = cckkRectangle(1, 2, 2, 1)
        self.assertEqual(img.get_sub_image(sub_rect).export_as_string(), "b\nm")

    def test_cckkImage_overlap(self):
        img1_str = "rgb\nc..\nxw."
        img2_str = "rgb\ncym\nxw."
        img1 = cckkImage(imgStr=img1_str)
        img2 = cckkImage(imgStr=img2_str)
        
        imgb_str = "rgb\ncym\nxw."  # Both image
        imgt_str = "rgb\nc..\nxw."  # Top image only
        img_overlap_b = img1.overlap(img2, top_only=False)
        img_overlap_t = img1.overlap(img2, top_only=True)
        self.assertEqual(img_overlap_b.export_as_string(), imgb_str)
        self.assertEqual(img_overlap_t.export_as_string(), imgt_str)
        
        img2.move(1,0)
        img_overlap12 = img1.overlap(img2)
        img_overlap21 = img2.overlap(img1)
        self.assertEqual(img_overlap12.export_as_string(), "gb\ncy\nww")
        self.assertEqual(img_overlap21.export_as_string(), "rg\ncy\nxw")

        img2.move(0,1)
        img_overlap12 = img1.overlap(img2)
        img_overlap21 = img2.overlap(img1)
        self.assertEqual(img_overlap12.export_as_string(), "gb\nxw")

        img2.move_to(-1,-1)
        img_overlap12 = img1.overlap(img2)
        img_overlap21 = img2.overlap(img1)
        self.assertEqual(img_overlap12.export_as_string(), "cb\nxw")
        self.assertEqual(img_overlap21.export_as_string(), "gb\nym")

    def test_cckkImage_overlap_multi(self):
        img1_str = "rgb\nc..\nxw."
        imgt_str = "tt\ntt\ntt"
        imgv_str = "vvv"
        img1 = cckkImage(imgStr=img1_str)
        imgt = cckkImage(imgStr=imgt_str)
        imgv = cckkImage(imgStr=imgv_str)
        
        img1_tv_str = "rg.\nct.\nxwv"
        img1_tv = img1.overlap_multi([imgt, imgv])
        self.assertEqual(img1_tv.export_as_string(), img1_tv_str)

        imgv.move(0,2)
        img1_tv_str = "rgb\nct.\nxw."
        img1_tv = img1.overlap_multi([imgt, imgv])
        self.assertEqual(img1_tv.export_as_string(), img1_tv_str)


if __name__ == "__main__":
    unittest.main()
