# test_cckkImage.py
import pytest

import sys
sys.path.append("./")

import cckk


def test_keep_within_and_calculate_mer():
    outer = cckkRectangle(xcols=10, yrows=10, xpos=0, ypos=0)
    inner = cckkRectangle(xcols=3, yrows=3, xpos=9, ypos=9)
    inner.keep_within(outer)
    # inner should be shifted so it fits entirely inside outer
    assert inner.xpos >= outer.xpos
    assert inner.ypos >= outer.ypos
    assert inner.xpos + inner.xcols <= outer.xpos + outer.xcols
    assert inner.ypos + inner.yrows <= outer.ypos + outer.yrows

    rlist = [
        cckkRectangle(xcols=2, yrows=2, xpos=1, ypos=1),
        cckkRectangle(xcols=3, yrows=1, xpos=4, ypos=0),
        cckkRectangle(xcols=1, yrows=4, xpos=0, ypos=3),
    ]
    mer = cckkRectangle.calculate_mer(rlist)
    assert isinstance(mer, cckkRectangle)
    # mer should enclose min xpos/min ypos to max extents
    min_x = min(r.xpos for r in rlist)
    min_y = min(r.ypos for r in rlist)
    max_x = max(r.xpos + r.xcols for r in rlist)
    max_y = max(r.ypos + r.yrows for r in rlist)
    assert mer.xpos == min_x
    assert mer.ypos == min_y
    assert mer.xcols == max_x - min_x
    assert mer.yrows == max_y - min_y

def test_background_and_view_ordering():
    # back: full red 2x2
    red = (255,0,0)
    white = (255,255,255)
    back_img = cckk(imgAA=[[red, red],[red, red]], name="back")
    # front: white at (0,0), rest transparent
    front_img = cckk(imgAA=[[white, None],[None, None]], name="front")
    viewer = cckkViewer(xcols=2, yrows=2, images=[front_img, back_img], fill=(0,0,0))
    # background length and fill check
    bg = viewer.background
    assert len(bg) == 4
    assert all(pixel == (0,0,0) for pixel in bg)
    view = viewer.view()
    # mapping: index = y*rows + x (view implementation uses yrows but for 2x2 it's equivalent)
    # expected: top-left white (front), others red (back)
    assert view[0] == white
    assert view[1] == red
    assert view[2] == red
    assert view[3] == red

def test_find_move_align_and_collision_intersection():
    # image A: 2x2 with values at all positions
    a1 = (10,10,10)
    a2 = (20,20,20)
    img_a = cckk(imgAA=[[a1, a2],[a2, a1]], name="A")
    # image B: 2x2 with top-left transparent, others non-transparent
    b1 = (30,30,30)
    img_b = cckk(imgAA=[[None, b1],[b1, None]], name="B")
    viewer = cckkViewer(xcols=2, yrows=2, images=[img_a, img_b])
    # find_image
    idx_a = viewer.find_image("A")
    idx_b = viewer.find_image("B")
    assert idx_a >= 0
    assert idx_b >= 0
    # align image A to top-left of viewer
    viewer.align_image("A", horiz="L", vert="T")
    idx = viewer.find_image("A")
    assert viewer._images[idx].xpos == viewer.xpos
    assert viewer._images[idx].ypos == viewer.ypos
    # collision count: overlapping non-None pixels between A and B
    # both images overlap entirely; overlapping positions with non-None in both: positions where both not None:
    # A has all non-None, B has 3 non-None (except top-left)
    expected_collision = 3
    coll = viewer.collision("A", "B")
    assert coll == expected_collision
    # intersection: pixels should come from first image (A) in intersection region
    inter = viewer.intersection("A", "B")
    assert inter is not None
    # intersection position should equal overlapping rectangle position (viewer uses image positions)
    # as both at same position (default 0,0) intersection xpos/ypos should be 0,0 for these images
    assert inter.xpos == max(img_a.xpos, img_b.xpos)
    assert inter.ypos == max(img_a.ypos, img_b.ypos)
    # pixels in intersection come from A: compare inter pixel at (1,0) (where B has non-None)
    # compute local coords inside inter to map to A
    if inter.xcols > 0 and inter.yrows > 0:
        # pick a coordinate that we know overlaps and is not None in A
        px = inter.pixel(1,0)
        # This should equal the corresponding pixel from A
        ax = inter.xpos + 1 - img_a.xpos
        ay = inter.ypos + 0 - img_a.ypos
        assert px == img_a.pixel(ax, ay)

def test_add_images_invalid_raises():
    viewer = cckkViewer()
    with pytest.raises(Exception):
        viewer.add_images([object()])

