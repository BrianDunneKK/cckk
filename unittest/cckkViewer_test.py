import unittest
from cckk import cckkImage, cckkViewer, cckkAction, cckkCondition, cckkColourDict


class test_cckkViewer(unittest.TestCase):

    def test_cckkAction_id(self):
        a1 = cckkAction("one")
        a2 = cckkAction("two", "target2")
        a3 = cckkAction("three", context=(2,3))
        self.assertEqual(a1.id, 1)
        self.assertEqual(a2.id, 2)
        self.assertEqual(a3.id, 3)
        self.assertEqual(a2.target, "target2")
        self.assertEqual(a3.context, (2,3))

    def test_cckkViewer_lastAction(self):
        start_id = cckkAction._nextID - 1
        img = cckkImage(imgStr="rgb\ncym\nxw", name = "image")
        viewer = cckkViewer(images=[img])
        viewer.move(1,2)
        self.assertEqual(viewer.lastAction, 1+start_id)
        viewer.moveTo_img("image", 3, 4)
        viewer.move_img("image", 5, 6)
        self.assertEqual(viewer.lastAction, 3+start_id)

    def test_cckkViewer_undo(self):
        img = cckkImage(imgStr="rgb\ncym\nxw", name = "image")
        viewer = cckkViewer(images=[img])
        viewer.move(1,2)
        self.assertEqual(viewer.pos, (1,2))
        viewer.move(3,4)
        self.assertEqual(viewer.pos, (4,6))
        viewer.undo()
        self.assertEqual(viewer.pos, (1,2))

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
        violet = cckkColourDict.def_colour_dict["v"]
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

    def test_cckkViewer_overlap_multi_count(self):
        img1_str = "..\nrr"
        img2_str = "b.\nb."
        imgv_str = "v"
        img1 = cckkImage(imgStr=img1_str, name="one")
        img2 = cckkImage(imgStr=img2_str, name = "two")
        imgv = cckkImage(imgStr=imgv_str, name = "violet", pos=(1,1))
        viewer = cckkViewer(images=[imgv, img1, img2], xcols=2, yrows=2)

        self.assertEqual(viewer.overlap_count("violet", "one"), 0)
        self.assertEqual(viewer.overlap_count("violet", "two"), 0)
        self.assertEqual(viewer.overlap_multi_count("violet", ["one"]), 0)
        self.assertEqual(viewer.overlap_multi_count("violet", ["one", "two"]), 0)

        imgv.moveTo(0,0)
        self.assertEqual(viewer.overlap_multi_count("violet", ["one", "two"]), 1)

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

    def test_cckkViewer_move_condition(self):
        img_green = cckkImage(imgA = [(0,255,0)], name="green", pos = (0,6))
        img_blue = cckkImage(imgA = [(0,0,255)]*4, name="blue", pos=(0,5))
        viewer = cckkViewer(images=[img_green,img_blue])
        self.assertEqual(img_green.pos, (0,6))

        cond = cckkCondition(unless_overlap=["blue"])
        viewer.move_img("green", 0, -1, condition=cond)
        self.assertEqual(img_green.pos, (0,6))

        viewer.move_img("green", 0, -1)
        self.assertEqual(img_green.pos, (0,5))

        cond2 = cckkCondition(only_if_overlap=["blue"])
        viewer.moveTo_img("green", 0, 5)
        self.assertEqual(img_green.pos, (0,5))
        viewer.move_img("green", 3, 0, condition=cond2)
        self.assertEqual(img_green.pos, (3,5))

        viewer.move_img("green", 1, 0, condition=cond2)
        self.assertEqual(img_green.pos, (3,5))
        viewer.move_img("green", -1, 0, condition=cond2)
        self.assertEqual(img_green.pos, (2,5))

    def test_cckkViewer_align(self):
        img_str = "rr\nrr"
        img = cckkImage(imgStr=img_str, name="red")
        viewer = cckkViewer(images=[img], xcols=8, yrows=8)
        viewer.align_image("red")
        pos = viewer.find_image("red").pos
        self.assertEqual(pos, (3,3))


if __name__ == "__main__":
    unittest.main()



