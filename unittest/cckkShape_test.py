import unittest
from cckk import cckkShape, cckkViewer, cckkImage

class test_cckkShape(unittest.TestCase):
    def test_cckkImage_properties(self):
        rect0 = cckkShape()
        self.assertEqual(rect0.xcols, 0)
        self.assertEqual(rect0.yrows, 0)
        self.assertEqual(rect0.xpos, 0)
        self.assertEqual(rect0.ypos, 0)

    def test_cckkShape_intersection_no_overlap(self):
        r1 = cckkShape(xcols=2, yrows=2, xpos=0, ypos=0)
        r2 = cckkShape(xcols=2, yrows=2, xpos=3, ypos=3)
        self.assertTrue(r1.overlap(r2) is None)

    def test_cckkShape_intersection_overlap(self):
        r1 = cckkShape(xcols=3, yrows=3, xpos=0, ypos=0)
        r2 = cckkShape(xcols=3, yrows=3, xpos=1, ypos=1)
        inter = r1.overlap(r2)
        self.assertTrue(isinstance(inter, cckkShape))
        self.assertTrue(inter.xpos == 1)
        self.assertTrue(inter.ypos == 1)
        self.assertTrue(inter.xcols == 2)
        self.assertTrue(inter.yrows == 2)
        self.assertTrue(r1.overlap(r2) == r2.overlap(r1))

if __name__ == '__main__':
    unittest.main()