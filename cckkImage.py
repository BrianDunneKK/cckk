class cckkImage:
    """Class representation of an image on a SenseHat"""
    def_colour_dict = {
        '.': (0,0,0)         # Black
        , 'w': (255,255,255) # White
        , 'r': (255,0,0)     # Red
        , 'g': (0,255,0)     # Green
        , 'b': (0,0,255)     # Blue
        , 'c': (0,255,255)   # Cyan
        , 'y': (255,255,0)   # Yellow
        , 'm': (255,0,255)   # Magenta
        , 'W': (128,128,128) # Gray
        , 'R': (128,0,0)     # Maroon
        , 'G': (0,128,0)     # Dark Green
        , 'B': (0,0,128)     # Navy
        , 'C': (0,128,128)   # Teal
        , 'Y': (128,128,0)   # Olive
        , 'M': (128,0,128)   # Purple
        , 's': (192,192,192) # Silver
        }

    def __init__(self, imgA = None, imgStr = None, img_cols = 8, camera_cols = 8, camera_rows = 8, camera_horiz = "C", camera_vert = "C", camera_fill = [0,0,0]):
        """Contructs a cckkImage object

        Args:
        imgA: One-dimensional array of colours elements. Each colour element is a list containing [R, G, B] (red, green, blue). Each R-G-B element must be an integer between 0 and 255.
        img_cols: Number of columns in the image
        camera_cols: Number of columns in the camera
        camera_rows: Number of rows in the camera
        camera_horiz: Camera horizontal alignment relative to image.  Contains "L", "C" or "R" (left, centre, right)
        camera_vert: Camera vertical alignment relative to image. Contains "T", "C" or "B" (top, centre, bottom)
        camera_fill: Fill colour if the image does not fill the camera

        Returns:
        cckImage object

        Raises:
        Exception: If invalid image specified
        """

        # Assign default values
        self._imgAA = None
        self._img_xpos = 0    # X-position of the image relative to the camera
        self._img_ypos = 0    # Y-position of the image relative to the camera
        self._camera_cols = 0 # Number of columns in the camera
        self._camera_rows = 0 # Number of rows in the camera
        self._camera_fill = None # Fill colour if the image does not fill the camera. Default: [0,0,0] (black)


        self._camera_cols = camera_cols
        self._camera_rows = camera_rows
        self._camera_fill = camera_fill

        if (imgA is not None):
            self.setFromArray(imgA, img_cols, camera_horiz, camera_vert)
        elif (imgStr is not None):
            self.setFromString(imgStr, None, camera_horiz, camera_vert)

    def setFromArray(self, imgA, img_cols = 8, camera_horiz = "C", camera_vert = "C"):
        self._imgAA = [imgA[i:i+img_cols] for i in range(0, len(imgA), img_cols)]
        self.align_image(camera_horiz, camera_vert)
        return self.pixels()

    def setFromString(self, imgStr, colour_dict = None, camera_horiz = "C", camera_vert = "C"):
        if (colour_dict is None):
            colour_dict = cckkImage.def_colour_dict

        self._imgAA = []
        img_lines = imgStr.splitlines()
        if (img_lines[0].strip() == ""):
            img_lines = img_lines[1:]

        for img_line in img_lines:
            line_pixels = []
            for ch in img_line.strip():
                if ch in colour_dict:
                    line_pixels.append(colour_dict[ch])
                else:
                    print("<"+img_line+">")
                    print("<"+ch+">")
                    raise Exception("Invalid colour character '" + ch + "' in image string")
            self._imgAA.append(line_pixels)

        self.align_image(camera_horiz, camera_vert)

        return self.pixels()

    def align_image(self, camera_horiz = "C", camera_vert = "C"):
        if camera_horiz.upper() == "L":
            self._img_xpos = 0
        elif camera_horiz.upper() == "R":
            self._img_xpos = self._camera_cols - self.img_cols
        else:
            self._img_xpos = int((self._camera_cols - self.img_cols)/2)
        
        if camera_vert.upper() == "T":
            self._img_ypos = 0
        elif camera_vert.upper() == "B":
            self._img_ypos = self._camera_rows - self.img_rows
        else:
            self._img_ypos = int((self._camera_rows - self.img_rows)/2)

        return self.pixels()

    def pixels(self):
        """Image as seen through the camera"""
        camera_imgA = [self._camera_fill] * (self._camera_cols * self._camera_rows)
        for row in range(self._camera_rows):
            for col in range(self._camera_cols):
                col_img = col - self._img_xpos
                row_img = row - self._img_ypos
                if (col_img >= 0 and col_img < self.img_cols and row_img >= 0 and row_img < self.img_rows):
                    camera_imgA[row*self._camera_rows + col] = self._imgAA[row_img][col_img]
        return camera_imgA

    @property
    def img_rows(self):
        """No. of rows in the image"""
        return len(self._imgAA)

    @property
    def img_cols(self):
        """No. of columns in the image"""
        return len(self._imgAA[0])

    @property
    def xpos(self):
        return self._img_xpos

    @xpos.setter
    def xpos(self, value):
        self._img_xpos = value

    @property
    def ypos(self):
        return self._img_ypos

    @xpos.setter
    def ypos(self, value):
        self._img_ypos = value

    def move(self, dx, dy):
        self._img_xpos += dx
        self._img_ypos += dy
        return self.pixels()
        
    def roll(self, dx, dy):
        result = []
        for r in range(self.img_rows):
            new_r = (r - dy + self.img_rows) % self.img_rows
            new_row = []
            for c in range(self.img_cols):
                new_c = (c - dx + self.img_cols) % self.img_cols
                new_row.append(self._imgAA[new_r][new_c])
            result.append(new_row)
        self._imgAA = result
        return self.pixels()

    def imgPrint(self):
        str = ""
        for row in self._imgAA:
            for pixel in row:
                str += pixel + " "
            str += "\n"
        print(str)
