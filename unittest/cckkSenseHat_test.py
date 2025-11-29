import unittest
from cckk import cckkSenseHat, cckkSenseHatEmu


class test_cckkSenseHat(unittest.TestCase):

    def test_cckkSenseHat_construct(self):
        hat = cckkSenseHat()
        self.assertTrue(hat is not None)

        # self.assertRaises(Exception, cckkSenseHat, None)
        with self.assertRaises(Exception) as context:
            hat._set_sensehat(None)
        self.assertTrue('A SenseHat object must be provided' in str(context.exception))
        
        hat_emu = cckkSenseHatEmu()
        try:
            hat._set_sensehat(hat_emu)
        except Exception:
            self.fail("setSenseHat() raised Exception unexpectedly!")
        

if __name__ == "__main__":
    unittest.main()
