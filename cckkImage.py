class cckkImage:
    """Class representation of an image on a SenseHat"""
    imgAA = None
    img_xpos = 0    # X-position of the image relative to the camera
    img_ypos = 0    # Y-position of the image relative to the camera
    camera_cols = 0 # Number of columns in the camera
    camera_rows = 0 # Number of rows in the camera
    camera_fill = None # Fill colour if the image does not fill the camera. Default: [0,0,0] (black)

    def __init__(self, imgA = None, img_cols = 8, camera_cols = 8, camera_rows = 8, camera_horiz = "C", camera_vert = "C", camera_fill = [0,0,0]):
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
        self.camera_cols = camera_cols
        self.camera_rows = camera_rows
        self.camera_fill = camera_fill

        if (imgA is not None):
            self.setFromArray(imgA, img_cols, camera_horiz, camera_vert)

    def setFromArray(self, imgA, img_cols = 8, camera_horiz = "C", camera_vert = "C"):
        self.imgAA = [imgA[i:i+img_cols] for i in range(0, len(imgA), img_cols)]
        self.set_camera(camera_horiz, camera_vert)
        return self

    def set_camera(self, camera_horiz = "C", camera_vert = "C"):
        if camera_horiz.upper() == "L":
            self.img_xpos = 0
        elif camera_horiz.upper() == "R":
            self.img_xpos = self.camera_cols - self.img_cols
        else:
            self.img_xpos = int((self.camera_cols - self.img_cols)/2)
        
        if camera_vert.upper() == "T":
            self.img_ypos = 0
        elif camera_vert.upper() == "B":
            self.img_ypos = self.camera_rows - self.img_rows
        else:
            self.img_ypos = int((self.camera_rows - self.img_rows)/2)

        return self

    def pixels(self):
        """Image as seen through the camera"""
        camera_imgA = [self.camera_fill] * (self.camera_cols * self.camera_rows)
        for row in range(self.camera_rows):
            for col in range(self.camera_cols):
                col_img = col - self.img_xpos
                row_img = row - self.img_ypos
                if (col_img >= 0 & col_img < self.img_cols and row_img >= 0 & row_img < self.img_rows):
                    print(row_img, ", ", col_img)
                    camera_imgA[row*self.camera_rows + col] = self.imgAA[row_img][col_img]
        return camera_imgA

    @property
    def img_rows(self):
        """No. of rows in the image"""
        return len(self.imgAA)

    @property
    def img_cols(self):
        """No. of columns in the image"""
        return len(self.imgAA[0])

    def roll(self, dx, dy):
        result = []
        for r in range(nrows):
            new_r = (r - dy + self.img_rows) % self.img_rows
            new_row = []
            for c in range(ncols):
                new_c = (c - dx + self.img_cols) % self.img_cols
                new_row.append(self.imgAA[new_r][new_c])
            result.append(new_row)
        self.imgAA = result
        return self

    def move(self, dx, dy, fill):
        resultX = []
        result = []
        
        if dx > 0 & dx <= self.img_cols: # move right
            for r in range(self.img_rows):
                new_row = [fill]*dx
                for c in range(self.img_cols-dx):
                    new_row.append(self.imgAA[r][c])
                resultX.append(new_row)
        elif dx < 0 & dx >= -self.img_cols: # move left
            for r in range(self.img_rows):
                new_row = []
                for c in range(-dx, self.img_cols):
                    new_row.append(self.imgAA[r][c])
                new_row += [fill] * (-dx)
                resultX.append(new_row)
        else: # dx == 0 or invalid
            resultX = [row[:] for row in self.imgAA]

        if dy > 0 & dy <= self.img_rows: # move down
            for r in range(dy):
                result.append([fill] * self.img_cols)
            for r in range(self.img_rows - dy):
                result.append(resultX[r])
        elif dy < 0 & dy >= -self.img_rows: # move up
            for r in range(-dy, self.img_rows):
                result.append(resultX[r])
            for r in range(-dy):
                result.append([fill] * self.img_cols)
        else: # dy == 0 or invalid
            result = [row[:] for row in resultX]

        self.imgAA = result
        return self

    def imgPrint(self):
        str = ""
        for row in self.imgAA:
            for pixel in row:
                str += pixel + " "
            str += "\n"
        print(str)
