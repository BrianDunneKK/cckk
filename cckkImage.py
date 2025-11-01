import copy

class cckkRectangle:
    def __init__(self, xcols = 0, yrows = 0, xpos = 0, ypos = 0):
        """Contructs a cckkRectangle object.

        Args:
        xcols: Number of columns in the rectangle
        yrows: Number of rows in the rectangle
        xpos: X-position of the rectangle
        ypos: Y-position of the rectangle

        Returns:
        cckkRectangle  object

        Raises:
        Exception: Never
        """
        # Assign default values
        self._xcols = xcols # No. of columns in the rectangle
        self._yrows = yrows # No. of rows in the rectangle
        self._xpos = xpos   # X-position of the rectangle
        self._ypos = ypos   # Y-position of the rectangle

    @property
    def xcols(self):
        """No. of columns in the rectangle"""
        return self._xcols
    
    @xcols.setter
    def xcols(self, value):
        self._xcols = value

    @property
    def yrows(self):
        """No. of rows in the rectangle"""
        return self._yrows

    @yrows.setter
    def yrows(self, value):
        self._yrows = value

    @property
    def xpos(self):
        return self._xpos

    @xpos.setter
    def xpos(self, value):
        self._xpos = value

    @property
    def ypos(self):
        return self._ypos

    @ypos.setter
    def ypos(self, value):
        self._ypos = value

    def str(self):  
        return "cckkRectangle: " + str(self.xcols) + " x " + str(self.yrows) + " at (" + str(self.xpos) + "," + str(self.ypos) + ")\n"


class cckkViewer:
    def __init__(self, xcols = 8, yrows = 8, xpos = 0, ypos = 0, fill = [0,0,0], images = []):
        """Contructs a cckkViewer object.
        The viewer represents the view area through which an image is seen. This view can be displayed on a SenseHat LED matrix.

        Args:
        xcols: Number of columns in the viewer
        yrows: Number of rows in the viewer
        xpos: X-position of the viewer
        ypos: Y-position of the viewer
        fill: Fill colour if the image does not fill the viewer
        images: List of cckkImage objects that are viewed through the viewer, First image in the list is at the *front*, last image is at the back.

        Returns:
        cckkViewer  object

        Raises:
        Exception: Never
        """

        # Assign default values
        self._rect = cckkRectangle(xcols, yrows, xpos, ypos)
        self._fill = fill   # Fill colour if the image does not fill the viewer
        self._mer_xpos = 0  # X-position of the minimum enclosing rectangle of the images
        self._mer_ypos = 0  # Y-position of the minimum enclosing rectangle of the images
        self._mer_xcols = 0 # No. of columns in the minimum enclosing rectangle of the images
        self._mer_yrows = 0 # No. of rows in the minimum enclosing rectangle of the images
        self._images = [] # List of cckkImage objects that are viewed through the viewer. First image in the list is at the *back*.

        self.add_images(images)

    @property
    def xcols(self):
        """No. of columns in the image"""
        return self._rect.xcols
    
    @property
    def yrows(self):
        """No. of rows in the image"""
        return self._rect.yrows

    @property
    def xpos(self):
        return self._rect.xpos

    @xpos.setter
    def xpos(self, value):
        self._rect.xpos = value

    @property
    def ypos(self):
        return self._rect.ypos

    @ypos.setter
    def ypos(self, value):
        self._rect.ypos = value

    @property
    def background(self):
        return [self._fill] * (self.xcols * self.yrows)
    
    def add_images(self, images = []):
        """Add images to the viewer

        Args:
        images: List of cckkImage objects to view through the viewer. These are added on top of any existing images.  
        
        Raises:
        Exception: If invalid image specified
        """

        for img in reversed(images):
            if not isinstance(img, cckkImage):
                raise Exception("Invalid image specified")
            self._images.append(img)

        self.calculate_mer()

        return self

    def align_viewer(self, horiz = "C", vert = "C", img_idx = 0):
        """Align the viewer relative to an image
        Args:
        horiz: Viewer horizontal alignment relative to selected image.  Contains "L", "C" or "R" (left, centre, right)
        vert: Viewer vertical alignment relative to selected image. Contains "T", "C" or "B" (top, centre, bottom)
        img_idx: Index of the image in the viewer's image list to align the viewer to. Default: 0 (top image)

        Returns:
        cckkViewer object
        
        Raises:
        Exception: If no images in viewer or invalid image index specified
        """
        if len(self._images) == 0 or img_idx < 0 or img_idx >= len(self._images):
            raise Exception("No images in viewer or invalid image index specified")
        
        img = self._images[img_idx]

        if horiz.upper() == "L":
            self.xpos = img.xpos
        elif horiz.upper() == "R":
            self.xpos = img.xpos + img.xcols - self.xcols
        else:
            self.xpos = img.xpos + int((img.xcols - self.xcols)/2)
        
        if vert.upper() == "T":
            self.ypos = img.ypos
        elif vert.upper() == "B":
            self.ypos = img.ypos + img.yrows - self.yrows
        else:
            self.ypos = img.ypos + int((img.yrows - self.yrows)/2)

        return self

    def view(self):
        """View of the images through the viewer

        Returns:
        View of the image through the viewer as a one-dimensional array of colour elements, ready to be sent to the SenseHat
        """
        viewer_viewA = self.background

        for img in self._images:
            for yrow in range(self.yrows):
                for xcol in range(self.xcols):
                    xcol_img = self.xpos + xcol - img.xpos
                    yrow_img = self.ypos + yrow - img.ypos
                    if (xcol_img >= 0 and xcol_img < img.xcols and yrow_img >= 0 and yrow_img < img.yrows):
                        viewer_viewA[yrow*self.yrows + xcol] = img.image[yrow_img][xcol_img]

        return viewer_viewA

    def calculate_mer(self):
        """Calculate the minimum enclosing rectangle of the images"""
        self._mer_xpos = self._mer_ypos = self._mer_xcols = self._mer_yrows = 0
        if len(self._images) > 0:
            min_xpos = min([img.xpos for img in self._images])
            min_ypos = min([img.ypos for img in self._images])
            max_xpos = max([img.xpos + img.xcols for img in self._images])
            max_ypos = max([img.ypos + img.yrows for img in self._images])
            self._mer_xpos = min_xpos
            self._mer_ypos = min_ypos
            self._mer_xcols = max_xpos - min_xpos
            self._mer_yrows = max_ypos - min_ypos

        def move(self, dx, dy, keep = False):
            """Move the viewer

            Args:
            dx: Change in x-position
            dy: Change in y-position
            keep: If True, keeps the cammera over the MER of the images

            Returns:
            View of the image through the viewer as a one-dimensional array of colour elements, ready to be sent to the SenseHat
            """
            self.xpos = self.xpos + dx
            self.ypos = self.ypos + dy

            if keep:
                # Test bottom-right first so that top-left correction is not overridden
                if self.xpos + self.xcols < self._mer_xpos + self._mer_xcols:
                    self.xpos = self._mer_xpos + self._mer_xcols - self.xcols
                if self.ypos + self.yrows < self._mer_ypos + self._mer_yrows:
                    self.ypos = self._mer_ypos + self._mer_yrows - self.y
                if self.xpos < self._mer_xpos:
                    self.xpos = self._mer_xpos
                if self.ypos < self._mer_ypos:
                    self.ypos = self._mer_ypos
                    
            return self.view()
        
    def str(self):
        str = "cckkViewer:\n"
        str += "  Fill: " + str(self._fill) + "\n"
        str += "  " + self._rect.str() + "\n"
        str += "  MER: " + str(self._mer_xcols) + " x " + str(self._mer_yrows) + " at (" + str(self._mer_xpos) + "," + str(self._mer_ypos) + ")\n"
        str += "  Images: " + str(len(self._images)) + "\n"
        return str

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

    def __init__(self, imgA = None, imgStr = None, img_cols = 8, viewer_cols = 8, viewer_rows = 8, viewer_horiz = "C", viewer_vert = "C", viewer_fill = [0,0,0]):
        """Contructs a cckkImage object

        Args:
        imgA: One-dimensional array of image pixels. Each pixel is a list containing [R, G, B] (red, green, blue). Each R-G-B element must be an integer between 0 and 255.
        img_cols: Number of columns in the image
        viewer_cols: Number of columns in the viewer
        viewer_rows: Number of rows in the viewer
        viewer_horiz: Viewer horizontal alignment relative to image.  Contains "L", "C" or "R" (left, centre, right)
        viewer_vert: Viewer vertical alignment relative to image. Contains "T", "C" or "B" (top, centre, bottom)
        viewer_fill: Fill colour if the image does not fill the viewer

        Returns:
        cckkImage object

        Raises:
        Exception: If invalid image specified
        """

        # Assign default values
        self._imgAA = None    # Two-dimensional array of image pixels
        self._rect = cckkRectangle(0, 0, 0, 0) # Rectangle representing the image size and position

        self._viewer_cols = 0 # Number of columns in the viewer
        self._viewer_rows = 0 # Number of rows in the viewer
        self._viewer_fill = None # Fill colour if the image does not fill the viewer. Default: [0,0,0] (black)

        self._viewer_cols = viewer_cols
        self._viewer_rows = viewer_rows
        self._viewer_fill = viewer_fill

        if (imgA is not None):
            self.setFromArray(imgA, img_cols, viewer_horiz, viewer_vert)
        elif (imgStr is not None):
            self.setFromString(imgStr, None, viewer_horiz, viewer_vert)

    def setFromArray(self, imgA, img_cols = 8, viewer_horiz = "C", viewer_vert = "C"):
        self._imgAA = [imgA[i:i+img_cols] for i in range(0, len(imgA), img_cols)]
        self.update_size()
        return self

    def setFromString(self, imgStr, colour_dict = None, viewer_horiz = "C", viewer_vert = "C"):
        if (colour_dict is None):
            colour_dict = cckkImage.def_colour_dict

        self._imgAA = []
        img_lines = imgStr.splitlines()

        # Remove leading/trailing blank lines
        if (img_lines[0].strip() == ""): 
            img_lines = img_lines[1:]
        if (img_lines[-1].strip() == ""):
            img_lines = img_lines[:-1]

        for img_line in img_lines:
            line_pixels = []
            for ch in img_line.strip():
                if ch in colour_dict:
                    line_pixels.append(colour_dict[ch])
                else:
                    raise Exception("Invalid colour character '" + ch + "' in image string")
            self._imgAA.append(line_pixels)

        self.update_size()
        return self

    def align_image(self, viewer_horiz = "C", viewer_vert = "C"):
        if viewer_horiz.upper() == "L":
            self.xpos = 0
        elif viewer_horiz.upper() == "R":
            self.xpos = self._viewer_cols - self.xcols
        else:
            self.xpos = int((self._viewer_cols - self.xcols)/2)
        
        if viewer_vert.upper() == "T":
            self.ypos = 0
        elif viewer_vert.upper() == "B":
            self.ypos = self._viewer_rows - self.yrows
        else:
            self.ypos = int((self._viewer_rows - self.yrows)/2)

        return self.pixels()

    def pixels(self):
        """Image as seen through the viewer"""
        viewer_imgA = [self._viewer_fill] * (self._viewer_cols * self._viewer_rows)
        for row in range(self._viewer_rows):
            for col in range(self._viewer_cols):
                col_img = col - self.xpos
                row_img = row - self.ypos
                if (col_img >= 0 and col_img < self.xcols and row_img >= 0 and row_img < self.yrows):
                    viewer_imgA[row*self._viewer_rows + col] = self._imgAA[row_img][col_img]
        return viewer_imgA

    def update_size(self):
        """Update the image size"""
        self._rect.xcols = len(self._imgAA[0])
        self._rect.yrows = len(self._imgAA)

    @property
    def image(self):
        """Copy of the full image"""
        return copy.deepcopy(self._imgAA)

    @property
    def xcols(self):
        """No. of columns in the image"""
        return self._rect._xcols

    @property
    def yrows(self):
        """No. of rows in the image"""
        return self._rect.yrows

    @property
    def xpos(self):
        return self._rect.xpos

    @xpos.setter
    def xpos(self, value):
        self._rect.xpos = value

    @property
    def ypos(self):
        return self._rect.ypos

    @ypos.setter
    def ypos(self, value):
        self._rect.ypos = value

    def move(self, dx, dy, keep = False):
        """Move the image (relative to the viewer)

        Args:
        dx: Change in x-position
        dy: Change in y-position
        keep: If True, keeps the image fully within the viewer view

        Returns:
        View of the image through the viewer as a one-dimensional array of colour elements, ready to be sent to the SenseHat
        """
        self.xpos += dx
        self.ypos += dy

        if keep:
            if self.xpos < 0:
                self.xpos = 0
            if self.ypos < 0:
                self.ypos = 0
            if self.xpos + self.xcols > self._viewer_cols:
                self.xpos = self._viewer_cols - self.xcols
            if self.ypos + self.yrows > self._viewer_rows:
                self.ypos = self._viewer_rows - self.yrows
        return self
        
    def roll(self, dx, dy):
        result = []
        for r in range(self.yrows):
            new_r = (r - dy + self.yrows) % self.yrows
            new_row = []
            for c in range(self.xcols):
                new_c = (c - dx + self.xcols) % self.xcols
                new_row.append(self._imgAA[new_r][new_c])
            result.append(new_row)
        self._imgAA = result
        return self

    def str(self):
        as_str = "cckkImage:\n"
        str += "  " + self._rect.str() + "\n"
        for row in self._imgAA:
            for pixel in row:
                as_str += str(pixel) + " "
            as_str += "\n"
        return as_str
    