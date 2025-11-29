### To Do
# - Move keep into cckkCondition for move_ing(), etc ... implement keep_within and rotate_within
# - Add cckkCondition to cckkViewer.move() and .moveTo()
# - Add method to display a message on the grid

import copy
import time


class cckkRectangle:
    def __init__(self, xcols: int = 0, yrows: int = 0, xpos: int = 0, ypos: int = 0):
        """Contructs a cckkRectangle object.

        Args:# - Make Senset
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

    def set(self, xcols: int = 0, yrows: int = 0, xpos: int = 0, ypos: int = 0) -> "cckkRectangle":
        self._xcols = xcols  # No. of columns in the rectangle
        self._yrows = yrows  # No. of rows in the rectangle
        self._xpos = xpos  # X-position of the rectangle
        self._ypos = ypos  # Y-position of the rectangle
        return self

    @property
    def xcols(self) -> int:
        """No. of columns in the rectangle"""
        return self._xcols

    @xcols.setter
    def xcols(self, value: int):
        self._xcols = value

    @property
    def yrows(self) -> int:
        """No. of rows in the rectangle"""
        return self._yrows

    @yrows.setter
    def yrows(self, value: int):
        self._yrows = value

    @property
    def xpos(self) -> int:
        return self._xpos

    @xpos.setter
    def xpos(self, value):
        self._xpos = value

    @property
    def ypos(self) -> int:
        return self._ypos

    @ypos.setter
    def ypos(self, value):
        self._ypos = value

    @property
    def pos(self) -> tuple[int,int]:
        return (self.xpos, self.ypos)

    @pos.setter
    def pos(self, value: tuple[int, int]):
        self.xpos = value[0]
        self.ypos = value[1]

    def __eq__(self, other : object):
        if not isinstance(other, cckkRectangle):
            # Don't attempt to compare against unrelated types
            return NotImplemented

        return self.xpos == other.xpos and self.ypos == other.ypos and self.xcols == other.xcols and self.yrows == other.yrows

    def moveTo(self, xpos, ypos = None, keep_rect=None):
        """Move the image to the specified position

        Args:
        xpos: New x-position. if a tuple with the format (x,y), use this as the position
        ypos: New y-position
        keep_rect: cckkRectangle object. If specified, keeps the image fully within the keep_rect area

        Returns:
        cckkImage object
        """
        if isinstance(xpos, tuple) and len(xpos) == 2:
            xpos, ypos = xpos

        if xpos is not None:
            self.xpos = xpos
        if ypos is not None:
            self.ypos = ypos

        self.keep_within(keep_rect)
        return self

    def move(self, dx, dy=None, keep_rect=None):
        """Move the image (relative to the viewer)

        Args:
        dx: Change in x-position. if a tuple with the format (ddx,dy), use this as the position delta
        dy: Change in y-position
        keep_rect: cckkRectangle object. If specified, keeps the image fully within the keep_rect area

        Returns:
        cckkImage object
        """
        if isinstance(dx, tuple) and len(dx) == 2:
            dx, dy = dx

        if dx is not None:
            self.xpos += dx
        if dy is not None:
            self.ypos += dy
        self.keep_within(keep_rect)
        return self

    def align(self, align_rect: "cckkRectangle", horiz: str = "C", vert: str = "C", keep_rect: "cckkRectangle" = None):
        """Align the rectangle relative to another rectangle
        
        Args:
        align_rect: cckkRectangle object representing the rectangle to align to
        horiz: Rectangle horizontal alignment relative to selected rectangle.  Contains "L", "C" or "R" (left, centre, right)
        vert: Rectangle vertical alignment relative to selected rectangle. Contains "T", "C" or "B" (top, centre, bottom)
        keep_rect: cckkRectangle object representing the rectangle to keep this rectangle within

        Returns:
        cckkRectangle object
        """
        if horiz.upper() == "L":
            self.xpos = align_rect.xpos
        elif horiz.upper() == "R":
            self.xpos = align_rect.xpos + align_rect.xcols - self.xcols
        elif horiz.upper() == "C":
            self.xpos = align_rect.xpos + \
                int((align_rect.xcols - self.xcols) / 2)

        if vert.upper() == "T":
            self.ypos = align_rect.ypos
        elif vert.upper() == "B":
            self.ypos = align_rect.ypos + align_rect.yrows - self.yrows
        elif vert.upper() == "C":
            self.ypos = align_rect.ypos + \
                int((align_rect.yrows - self.yrows) / 2)

        if keep_rect is not None:
            self.keep_within(keep_rect)

        return self

    def keep_within(self, outer_rect=None) -> "cckkRectangle":
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

    def str(self) -> str:
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

    def overlap(self, other_rect) -> "cckkRectangle":
        """Calculate the intersection of this rectangle with another rectangle

        Args:
        other_rect: cckkRectangle object representing the other rectangle

        Returns:
        cckkRectangle object representing the intersection rectangle, or None if there is no intersection
        """
        inter_xpos = max(self.xpos, other_rect.xpos)
        inter_ypos = max(self.ypos, other_rect.ypos)
        inter_xend = min(self.xpos + self.xcols,
                         other_rect.xpos + other_rect.xcols)
        inter_yend = min(self.ypos + self.yrows,
                         other_rect.ypos + other_rect.yrows)

        if inter_xend > inter_xpos and inter_yend > inter_ypos:
            return cckkRectangle(
                xcols=inter_xend - inter_xpos,
                yrows=inter_yend - inter_ypos,
                xpos=inter_xpos,
                ypos=inter_ypos,
            )
        else:
            return None

    def calculate_mer(rectangles=[]) -> "cckkRectangle":
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

class cckkLayer:
    # Class representation of an image layer
    def __init__(self, img_id: int, img_name: str, visible: bool = True):
        self._img_id = img_id
        self._img_name = img_name
        self.visible = visible
    
    @property
    def id(self) -> int:
        return self._img_id
    
    @property
    def name(self) -> str:
        return self._img_name
        
    def show(self) -> "cckkLayer":
        self.visible = True
        return self
        
    def hide(self) -> "cckkLayer":
        self.visible = False
        return self

class cckkAction:
    _nextID = 1

    # Class representation of a viewer action
    def __init__(self, action: str, target: str = None, context: dict = None):
        self._id = cckkAction._nextID
        self._action = action
        self._target = target
        self._context = context
        cckkAction._nextID += 1
    
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def action(self) -> str:
        return self._action
        
    @property
    def target(self) -> str:
        return self._target

    @property
    def context(self) -> dict:
        return self._context


class cckkCondition:
    # Class representation of condition impacting an action
    def __init__(
        self,
        unless_overlap: list[str] = None,
        only_if_overlap: list[str] = None,
        keep_within: cckkRectangle = None,
        rotate_within: cckkRectangle = None,
    ):
        self._unless_overlap = unless_overlap
        self._only_if_overlap = only_if_overlap
        self._keep_within = keep_within
        self._rotate_within = rotate_within

    @property
    def unless_overlap(self) -> list[str]:
        return self._unless_overlap

    @property
    def only_if_overlap(self) -> list[str]:
        return self._only_if_overlap

    @property
    def keep_within(self) -> cckkRectangle:
        return self._keep_within

    @property
    def rotate_within(self) -> cckkRectangle:
        return self._rotate_within


class cckkViewer(cckkRectangle):
    # Class representation of a viewer of images for display on a SenseHat
    # The viewer represents the view area through which an image is seen. This view can be displayed on a SenseHat LED matrix.
    # The viewer can contain multiple images, which are layered on top of each other.
    # The base class cckkRectangle is used to represent the viewer size and position.
    ##############################################################################################

    """Class representation of a viewer of images for display on a SenseHat"""

    def __init__(self, xcols=8, yrows=8, xpos=0, ypos=0, fill=(0, 0, 0), images=[], horiz=None, vert=None):
        """Contructs a cckkViewer object.
        The viewer represents the view area through which an image is seen. This view can be displayed on a SenseHat LED matrix.

        Args:
        xcols: Number of columns in the viewer
        yrows: Number of rows in the viewer
        xpos: X-position of the viewer
        ypos: Y-position of the viewer
        fill: Fill colour if the image does not fill the viewer
        images: List of cckkImage objects that are viewed through the viewer, First image in the list is at the *back*.

        Returns:
        cckkViewer object

        Raises:
        Exception: Never
        """
        super().__init__(xcols=xcols, yrows=yrows, xpos=xpos, ypos=ypos)  # Initialize cckkRectangle base class

        self._fill = fill  # Fill colour if the image does not fill the viewer
        self._mer_rect = cckkRectangle()  # Minimum enclosing rectangle of the images
        self._images = {} # Dictionary of cckkImage objects that are viewed through the viewer. The object keys are the object id().
        self._layers = [] # Stack of cckkLayer objects representing image layers in the viewer. First layer in the list is at the *top*.
        self._actions = [] # Stack of cckkAction objects representing actions carried out in the viewer

        self.add_images(images)

        if horiz is not None or vert is not None:
            self.align_images(horiz, vert)

    @property
    def background(self):
        return [self._fill] * (self.xcols * self.yrows)

    def _add_action(self, action: str, target: str = None, context = None):
        self._actions.append(cckkAction(action:=action, target=target, context=context))

    @property
    def lastAction(self):
        if len(self._actions) > 0:
            return self._actions[-1].id
        else:
            return 0

    def add_images(self, images=[]):
        """Add images to the viewer

        Args:
        images: List of cckkImage objects to view through the viewer. These are added on top of any existing images. First image is topmost.

        Raises:
        Exception: If invalid image specified
        """
        for img in reversed(images):
            if not isinstance(img, cckkImage):
                raise Exception("Invalid image specified")
            _id = id(img)
            self._images[_id] = img
            self._layers.insert(0, cckkLayer(img_id=_id, img_name=img.name, visible=True)) # Add new layers at the front
        self._mer_rect = cckkRectangle.calculate_mer(self._images.values())
        return self

    def align_to_img(self, img_name: str = "", horiz: str = "C", vert: str = "C", keep_img_name: str = None):
        """Align the viewer relative to an image
        Args:
        img_name: Name of the image in the viewer's image list to align the viewer to. Default: 0 (top image)
        horiz: Viewer horizontal alignment relative to selected image.  Contains "L", "C" or "R" (left, centre, right)
        vert: Viewer vertical alignment relative to selected image. Contains "T", "C" or "B" (top, centre, bottom)
        keep_img_name: Name of the image representing the rectangle to keep the viewer within

        Returns:
        cckkViewer object

        Raises:
        Exception: If no images in viewer or invalid image index specified
        """
        self.align(
            self.find_image(img_name, 0), horiz, vert, self.find_image(keep_img_name)
        )

        return self

    def view(self):
        """View of the images through the viewer

        Returns:
        cckkImage object representing the view of the images through the viewer
        """
        view_img = cckkImage(imgA=self.background, img_cols=self.xcols)

        for layer in reversed(self._layers): # Start with the bottom layer and paint each one on top
            if layer.visible:
                img = self._images[layer.id]
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

    @property
    def pixels(self):
        """View of the image through the viewer as a one-dimensional array of colour elements, ready to be sent to the SenseHat"""
        return self.view().pixels

    def moveTo(self, xpos, ypos=None, keep=False):
        """Move the viewer to the specified position

        Args:
        xpos: New x-position
        ypos: New y-position
        keep: If True, keeps the cammera over the MER of the images

        Returns: self
        """
        self._add_action(action="MoveViewer", target="self", context={ "before": (self.xpos, self.ypos) })
        return super().moveTo(xpos, ypos, self._mer_rect if keep else None)

    def move(self, dx, dy=None, keep=False):
        """Move the viewer

        Args:
        dx: Change in x-position
        dy: Change in y-position
        keep: If True, keeps the cammera over the MER of the images

        Returns: self
        """
        self._add_action( action="MoveViewer", target="self", context={"before": (self.xpos, self.ypos)})
        super().move(dx, dy, self._mer_rect if keep else None)


    def _find_layer(self, name):
        """Find a image layer in the viewer by name

        Args:
        name: Name of the image layer to find

        Returns:
        cckkLayer representing the layer, or None if not found
        """
        for layer in self._layers:
            if layer.name == name:
                return layer
        return None

    def _find_image_id(self, name: str, id_if_not_found: int = -1) -> str:
        """Find an image in the viewer by name

        Args:
        name: Name of the image to find
        id_if_not_found: ID to return if name is not found

        Returns:
        ID of the image in the viewer's image list, or -1 if not found
        """
        layer = self._find_layer(name)
        if layer is None:
            return id_if_not_found
        else:
            return layer.id

    def find_image(self, name: str, id_if_not_found: int = -1) -> "cckkImage":
        """Find an image in the viewer by name

        Args:
        name: Name of the image to find
        id_if_not_found: ID of the image to return if name is not found

        Returns:
        cckkImage object in the viewer's image list, or None if not found
        """
        idx = self._find_image_id(name, id_if_not_found)
        if idx >= 0:
            return self._images[idx]
        else:
            return None

    def find_images(self, name_list):
        img_list = []
        if name_list is not None:
            for name in name_list:         
                img = self.find_image(name)
                if img is not None:
                    img_list.append(img)
        return img_list

    def _find_below(self, name):
        name_list = []
        found = False
        for layer in self._layers:
            if layer.name == name:
                found = True
            elif found == True:
                name_list.append(layer.name)

        return name_list

    def hide_image(self, name):
        layer = self._find_layer(name)
        if layer is not None:
            layer.hide()
        return self

    def show_image(self, name):
        layer = self._find_layer(name)
        if layer is not None:
            layer.show()
        return self

    def moveTo_img(self, name, xpos, ypos=None, keep=False):
        img = self.find_image(name)
        if img is not None:
            self._add_action(action="MoveImage", target=name
                             ,context={ "before": (img.xpos, img.ypos) })
            img.moveTo(xpos, ypos, self._mer_rect if keep else None)
        return self

    def move_img(self, name: str, dx: int | tuple[int, int], dy: int = None, keep: bool = False, condition: cckkCondition = None):
        img = self.find_image(name)
        if img is not None:
            self._add_action(action="MoveImage", target=name
                             ,context={ "before": (img.xpos, img.ypos) })
            img.move(dx, dy, self._mer_rect if keep else None)

            if condition is not None:
                if condition.unless_overlap is not None and len(condition.unless_overlap) > 0:
                    if self.overlap_multi_count(name, condition.unless_overlap) > 0:
                        self.undo()

                if condition.only_if_overlap is not None and len(condition.only_if_overlap) > 0:
                    if self.overlap_multi_count(name, condition.only_if_overlap) == 0:
                        self.undo()

        return self

    def align_image(self, name, horiz="C", vert="C"):
        img = self.find_image(name)
        if img is not None:
            img.align(self, horiz, vert)
        return self

    def align_images(self, horiz="C", vert="C"):
        for img in self._images:
            img.align(self, horiz, vert)
        return self

    def overlap(self, img1_name, img2_name):
        """Calculate the intersection of two images in the viewer

        Args:
        img1_name: Name of the first image
        img2_name: Name of the second image

        Returns:
        cckkImage object representing the overlapping image, or None if there is no overlap. Pixels are taken from the first image.
        """
        img1 = self.find_image(img1_name)
        img2 = self.find_image(img2_name)
        if img1 is not None and img2 is not None:
            return img1.overlap(img2)
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
        img1 = self.find_image(img1_name)
        img2 = self.find_image(img2_name)
        if img1 is not None and img2 is not None:
            return img1.overlap_count(img2)
        else:
            return 0

    def overlap_string(self, img1_name, img2_name):
        """Get a string representation of the overlapping area between two images in the viewer

        Args:
        img1_name: Name of the first image
        img2_name: Name of the second image

        Returns:
        String representation of the overlapping area
        """
        img1 = self.find_image(img1_name)
        img2 = self.find_image(img2_name)
        if img1 is not None and img2 is not None:
            return img1.overlap_string(img2)
        else:
            return ""

    def overlap_multi(self, name, other_names = None):
        """Calculate the overlap of one image with a stack of other images

        Args:
        name: Name of a cckkImage object name
        other_names: Stack (list) of cckkImage object name

        Returns:
        cckkImage object representing the intersection image, or None if there is no intersection
        """
        img = self.find_image(name)
        if img is None:
            return None

        if other_names is None:
            other_names = self._find_below(name)
        other_imgs = self.find_images(other_names)
        return img.overlap_multi(other_imgs)

    def overlap_multi_count(self, name, other_names = None):
        """Count the number of pixels that overlap with a stack of other images, ignoring transparent pixels

        Args:
        name: Name of a cckkImage object name
        other_names: Stack (list) of cckkImage object name

        Returns:
        Number of pixels in this image that overlap with any pixel in the other images
        """
        img = self.find_image(name)
        if img is None:
            return None

        if other_names is None:
            other_names = self._find_below(name)
        other_imgs = self.find_images(other_names)
        return img.overlap_multi_count(other_imgs)

    def overlap_with(self, name, other_names = None):
        """For an image, find the name of the first image in a stack of other images that intersects

        Args:
        name: Name of a cckkImage object name
        other_names: Stack (list) of cckkImage object name

        Returns:
        Name of the first image in a stack of other images that intersects
        """
        img = self.find_image(name)
        if img is None:
            return None

        if other_names is None:
            other_names = self._find_below(name)
        other_imgs = self.find_images(other_names)

        found = None
        for i, other_img in enumerate(other_imgs):
            if found is None and img.overlap_count(other_img) > 0:
                found = other_names[i]

        return found

    def undo(self):
        action = self._actions.pop() 

        match action.action:
            case "MoveViewer":
                self.moveTo(action.context["before"])
            case "MoveImage":
                self.moveTo_img(name=action.target, xpos=action.context["before"], ypos=None)
            case _:
                # Unknown action
                pass

        return self

    def exportAsString(self):
        """Export the viewer's current view as a string representation

        Returns:
        String representation of the viewer's current view
        """
        view = self.view()
        return view.exportAsString()

    def str(self):
        as_str = "cckkViewer:\n"
        as_str += "  " + super().str() + "\n"
        as_str += "  Fill: " + str(self._fill) + "\n"
        as_str += "  MER: " + self._mer_rect.str() + "\n"
        as_str += "  Images: " + str(len(self._images)) + "\n"
        return as_str

class cckkColourDict:
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

    def __init__(
        self,
        colour_dict: dict[str, tuple[int, int, int]] = None,
        update_dict: dict[str, tuple[int, int, int]] = None,
    ):
        self._colour_dict = (colour_dict if colour_dict is not None else cckkColourDict.def_colour_dict.copy())
        if update_dict is not None:
            self._colour_dict.update(update_dict)

        self._reverse_colour_dict = {v: k for k, v in self._colour_dict.items()}

    @property
    def dict(self) -> dict[str, tuple[int, int, int]]:
        return self._colour_dict

    @property
    def reverse_dict(self) -> dict:
        return self._reverse_colour_dict

    def get(self, colour_string: str) -> tuple:
        """Convert a string to its pixel (RGB) equivalent

        Args:
        colour_string Pixel value as a character

        Returns:
        Pixel value as a list containing [R, G, B] (red, green, blue)
        """
        return self.dict.get(colour_string, None)

    def getRGB(self, pixel: tuple[int, int, int]) -> str:
        """Convert a pixel to its string equivalent

        Args:
        pixel: Pixel value as a list containing [R, G, B] (red, green, blue)

        Returns:
        Pixel value as a character
        """
        return self.reverse_dict.get(pixel, "?")


class cckkImage(cckkRectangle):
    # Class representation of an image
    # The base class cckkRectangle is used to represent the image size and position.
    ##############################################################################################

    """Class representation of an image"""
    def __init__(
        self,
        imgA: list[tuple[int, int, int]] = None,
        imgAA: list[list[tuple[int, int, int]]] = None,
        imgStr: str = None,
        imgFile: str = None,
        img_cols: int = 8,
        pos: tuple[int, int] = None,
        name: str = "",
        colour_dict: cckkColourDict = None,
    ):
        """Contructs a cckkImage object

        Args:
        imgA: One-dimensional array of image pixels. Each pixel is a list containing [R, G, B] (red, green, blue). Each R-G-B element must be an integer between 0 and 255.
        imgAA: Two-dimensional array of image pixels
        imgStr: Image as a string, mapped using the colour dictionary
        imgFile: Filename containing the image
        img_cols: Number of columns in the image
        pos: Tuple containing the position of the image (x,y)
        name: Name of the image
        colour_dict: Dictionary to map the image to/from strings

        Returns:
        cckkImage object

        Raises:
        Exception: If invalid image specified
        """
        super().__init__()  # Initialize cckkRectangle base class
        self._imgAA = None  # Two-dimensional array of image pixels
        self._name = name   # Name of the image
        self._colour_dict = colour_dict  # Colour dictionary

        if imgA is not None:
            self.createFromArray(imgA, img_cols)
        elif imgAA is not None:
            self._imgAA = imgAA
            self.update_size()
        elif imgStr is not None:
            self.createFromString(imgStr)
        elif imgFile is not None:
            self.createFromImageFile(imgFile)

        if pos is not None and len(pos) == 2:
            self.pos = pos

    @property
    def colour_dict(self):
        if self._colour_dict is None:
            self._colour_dict = cckkColourDict()

        return self._colour_dict

    def createFromArray(self, imgA, img_cols=8):
        self._imgAA = [imgA[i: i + img_cols]
                       for i in range(0, len(imgA), img_cols)]
        self.update_size()
        return self

    def createFromString(self, imgStr):
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
                if ch in self.colour_dict.dict:
                    line_pixels.append(self.colour_dict.get(ch))
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

    def createFromPixel(self, xcols, yrows, pixel=None):
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

    def exportAsString(self):
        """Export the image as a string representation

        Args:
        colour_dict: Dictionary mapping pixel colours to characters. If None, uses the default colour dictionary.

        Returns:
        String representation of the image
        """
        img_str = ""
        for row in self._imgAA:
            for pixel in row:
                img_str += self.colour_dict.getRGB(pixel)
            img_str += "\n"
        return img_str.strip()

    def update_size(self):
        """Update the image size"""
        self.xcols = len(self._imgAA[0])
        self.yrows = len(self._imgAA)

    @property
    def name(self):
        return self._name

    @property
    def image(self):
        """Copy of the full image"""
        return copy.deepcopy(self._imgAA)

    @property
    def pixels(self):
        """One-dimensional array of image pixels"""
        imgA = []
        for row in self._imgAA:
            for pixel in row:
                imgA.append(pixel)
        return imgA

    def getPixel(self, x, y):
        """Get the pixel at the specified position

        Args:
        x: X-position of the pixel
        y: Y-position of the pixel

        Returns:
        Pixel value as a list containing [R, G, B] (red, green, blue)
        """
        return self._imgAA[self.yrows-y-1][x]  # Access from bottom-left (0,0)

    def setPixel(self, x, y, pixel=None):
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
        return self.colour_dict.getRGB(self.getPixel(x, y))

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
                    # Transparent pixel if out of bounds
                    row_pixels.append(None)
            sub_imgAA.append(row_pixels)
        sub_img = cckkImage(imgAA=sub_imgAA)
        sub_img.xpos = sub_rect.xpos
        sub_img.ypos = sub_rect.ypos
        return sub_img

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
                            # Take the pixel from this image
                            row_pixels.append(pixel_self)
                        else:
                            pixel_other = other_img.getPixel(x_other, y_other)
                            if pixel_self is not None:
                                # Take the pixel from this image
                                row_pixels.append(pixel_self)
                            else:
                                # Take the pixel from the other image
                                row_pixels.append(pixel_other)
                    else:
                        raise Exception(
                            "Pixel incorrectly out of bounds during intersection calculation")
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
        overlap_rect = super().overlap(other_img)
        if overlap_rect is not None:
            for yrow in reversed(range(overlap_rect.yrows)):
                for xcol in range(overlap_rect.xcols):
                    x_self = overlap_rect.xpos + xcol - self.xpos
                    y_self = overlap_rect.ypos + yrow - self.ypos
                    x_other = overlap_rect.xpos + xcol - other_img.xpos
                    y_other = overlap_rect.ypos + yrow - other_img.ypos
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

    def overlap_string(self, other_img):
        """Get a string representation of the overlapping area with another image

        Args:
        other_img: cckkImage object representing the other image

        Returns:
        String representation of the overlapping area
        """
        img = self.overlap(other_img)
        if img is None:
            return ""
        else:
            return img.exportAsString()

    def overlap_multi(self, other_imgs):
        """Calculate the intersection of this image with a stack of other images

        Args:
        other_imgs: Stack (list) of cckkImage objects

        Returns:
        cckkImage object representing the intersection image, or None if there is no intersection
        """
        other_mer = cckkRectangle.calculate_mer(other_imgs)
        overlap_rect = super().overlap(other_mer)
        if overlap_rect is not None:
            inter_imgAA = []
            for yrow in reversed(range(overlap_rect.yrows)):
                row_pixels = []
                for xcol in range(overlap_rect.xcols):
                    overlap_found = False
                    for other_img in other_imgs:
                        x_self = overlap_rect.xpos + xcol - self.xpos
                        y_self = overlap_rect.ypos + yrow - self.ypos
                        x_other = overlap_rect.xpos + xcol - other_img.xpos
                        y_other = overlap_rect.ypos + yrow - other_img.ypos
                        if (
                            0 <= x_self < self.xcols
                            and 0 <= y_self < self.yrows
                            and 0 <= x_other < other_img.xcols
                            and 0 <= y_other < other_img.yrows
                            and not overlap_found
                        ):
                            pixel_self = self.getPixel(x_self, y_self)
                            pixel_other = other_img.getPixel(x_other, y_other)
                            if pixel_self is not None:
                                # Take the pixel from this image
                                row_pixels.append(pixel_self)
                                overlap_found = True
                            elif pixel_other is not None:
                                # Take the pixel from the other image
                                row_pixels.append(pixel_other)
                                overlap_found = True
                        else:
                            pass # Multiple images so some may have no overlap

                    if not overlap_found:
                        row_pixels.append(None)

                inter_imgAA.append(row_pixels)

            inter_img = cckkImage(imgAA=inter_imgAA)
            inter_img.xpos = overlap_rect.xpos
            inter_img.ypos = overlap_rect.ypos
            return inter_img
        else:
            return None

    def overlap_multi_count(self, other_imgs):
        """Count the number of pixels that overlap with a stack of other images, ignoring transparent pixels

        Args:
        other_imgs: Stack (list) of cckkImage objects

        Returns:
        Number of pixels in this image that overlap with any pixel in the other images
        """
        pixel_count = 0
        other_mer = cckkRectangle.calculate_mer(other_imgs)
        overlap_rect = super().overlap(other_mer)
        if overlap_rect is not None:
            inter_imgAA = []
            for yrow in reversed(range(overlap_rect.yrows)):
                for xcol in range(overlap_rect.xcols):
                    overlap_found = False
                    for other_img in other_imgs:
                        x_self = overlap_rect.xpos + xcol - self.xpos
                        y_self = overlap_rect.ypos + yrow - self.ypos
                        x_other = overlap_rect.xpos + xcol - other_img.xpos
                        y_other = overlap_rect.ypos + yrow - other_img.ypos
                        if (
                            0 <= x_self < self.xcols
                            and 0 <= y_self < self.yrows
                            and 0 <= x_other < other_img.xcols
                            and 0 <= y_other < other_img.yrows
                            and not overlap_found
                        ):
                            pixel_self = self.getPixel(x_self, y_self)
                            pixel_other = other_img.getPixel(x_other, y_other)

                            if pixel_self is not None and pixel_other is not None:
                                overlap_found = True
                        else:
                            pass # Multiple images so some may have no overlap

                    if overlap_found:
                        pixel_count += 1

        return pixel_count

    def str(self):
        as_str = "cckkImage:\n"
        as_str = "  Name: \"" + self.name + "\"\n"
        as_str += "  " + super().str() + "\n"
        for row in self._imgAA:
            for pixel in row:
                as_str += str(pixel) + " "
            as_str += "\n"
        return as_str


class cckkSenseHat(cckkViewer):
    """Class wrapper for SenseHat class"""

    def __init__(self, images=[]):
        """Contructs a cckkSenseHat object"""
        super().__init__(xcols=8, yrows=8, xpos=0, ypos=0, fill=(0, 0, 0), images=images, horiz=None, vert=None)
        self._sense = None

    @property
    def sense(self):
        """SenseHat object"""
        return self._sense

    @sense.setter
    def sense(self, sense_hat):
        self.setSenseHat(sense_hat)

    def setSenseHat(self, sense_hat):
        """Associate SenHat object

        Args:
            sense_hat (SenseHat): SenseHat object

        Raises:
            Exception: Invalid SenseHat object provided
        """
        if sense_hat is None:
            raise Exception("A SenseHat object must be provided")

        get_orientation = getattr(sense_hat, "get_orientation", None)
        if get_orientation is None or not callable(sense_hat.get_orientation):
            raise Exception("A SenseHat object must be provided")

        self._sense = sense_hat

    def clear_pixels(self):
        """Clear the SenseHat LED matrix"""
        self._sense.clear()

    def update_pixels(self):
        """Update the SenseHat LED matrix from a cckkViewer object"""
        self.clear_pixels()
        self._sense.set_pixels(self.pixels)

    def getInputs(self, inc_joystick=True, inc_orientation=True, gyro_sensitivity=4):
        events = self._sense.stick.get_events()
        return_events = []
        simple_events = {
            "right": "R",
            "left": "L",
            "up": "U",
            "down": "D",
            "middle": "M"
        }
        dxdy_map = {
            "R": (1, 0),
            "L": (-1, 0),
            "U": (0, 1),
            "D": (0, -1)
        }

        if inc_joystick:
            for event in events:
                if event.action in ["pressed", "held"]:
                    return_events.append({
                        "timestamp": event.timestamp,
                        "direction": event.direction,
                        "action": event.action,
                        "simple": simple_events.get(event.direction, "?"),
                        "dx_dy": dxdy_map.get(simple_events.get(event.direction, "?"), (0, 0)),
                        "dx": dxdy_map.get(simple_events.get(event.direction, "?"), (0, 0))[0],
                        "dy": dxdy_map.get(simple_events.get(event.direction, "?"), (0, 0))[1]
                    })

        if inc_orientation:
            def _create_orientation_event(direction, action, value):
                simple = simple_events.get(direction, "?")
                dx_dy = dxdy_map.get(simple, (0, 0))
                return {
                    "timestamp": time.time(),
                    "direction": direction,
                    "action": action,
                    "value": value,
                    # 1-5
                    "scaled_value": min(5, round(value / gyro_sensitivity)) if value < 180 else min(5, round((360 - value) / gyro_sensitivity)),
                    "simple": simple,
                    "dx_dy": dx_dy,
                    "dx": dx_dy[0],
                    "dy": dx_dy[1]
                }

            orient = self._sense.get_orientation()
            if orient["roll"] > gyro_sensitivity and orient["roll"] < (gyro_sensitivity*10):
                return_events.append(_create_orientation_event(
                    "down", "roll", orient["roll"]))
            elif orient["roll"] > (360 - gyro_sensitivity*10) and orient["roll"] < (360 - gyro_sensitivity):
                return_events.append(_create_orientation_event(
                    "up", "roll", orient["roll"]))

            if orient["pitch"] > gyro_sensitivity and orient["pitch"] < (gyro_sensitivity*10):
                return_events.append(_create_orientation_event(
                    "left", "pitch", orient["pitch"]))
            elif orient["pitch"] > (360 - gyro_sensitivity*10) and orient["pitch"] < 355:
                return_events.append(_create_orientation_event(
                    "right", "pitch", orient["pitch"]))

        return return_events


class cckkEvent:
    """Class for SenseHat joystick emulator event"""
    def __init__(self, timestamp, direction, action):
        """Contructs a cckkEvent object

        Args:
            timestamp (float): Event timestamp
            direction (str): Joystick direction
            action (str): Joystick action
        """
        self.timestamp = timestamp
        self.direction = direction
        self.action = action

class cckkEventFactory:
    """Class for SenseHat joystick emulator"""
    def createInputEvent(timestamp=None, direction="up", action="pressed"):
        """Create a SenseHat emulator InputEvent event

        Returns:
            dict: Event dictionary
        """
        # direction - The direction the joystick was moved, as a string ("up", "down", "left", "right", "middle")
        # action - The action that occurred, as a string ("pressed", "released", "held")
        _timestamp = timestamp if timestamp is not None else time.time()
        return cckkEvent(timestamp= _timestamp, direction=direction, action=action)

    test_events = []
    def addTestEvent(timestamp=None, direction="up", action="pressed"):
        cckkEventFactory.test_events.append(
            cckkEvent(timestamp=timestamp, direction=direction, action=action)
        )

    event_idx = 0

    def get_events(self, loop: bool = False):
        if loop and cckkEventFactory.event_idx == len(cckkEventFactory.test_events) and len(cckkEventFactory.test_events) > 0:
            cckkEventFactory.event_idx = 0
        if cckkEventFactory.event_idx < len(cckkEventFactory.test_events):
            event = cckkEventFactory.test_events[cckkEventFactory.event_idx]
            cckkEventFactory.event_idx += 1
            return [event]
        else:
            return []

class cckkSenseHatEmu:
    """Class for SenseHat emulator"""

    def __init__(self):
        """Contructs a cckkSenseHatEmu object"""
        self._pixels = None
        self.stick = cckkEventFactory()

    def clear(self):
        self._pixels = [(0, 0, 0)] * 64

    def set_pixels(self, pixel_list):
        self._pixels = pixel_list
        img_str = ""
        _colour_dict = cckkColourDict(update_dict={ " ": (0,0,0) })
        for i in range(8):
            for j in range(8):
                pixel = self._pixels[i * 8 + j]
                img_str += _colour_dict.getRGB(pixel)
            img_str += "\n"
        print(img_str+"\n")

    def get_humidity(self):
        return 50.0

    def get_temperature(self):
        return 20.0

    def get_pressure(self):
        return 1013.25

    def get_orientation(self):
        return {"pitch": 0, "roll": 0, "yaw": 0}


if __name__ == '__main__':
    print("cckk module")
