import unittest
from cckk import cckkRectangle, cckkViewer, cckkImage

class test_cckk(unittest.TestCase):

    def test_cckkImage_setFromImageFile(self):
        img = cckkImage()
        img.create_from_image_file("test_image.png")
        self.assertTrue(img.xcols == 8)
        self.assertTrue(img.yrows == 8)
        self.assertTrue(len(img.image) == img.yrows)
        self.assertTrue(len(img.image[0]) == img.xcols)

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()