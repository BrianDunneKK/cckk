# To Do
# 1. Use cckkRectangle as base class for cckkImage and cckkViewer
# 2. Move calculate_mer() to cckkRectangle   ## attributes = [node.attr for node in nodes]
# 4. Intersection of rectangles function to cckkRectangle ... collision detection

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
        self.set(xcols, yrows, xpos, ypos)

    def set(self, xcols = 0, yrows = 0, xpos = 0, ypos = 0):
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

    def keep_within(self, outer_rect = None):
        """Adjust the rectangle position to keep it fully within another rectangle.
        Test bottom-right first so that top-left correction is not overridden

        Args:
        outer_rect: cckkRectangle object representing the outer rectangle

        Returns:
        cckkRectangle object
        """
        if outer_rect is not None:
            if self.xpos + self.xcols > outer_rect.xpos + outer_rect.xcols:
                self.xpos = outer_rect.xpos + outer_rect.xcols - self.xcols
            if self.ypos + self.yrows > outer_rect.ypos + outer_rect.yrows:
                self.ypos = outer_rect.ypos + outer_rect.yrows - self.yrows
            if self.xpos < outer_rect.xpos:
                self.xpos = outer_rect.xpos
            if self.ypos < outer_rect.ypos:
                self.ypos = outer_rect.ypos

        return self
    
    def str(self):  
        return "cckkRectangle: " + str(self.xcols) + " x " + str(self.yrows) + " at (" + str(self.xpos) + "," + str(self.ypos) + ")\n"


class cckkViewer(cckkRectangle):
    ## Class representation of a viewer of images for display on a SenseHat
    # The viewer represents the view area through which an image is seen. This view can be displayed on a SenseHat LED matrix.
    # The viewer can contain multiple images, which are layered on top of each other.
    # The base class cckkRectangle is used to represent the viewer size and position.
    ##############################################################################################

    """Class representation of a viewer of images for display on a SenseHat"""

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
        cckkViewer object

        Raises:
        Exception: Never
        """
        super().__init__(xcols=xcols, yrows=yrows, xpos=xpos, ypos=ypos)  # Initialize cckkRectangle base class
        self._fill = fill   # Fill colour if the image does not fill the viewer
        self._mer_rect = cckkRectangle() # Minimum enclosing rectangle of the images
        self._images = [] # List of cckkImage objects that are viewed through the viewer. First image in the list is at the *back*.
        self.add_images(images)

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

    def align(self, img_name = "", horiz = "C", vert = "C"):
        """Align the viewer relative to an image
        Args:
        img_idx: Index of the image in the viewer's image list to align the viewer to. Default: 0 (top image)
        horiz: Viewer horizontal alignment relative to selected image.  Contains "L", "C" or "R" (left, centre, right)
        vert: Viewer vertical alignment relative to selected image. Contains "T", "C" or "B" (top, centre, bottom)

        Returns:
        cckkViewer object
        
        Raises:
        Exception: If no images in viewer or invalid image index specified
        """
        img_idx = self.find_image(img_name)
        if img_idx < 0:
            img_idx = 0

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
        
        self._mer_rect.set()
        if len(self._images) > 0:
            min_xpos = min([img.xpos for img in self._images])
            min_ypos = min([img.ypos for img in self._images])
            max_xpos = max([img.xpos + img.xcols for img in self._images])
            max_ypos = max([img.ypos + img.yrows for img in self._images])
            self._mer_rect.set(
                xcols = max_xpos - min_xpos,
                yrows = max_ypos - min_ypos,
                xpos = min_xpos,
                ypos = min_ypos
            )

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
            self.keep_within(self._mer_rect)
                
        return self.view()
        
    def find_image(self, name):
        """Find an image in the viewer by name

        Args:
        name: Name of the image to find

        Returns:
        Index of the image in the viewer's image list, or -1 if not found
        """
        for idx, img in enumerate(self._images):
            if img._name == name:
                return idx
        return -1
    
    def move_img(self, name, dx, dy, keep = False):
        idx = self.find_image(name)
        if idx >= 0:
            self._images[idx].move(dx, dy, self._mer_rect if keep else None)
        return self
    
    def align_image(self, name, horiz = "C", vert = "C"):
        idx = self.find_image(name)
        if idx >= 0:
            self._images[idx].align(self, horiz, vert)
        return self

    def str(self):
        str = "cckkViewer:\n"
        str += "  " + super().str() + "\n"
        str += "  Fill: " + str(self._fill) + "\n"
        str += "  MER: " + self._mer_rect.str() + "\n"
        str += "  Images: " + str(len(self._images)) + "\n"
        return str


class cckkImage(cckkRectangle):
    ## Class representation of an image
    # The base class cckkRectangle is used to represent the image size and position.
    ##############################################################################################

    """Class representation of an image"""
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

    def __init__(self, imgA = None, imgStr = None, img_cols = 8, name = ""):
        """Contructs a cckkImage object

        Args:
        imgA: One-dimensional array of image pixels. Each pixel is a list containing [R, G, B] (red, green, blue). Each R-G-B element must be an integer between 0 and 255.
        img_cols: Number of columns in the image

        Returns:
        cckkImage object

        Raises:
        Exception: If invalid image specified
        """
        super().__init__()  # Initialize cckkRectangle base class
        self._imgAA = None  # Two-dimensional array of image pixels
        self._name = name   # Name of the image

        if (imgA is not None):
            self.setFromArray(imgA, img_cols)
        elif (imgStr is not None):
            self.setFromString(imgStr, None)

    def setFromArray(self, imgA, img_cols = 8):
        self._imgAA = [imgA[i:i+img_cols] for i in range(0, len(imgA), img_cols)]
        self.update_size()
        return self

    def setFromString(self, imgStr, colour_dict = None):
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

    def align(self, viewer_rect, horiz = "C", vert = "C"):
        if horiz.upper() == "L":
            self.xpos = viewer_rect.xpos
        elif horiz.upper() == "R":
            self.xpos = viewer_rect.xpos + viewer_rect.xcols - self.xcols
        else:
            self.xpos = viewer_rect.xpos + int((viewer_rect.xcols - self.xcols)/2)
        
        if vert.upper() == "T":
            self.ypos = viewer_rect.ypos
        elif vert.upper() == "B":
            self.ypos = viewer_rect.ypos + viewer_rect.yrows - self.yrows
        else:
            self.ypos = viewer_rect.ypos + int((viewer_rect.yrows - self.yrows)/2)

        return self

    def update_size(self):
        """Update the image size"""
        self.xcols = len(self._imgAA[0])
        self.yrows = len(self._imgAA)

    @property
    def image(self):
        """Copy of the full image"""
        return copy.deepcopy(self._imgAA)

    def move(self, dx, dy, keep_rect = None):
        """Move the image (relative to the viewer)

        Args:
        dx: Change in x-position
        dy: Change in y-position
        keep_rect: cckkRectangle object. If specified, keeps the image fully within the keep_rect area

        Returns:
        cckkImage object
        """
        self.xpos += dx
        self.ypos += dy
        self.keep_within(keep_rect)
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
        str += "  " + super().str() + "\n"
        for row in self._imgAA:
            for pixel in row:
                as_str += str(pixel) + " "
            as_str += "\n"
        return as_str
    