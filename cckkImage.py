def imgTransformFromArray(imgA, ncols):
    return [imgA[i:i+ncols] for i in range(0, len(imgA), ncols)]
    
def imgTransformToArray(imgAA):
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

