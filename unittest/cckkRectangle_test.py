import unittest
from cckk import cckkRectangle, cckkViewer, cckkImage

class test_cckkRectangle(unittest.TestCase):
    def test_cckkImage_properties(self):
        rect0 = cckkRectangle()
        self.assertEqual(rect0.xcols, 0)
        self.assertEqual(rect0.yrows, 0)
        self.assertEqual(rect0.xpos, 0)
        self.assertEqual(rect0.ypos, 0)

    def test_cckkRectangle_intersection_no_overlap(self):
        r1 = cckkRectangle(xcols=2, yrows=2, xpos=0, ypos=0)
        r2 = cckkRectangle(xcols=2, yrows=2, xpos=3, ypos=3)
        self.assertTrue(r1.overlap(r2) is None)

    def test_cckkRectangle_intersection_overlap(self):
        r1 = cckkRectangle(xcols=3, yrows=3, xpos=0, ypos=0)
        r2 = cckkRectangle(xcols=3, yrows=3, xpos=1, ypos=1)
        inter = r1.overlap(r2)
        self.assertTrue(isinstance(inter, cckkRectangle))
        self.assertTrue(inter.xpos == 1)
        self.assertTrue(inter.ypos == 1)
        self.assertTrue(inter.xcols == 2)
        self.assertTrue(inter.yrows == 2)
        self.assertTrue(r1.overlap(r2) == r2.overlap(r1))

if __name__ == '__main__':
    unittest.main()