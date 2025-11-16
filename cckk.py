import copy


class cckkRectangle:
    def __init__(self, xcols=0, yrows=0, xpos=0, ypos=0):
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

    def set(self, xcols=0, yrows=0, xpos=0, ypos=0):
        self._xcols = xcols  # No. of columns in the rectangle
        self._yrows = yrows  # No. of rows in the rectangle
        self._xpos = xpos  # X-position of the rectangle
        self._ypos = ypos  # Y-position of the rectangle

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

    def __eq__(self, other): 
        if not isinstance(other, cckkRectangle):
            # Don't attempt to compare against unrelated types
            return NotImplemented

        return self.xpos == other.xpos and self.ypos == other.ypos and self.xcols == other.xcols and self.yrows == other.yrows

    def keep_within(self, outer_rect=None):
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
        return (
            "cckkRectangle: "
            + str(self.xcols)
            + " x "
            + str(self.yrows)
            + " at ("
            + str(self.xpos)
            + ","
            + str(self.ypos)
            + ")\n"
        )

    def overlap(self, other_rect):
        """Calculate the intersection of this rectangle with another rectangle

        Args:
        other_rect: cckkRectangle object representing the other rectangle

        Returns:
        cckkRectangle object representing the intersection rectangle, or None if there is no intersection
        """
        inter_xpos = max(self.xpos, other_rect.xpos)
        inter_ypos = max(self.ypos, other_rect.ypos)
        inter_xend = min(self.xpos + self.xcols, other_rect.xpos + other_rect.xcols)
        inter_yend = min(self.ypos + self.yrows, other_rect.ypos + other_rect.yrows)

        if inter_xend > inter_xpos and inter_yend > inter_ypos:
            return cckkRectangle(
                xcols=inter_xend - inter_xpos,
                yrows=inter_yend - inter_ypos,
                xpos=inter_xpos,
                ypos=inter_ypos,
            )
        else:
            return None

    def calculate_mer(rectangles=[]):
        """Calculate the minimum enclosing rectangle of a list of rectangles"""
        mer = cckkRectangle()
        if len(rectangles) > 0:
            min_xpos = min([rect.xpos for rect in rectangles])
            min_ypos = min([rect.ypos for rect in rectangles])
            max_xpos = max([rect.xpos + rect.xcols for rect in rectangles])
            max_ypos = max([rect.ypos + rect.yrows for rect in rectangles])
            mer.set(
                xcols=max_xpos - min_xpos,
                yrows=max_ypos - min_ypos,
                xpos=min_xpos,
                ypos=min_ypos,
            )
        return mer


class cckkViewer(cckkRectangle):
    ## Class representation of a viewer of images for display on a SenseHat
    # The viewer represents the view area through which an image is seen. This view can be displayed on a SenseHat LED matrix.
    # The viewer can contain multiple images, which are layered on top of each other.
    # The base class cckkRectangle is used to represent the viewer size and position.
    ##############################################################################################

    """Class representation of a viewer of images for display on a SenseHat"""

    def __init__(self, xcols=8, yrows=8, xpos=0, ypos=0, fill=(0, 0, 0), images=[]):
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
        super().__init__(
            xcols=xcols, yrows=yrows, xpos=xpos, ypos=ypos
        )  # Initialize cckkRectangle base class

        self._fill = fill  # Fill colour if the image does not fill the viewer
        self._mer_rect = cckkRectangle()  # Minimum enclosing rectangle of the images
        self._images = (
            []
        )  # List of cckkImage objects that are viewed through the viewer. First image in the list is at the *back*.
        self.add_images(images)

    @property
    def background(self):
        return [self._fill] * (self.xcols * self.yrows)

    def add_images(self, images=[]):
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
        self._mer_rect = cckkRectangle.calculate_mer(self._images)
        return self

    def align(self, img_name="", horiz="C", vert="C"):
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
            self.xpos = img.xpos + int((img.xcols - self.xcols) / 2)

        if vert.upper() == "T":
            self.ypos = img.ypos
        elif vert.upper() == "B":
            self.ypos = img.ypos + img.yrows - self.yrows
        else:
            self.ypos = img.ypos + int((img.yrows - self.yrows) / 2)

        return self

    def view(self):
        """View of the images through the viewer

        Returns:
        cckkImage object representing the view of the images through the viewer
        """
        view_img = cckkImage(imgA=self.background, img_cols=self.xcols)

        for img in self._images:
            for yrow in range(self.yrows):
                for xcol in range(self.xcols):
                    xcol_img = self.xpos + xcol - img.xpos
                    yrow_img = self.ypos + yrow - img.ypos
                    if (
                        xcol_img >= 0
                        and xcol_img < img.xcols
                        and yrow_img >= 0
                        and yrow_img < img.yrows
                    ):
                        img_pixel = img.getPixel(xcol_img, yrow_img)
                        if img_pixel is not None:
                            view_img.setPixel(xcol, yrow, pixel=img_pixel)
        return view_img

    def moveTo(self, xpos, ypos, keep=False):
        """Move the viewer to the specified position

        Args:
        xpos: New x-position
        ypos: New y-position
        keep: If True, keeps the cammera over the MER of the images

        Returns:
        View of the image through the viewer as a one-dimensional array of colour elements, ready to be sent to the SenseHat
        """
        self.xpos = xpos
        self.ypos = ypos

        if keep:
            self.keep_within(self._mer_rect)

        return self.view()

    def move(self, dx, dy, keep=False):
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

    def moveTo_img(self, name, xpos, ypos, keep=False):
        idx = self.find_image(name)
        if idx >= 0:
            self._images[idx].moveTo(xpos, ypos, self._mer_rect if keep else None)
        return self

    def move_img(self, name, dx, dy, keep=False):
        idx = self.find_image(name)
        if idx >= 0:
            self._images[idx].move(dx, dy, self._mer_rect if keep else None)
        return self

    def align_image(self, name, horiz="C", vert="C"):
        idx = self.find_image(name)
        if idx >= 0:
            self._images[idx].align(self, horiz, vert)
        return self

    def overlap(self, img1_name, img2_name):
        """Calculate the intersection of two images in the viewer

        Args:
        img1_name: Name of the first image
        img2_name: Name of the second image

        Returns:
        cckkImage object representing the overlapping image, or None if there is no overlap. Pixels are taken from the first image.
        """
        idx1 = self.find_image(img1_name)
        idx2 = self.find_image(img2_name)
        if idx1 >= 0 and idx2 >= 0:
            return self._images[idx1].overlap(self._images[idx2])
        else:
            return None

    def overlap_count(self, img1_name, img2_name):
        """Count the number of pixels that overlap between two images in the viewer, ignoring transparent pixels

        Args:
        img1_name: Name of the first image
        img2_name: Name of the second image

        Returns:
        Number of pixels that overlap between the two images
        """
        idx1 = self.find_image(img1_name)
        idx2 = self.find_image(img2_name)
        if idx1 >= 0 and idx2 >= 0:
            return self._images[idx1].overlap_count(self._images[idx2])
        else:
            return 0

    def exportAsString(self, colour_dict=None):
        """Export the viewer's current view as a string representation

        Args:
        colour_dict: Dictionary mapping pixel colours to characters.

        Returns:
        String representation of the viewer's current view
        """
        view = self.view()
        return view.exportAsString(colour_dict)

    def str(self):
        as_str = "cckkViewer:\n"
        as_str += "  " + super().str() + "\n"
        as_str += "  Fill: " + str(self._fill) + "\n"
        as_str += "  MER: " + self._mer_rect.str() + "\n"
        as_str += "  Images: " + str(len(self._images)) + "\n"
        return as_str


class cckkImage(cckkRectangle):
    ## Class representation of an image
    # The base class cckkRectangle is used to represent the image size and position.
    ##############################################################################################

    """Class representation of an image"""
    def_colour_dict = {
        ".": None,  # Transparent
        "x": (0, 0, 0),  # Black
        "w": (255, 255, 255),  # White
        "r": (255, 0, 0),  # Red
        "g": (0, 255, 0),  # Green
        "b": (0, 0, 255),  # Blue
        "c": (0, 255, 255),  # Cyan
        "y": (255, 255, 0),  # Yellow
        "m": (255, 0, 255),  # Magenta
        "W": (128, 128, 128),  # Gray
        "R": (128, 0, 0),  # Maroon
        "G": (0, 128, 0),  # Dark Green
        "B": (0, 0, 128),  # Navy
        "C": (0, 128, 128),  # Teal
        "Y": (128, 128, 0),  # Olive
        "M": (128, 0, 128),  # Purple
        "s": (192, 192, 192),  # Silver
        "p": (255, 0, 128),  # Pink
        "o": (255, 128, 0),  # Orange
        "l": (0, 255, 128),  # Lime
        "d": (128, 255, 0),  # Gold
        "t": (0, 128, 255),  # Turquoise
        "v": (128, 0, 255),  # Violet
    }

    reverse_colour_dict = {v: k for k, v in def_colour_dict.items()}

    def rgbAsString(pixel, colour_dict=None):
        """Convert a pixel to its string equivalent

        Args:
        pixel: Pixel value as a list containing [R, G, B] (red, green, blue)
        colour_dict: Dictionary mapping pixel colours to characters. If None, uses the default colour dictionary.

        Returns:
        Pixel value as a character
        """
        if colour_dict is None:
            colour_dict = cckkImage.reverse_colour_dict

        if pixel in colour_dict:
            return colour_dict[pixel]
        else:
            return "?"  # Unknown colour

    def __init__(self, imgA=None, imgAA=None, imgStr=None, imgFile=None, img_cols=8, name=""):
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
        self._name = name  # Name of the image

        if imgA is not None:
            self.createFromArray(imgA, img_cols)
        elif imgAA is not None:
            self._imgAA = imgAA
            self.update_size()
        elif imgStr is not None:
            self.createFromString(imgStr, None)
        elif imgFile is not None:
            self.createFromImageFile(imgFile)

    def createFromArray(self, imgA, img_cols=8):
        self._imgAA = [imgA[i : i + img_cols] for i in range(0, len(imgA), img_cols)]
        self.update_size()
        return self

    def createFromString(self, imgStr, colour_dict=None):
        if colour_dict is None:
            colour_dict = cckkImage.def_colour_dict

        self._imgAA = []
        img_lines = imgStr.splitlines()

        # Remove leading/trailing blank lines
        if img_lines[0].strip() == "":
            img_lines = img_lines[1:]
        if img_lines[-1].strip() == "":
            img_lines = img_lines[:-1]

        for img_line in img_lines:
            line_pixels = []
            for ch in img_line.strip():
                if ch in colour_dict:
                    line_pixels.append(colour_dict[ch])
                else:
                    raise Exception(
                        "Invalid colour character '" + ch + "' in image string"
                    )
            self._imgAA.append(line_pixels)

        self.update_size()
        return self

    def createFromImageFile(self, img_filename):
        """Set the image from an image file

        Args:
        img_filename: Path to the image file

        Returns:
        cckkImage object

        Raises:
        Exception: If unable to read the image file
        """
        try:
            from PIL import Image
        except ImportError:
            raise Exception(
                "PIL module not found. Please install Pillow to use this feature."
            )

        img = Image.open(img_filename)
        img = img.convert("RGBA")  # Ensure image is in RGB format
        imgA = list(img.getdata())
        img_cols, img_rows = img.size
        for i in range(len(imgA)):
            r, g, b, a = imgA[i]
            if a == 0:
                imgA[i] = None
            else:
                imgA[i] = (r, g, b)
        self.createFromArray(imgA, img_cols)
        return self

    def createFromPixel(self, xcols, yrows, pixel = None):
        """Create an image of the specified size and pixel colour

        Args:
        pixel: Pixel value as a list containing [R, G, B] (red, green, blue)
        xcols: Number of columns in the image
        yrows: Number of rows in the image

        Returns:
        cckkImage object
        """
        self._imgAA = [[pixel for _ in range(xcols)] for _ in range(yrows)]
        self.update_size()
        return self

    def exportAsString(self, colour_dict=None):
        """Export the image as a string representation

        Args:
        colour_dict: Dictionary mapping pixel colours to characters. If None, uses the default colour dictionary.

        Returns:
        String representation of the image
        """
        if colour_dict is None:
            colour_dict = cckkImage.reverse_colour_dict

        img_str = ""
        for row in self._imgAA:
            for pixel in row:
                img_str += cckkImage.rgbAsString(pixel)
            img_str += "\n"
        return img_str.strip()

    def align(self, viewer_rect, horiz="C", vert="C"):
        if horiz.upper() == "L":
            self.xpos = viewer_rect.xpos
        elif horiz.upper() == "R":
            self.xpos = viewer_rect.xpos + viewer_rect.xcols - self.xcols
        else:
            self.xpos = viewer_rect.xpos + int((viewer_rect.xcols - self.xcols) / 2)

        if vert.upper() == "T":
            self.ypos = viewer_rect.ypos
        elif vert.upper() == "B":
            self.ypos = viewer_rect.ypos + viewer_rect.yrows - self.yrows
        else:
            self.ypos = viewer_rect.ypos + int((viewer_rect.yrows - self.yrows) / 2)

        return self

    def update_size(self):
        """Update the image size"""
        self.xcols = len(self._imgAA[0])
        self.yrows = len(self._imgAA)

    @property
    def image(self):
        """Copy of the full image"""
        return copy.deepcopy(self._imgAA)

    def getPixel(self, x, y):
        """Get the pixel at the specified position

        Args:
        x: X-position of the pixel
        y: Y-position of the pixel

        Returns:
        Pixel value as a list containing [R, G, B] (red, green, blue)
        """
        return self._imgAA[self.yrows-y-1][x] # Access from bottom-left (0,0)

    def setPixel(self, x, y, pixel = None):
        """Set the pixel at the specified position

        Args:
        x: X-position of the pixel
        y: Y-position of the pixel
        pixel: Pixel value as a list containing [R, G, B] (red, green, blue)

        Returns:
        cckkImage object
        """
        self._imgAA[self.yrows-y-1][x] = pixel  # Access from bottom-left (0,0)
        return self

    def pixelAsString(self, x, y, colour_dict=None):
        """Get the pixel at the specified position as a string character

        Args:
        x: X-position of the pixel
        y: Y-position of the pixel
        colour_dict: Dictionary mapping pixel colours to characters. If None, uses the default colour dictionary.

        Returns:
        Pixel value as a character
        """
        return cckkImage.rgbAsString(self.getPixel(x, y), colour_dict)
        
    def getSubImage(self, sub_rect):
        """Get a sub-image from the image

        Args:
        sub_rect: cckkRectangle object representing the sub-image area

        Returns:
        cckkImage object representing the sub-image
        """
        sub_imgAA = []
        for yrow in reversed(range(sub_rect.yrows)):
            row_pixels = []
            for xcol in range(sub_rect.xcols):
                x_img = sub_rect.xpos + xcol - self.xpos
                y_img = sub_rect.ypos + yrow - self.ypos
                if 0 <= x_img < self.xcols and 0 <= y_img < self.yrows:
                    row_pixels.append(self.getPixel(x_img, y_img))
                else:
                    row_pixels.append(None)  # Transparent pixel if out of bounds
            sub_imgAA.append(row_pixels)
        sub_img = cckkImage(imgAA=sub_imgAA)
        sub_img.xpos = sub_rect.xpos
        sub_img.ypos = sub_rect.ypos
        return sub_img

    def moveTo(self, xpos, ypos, keep_rect=None):
        """Move the image to the specified position

        Args:
        xpos: New x-position
        ypos: New y-position
        keep_rect: cckkRectangle object. If specified, keeps the image fully within the keep_rect area

        Returns:
        cckkImage object
        """
        self.xpos = xpos
        self.ypos = ypos
        self.keep_within(keep_rect)
        return self
    
    def move(self, dx, dy, keep_rect=None):
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

    def overlap(self, other_img, top_only=False):
        """Calculate the intersection of this image with another image

        Args:
        other_img: cckkImage object representing the other image
        top_only: If True, only consider pixels from this image (ignore pixels from other image)

        Returns:
        cckkImage object representing the intersection image, or None if there is no intersection
        """
        inter_rect = super().overlap(other_img)
        if inter_rect is not None:
            inter_imgAA = []
            for yrow in reversed(range(inter_rect.yrows)):
                row_pixels = []
                for xcol in range(inter_rect.xcols):
                    x_self = inter_rect.xpos + xcol - self.xpos
                    y_self = inter_rect.ypos + yrow - self.ypos
                    x_other = inter_rect.xpos + xcol - other_img.xpos
                    y_other = inter_rect.ypos + yrow - other_img.ypos
                    if (
                        0 <= x_self < self.xcols
                        and 0 <= y_self < self.yrows
                        and 0 <= x_other < other_img.xcols
                        and 0 <= y_other < other_img.yrows
                    ):
                        pixel_self = self.getPixel(x_self, y_self)
                        if top_only:
                            row_pixels.append(pixel_self)  # Take the pixel from this image
                        else:
                            pixel_other = other_img.getPixel(x_other, y_other)
                            if pixel_self is not None:
                                row_pixels.append(pixel_self)  # Take the pixel from this image
                            else:
                                row_pixels.append(pixel_other)  # Take the pixel from the other image
                    else:
                        raise Exception("Pixel incorrectly out of bounds during intersection calculation")
                inter_imgAA.append(row_pixels)
            inter_img = cckkImage(imgAA=inter_imgAA)
            inter_img.xpos = inter_rect.xpos
            inter_img.ypos = inter_rect.ypos
            return inter_img
        else:
            return None

    def overlap_count(self, other_img):
        """Count the number of pixels that overlap with another image, ignoring transparent pixels

        Args:
        other_img: cckkImage object representing the other image

        Returns:
        Number of pixels that overlap between the two images
        """
        pixel_count = 0
        inter_rect = super().overlap(other_img)
        if inter_rect is not None:
            for yrow in reversed(range(inter_rect.yrows)):
                for xcol in range(inter_rect.xcols):
                    x_self = inter_rect.xpos + xcol - self.xpos
                    y_self = inter_rect.ypos + yrow - self.ypos
                    x_other = inter_rect.xpos + xcol - other_img.xpos
                    y_other = inter_rect.ypos + yrow - other_img.ypos
                    if (
                        0 <= x_self < self.xcols
                        and 0 <= y_self < self.yrows
                        and 0 <= x_other < other_img.xcols
                        and 0 <= y_other < other_img.yrows
                    ):
                        pixel_self = self.getPixel(x_self, y_self)
                        pixel_other = other_img.getPixel(x_other, y_other)
                        if pixel_self is not None and pixel_other is not None:
                            pixel_count += 1
        return pixel_count

    def str(self):
        as_str = "cckkImage:\n"
        as_str += "  " + super().str() + "\n"
        for row in self._imgAA:
            for pixel in row:
                as_str += str(pixel) + " "
            as_str += "\n"
        return as_str
