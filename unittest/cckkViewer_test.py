import unittest
from cckk import cckkImage, cckkViewer


class test_cckkViewer(unittest.TestCase):

    def test_cckkViewer_properties(self):
        viewer0 = cckkViewer()
        self.assertEqual(viewer0.xcols, 8) # Default size 8x8 (same as SenseHAT)
        self.assertEqual(viewer0.yrows, 8)
        self.assertEqual(viewer0.xpos, 0)
        self.assertEqual(viewer0.ypos, 0)
        self.assertEqual(viewer0.background, [(0,0,0)] * 64)  # Default black background

        img_str = """
rgbcymxw
rgbcymxw
rgbcymxw
rgbcymxw
rgbcymxw
rgbcymxw
rgbcymxw
rgbcymxw"""
        img = cckkImage(imgStr=img_str)
        viewer1 = cckkViewer(images=[img])
        self.assertEqual(viewer1.xcols, 8)
        self.assertEqual(viewer1.yrows, 8)
        self.assertEqual(viewer1.xpos, 0)
        self.assertEqual(viewer1.ypos, 0)
  
    def test_cckkViewer_view(self):
        img_str = "rgb\ncym\nxw."
        img = cckkImage(imgStr=img_str)
        violet = cckkImage.def_colour_dict["v"]
        viewer = cckkViewer(images=[img], xcols=4, yrows=4, fill=violet)  # Violet background ("v")
        img_view = viewer.view()
        view_str = "vvvv\nrgbv\ncymv\nxwvv"
        self.assertTrue(img_view.exportAsString() == view_str)

    def test_cckkViewer_pixels(self):
        img_str = "rg.\n.cy\nxw."
        img = cckkImage(imgStr=img_str)
        viewer = cckkViewer(images=[img], xcols=3, yrows=3)
        expected_pixels = [
            (255, 0, 0), (0, 255, 0), (0, 0, 0),
            (0, 0, 0), (0, 255, 255), (255, 255, 0),
            (0, 0, 0), (255, 255, 255), (0, 0, 0)
        ]
        self.assertEqual(viewer.pixels, expected_pixels)

if __name__ == "__main__":
    unittest.main()
