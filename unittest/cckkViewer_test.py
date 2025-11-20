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
        self.assertEqual(img_view.exportAsString(), view_str)

    def test_cckkViewer_layers(self):
        imgr_str = "rrr\nrrr\nrrr"
        imgg_str = ".gg\n.gg\n.gg"
        imgb_str = "..b\n..b\n..b"
        imgr = cckkImage(imgStr=imgr_str, name="red")
        imgg = cckkImage(imgStr=imgg_str, name="green")
        imgb = cckkImage(imgStr=imgb_str, name="blue")
        viewer = cckkViewer(images=[imgb, imgg, imgr], xcols=3, yrows=3)
        img_view = viewer.view()
        view_str = "rgb\nrgb\nrgb"
        self.assertEqual(img_view.exportAsString(), view_str)
        
        viewer.hide_image("green")
        img_view = viewer.view()
        view_str = "rrb\nrrb\nrrb"
        self.assertEqual(img_view.exportAsString(), view_str)

        viewer = cckkViewer(images=[imgg, imgr, imgb], xcols=3, yrows=3)
        img_view = viewer.view()
        view_str = "rgg\nrgg\nrgg"
        self.assertEqual(img_view.exportAsString(), view_str)

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

    def test_cckkViewer_overlap_multi(self):
        img1_str = "rgb\nc..\nxw."
        imgt_str = "tt\ntt\ntt"
        imgv_str = "vvv"
        img1 = cckkImage(imgStr=img1_str, name="one")
        imgt = cckkImage(imgStr=imgt_str, name = "turquoise")
        imgv = cckkImage(imgStr=imgv_str, name = "violet")
        viewer = cckkViewer(images=[img1, imgt, imgv], xcols=3, yrows=3)

        img_1_tv_str = "rg.\nct.\nxwv"
        img_1tv = viewer.overlap_multi("one", ["turquoise", "violet"])
        self.assertEqual(img_1tv.exportAsString(), img_1_tv_str)

        imgv.move(0,2)
        img_1_tv_str = "rgb\nct.\nxw."
        img_1tv = viewer.overlap_multi("one", ["turquoise", "violet"])
        self.assertEqual(img_1tv.exportAsString(), img_1_tv_str)

        img_1tv = viewer.overlap_multi("one")
        self.assertEqual(img_1tv.exportAsString(), img_1_tv_str)

        img_t_v_str = "tt"
        img_t_v = viewer.overlap_multi("turquoise")
        self.assertEqual(img_t_v.exportAsString(), img_t_v_str)

        img_v = viewer.overlap_multi("violet")
        self.assertEqual(img_v, None)


    def test_cckkViewer_overlap_with(self):
        img1_str = "rgb\nc..\nxw."
        imgt_str = "tt\ntt\ntt"
        imgv_str = "vvv"
        img1 = cckkImage(imgStr=img1_str, name="one")
        imgt = cckkImage(imgStr=imgt_str, name = "turquoise")
        imgv = cckkImage(imgStr=imgv_str, name = "violet")
        viewer = cckkViewer(images=[img1, imgt, imgv], xcols=3, yrows=3)

        self.assertEqual(viewer.overlap_with("one", ["turquoise", "violet"]), "turquoise")
        self.assertEqual(viewer.overlap_with("one"), "turquoise")
        self.assertEqual(viewer.overlap_with("turquoise"), "violet")
        self.assertEqual(viewer.overlap_with("violet"), None)




if __name__ == "__main__":
    unittest.main()
