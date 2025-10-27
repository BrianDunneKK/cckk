def imgImportFromArray(imgA, ncols):
    return [imgA[i:i+ncols] for i in range(0, len(imgA), ncols)]
    
def imgExportToArray(imgAA):
    imgA = []
    for row in imgAA:
        for pixel in row:
            imgA.append(pixel)
    return imgA
        
def imgRoll(imgAA, dx, dy):
    nrows = len(imgAA)
    ncols = len(imgAA[0])
    result = []
    for r in range(nrows):
        new_r = (r - dy + nrows) % nrows
        new_row = []
        for c in range(ncols):
            new_c = (c - dx + ncols) % ncols
            new_row.append(imgAA[new_r][new_c])
        result.append(new_row)
    return result

def imgMove(imgAA, dx, dy, fill):
    nrows = len(imgAA)
    ncols = len(imgAA[0])
    resultX = []
    result = []
    
    if dx > 0 & dx <= ncols: # move right
        for r in range(nrows):
            new_row = [fill]*dx
            for c in range(ncols-dx):
                new_row.append(imgAA[r][c])
            resultX.append(new_row)
    elif dx < 0 & dx >= -ncols: # move left
        for r in range(nrows):
            new_row = []
            for c in range(-dx, ncols):
                new_row.append(imgAA[r][c])
            new_row += [fill]*(-dx)
            resultX.append(new_row)
    else: # dx == 0 or invalid
        resultX = [row[:] for row in imgAA]

    if dy > 0 & dy <= nrows: # move down
        for r in range(dy):
            result.append([fill]*ncols)
        for r in range(nrows-dy):
            result.append(resultX[r])
    elif dy < 0 & dy >= -nrows: # move up
        for r in range(-dy, nrows):
            result.append(resultX[r])
        for r in range(-dy):
            result.append([fill]*ncols)
    else: # dy == 0 or invalid
        result = [row[:] for row in resultX]

    return result

def imgPrint(imgAA):
    str = ""
    for row in imgAA:
        for pixel in row:
            str += pixel + " "
        str += "\n"
    print(str)



class cckkImage:
    """Class representation of an image on a SenseHat"""
    imgAA = None

    def __init__(self, imgA = None, ncols = 8):
        self.imgAA = None
        if (imgA is not None):
            self.setFromArray(imgA, ncols)

    def setFromArray(self, imgA, ncols):
        self.imgAA = [imgA[i:i+ncols] for i in range(0, len(imgA), ncols)]
        return self

    def pixels(self):
        imgA = []
        for row in self.imgAA:
            for pixel in row:
                imgA.append(pixel)
        return imgA

    @property
    def nrows(self):
        """No. of rows in the image"""
        return len(self.imgAA)

    @property
    def ncols(self):
        """No. of columns in the image"""
        return len(self.imgAA[0])

    def roll(self, dx, dy):
        result = []
        for r in range(nrows):
            new_r = (r - dy + self.nrows) % self.nrows
            new_row = []
            for c in range(ncols):
                new_c = (c - dx + self.ncols) % self.ncols
                new_row.append(self.imgAA[new_r][new_c])
            result.append(new_row)
        self.imgAA = result
        return self

    def move(self, dx, dy, fill):
        resultX = []
        result = []
        
        if dx > 0 & dx <= self.ncols: # move right
            for r in range(self.nrows):
                new_row = [fill]*dx
                for c in range(self.ncols-dx):
                    new_row.append(self.imgAA[r][c])
                resultX.append(new_row)
        elif dx < 0 & dx >= -self.ncols: # move left
            for r in range(self.nrows):
                new_row = []
                for c in range(-dx, self.ncols):
                    new_row.append(self.imgAA[r][c])
                new_row += [fill] * (-dx)
                resultX.append(new_row)
        else: # dx == 0 or invalid
            resultX = [row[:] for row in self.imgAA]

        if dy > 0 & dy <= self.nrows: # move down
            for r in range(dy):
                result.append([fill] * self.ncols)
            for r in range(self.nrows - dy):
                result.append(resultX[r])
        elif dy < 0 & dy >= -self.nrows: # move up
            for r in range(-dy, self.nrows):
                result.append(resultX[r])
            for r in range(-dy):
                result.append([fill] * self.ncols)
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
