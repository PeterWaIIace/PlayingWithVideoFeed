import pytest

from zoom import ZoomScope

class Mockup:

    def __init__(self,x,y,h,w):
        self._x = x
        self._y = y 
        self.h = h
        self.w = w

    def copy(self,obj):
        return Mockup(obj.x(),obj.y(),obj.height(),obj.width())

    def x(self):
        return self._x

    def y(self):
        return self._y

    def height(self):
        return self.h

    def width(self):
        return self.w


def test_zoom_constructor():
    assert ZoomScope(0,0) is not None

def test_zoom_dummy_cropImage():
    mockDisp = Mockup(0,0,100,100)
    mockImg  = Mockup(0,0,100,100)
    zoomDisp = ZoomScope(100,100)

    Img = zoomDisp.cropImage(mockImg,mockDisp)

    assert Img.width()  == mockImg.width()
    assert Img.height() == mockImg.height()

def test_zoom_setZoom_cropImage():
    mockDisp = Mockup(0,0,100,100)
    mockImg  = Mockup(0,0,100,100)
    zoomDisp = ZoomScope(100,100)

    zoomDisp.setZoom(0,50,0,50,mockDisp)

    Img = zoomDisp.cropImage(mockImg,mockDisp)


    assert Img.x()      == 0
    assert Img.y()      == 0
    assert Img.width()  == mockImg.width()/2
    assert Img.height() == mockImg.height()/2

def test_zoom_left_double_setZoom_cropImage():
    mockDisp = Mockup(0,0,100,100)
    mockImg  = Mockup(0,0,100,100)
    zoomDisp = ZoomScope(100,100)

    zoomDisp.setZoom(0,50,0,50,mockDisp)
    zoomDisp.setZoom(0,50,0,50,mockDisp)

    Img = zoomDisp.cropImage(mockImg,mockDisp)

    assert Img.x()      == 0
    assert Img.y()      == 0
    assert Img.width()  == mockImg.width()/4
    assert Img.height() == mockImg.height()/4

def test_zoom_center_setZoom_cropImage():
    mockDisp = Mockup(0,0,100,100)
    mockImg  = Mockup(0,0,100,100)
    zoomDisp = ZoomScope(100,100)

    zoomDisp.setZoom(25,75,25,75,mockDisp)

    Img = zoomDisp.cropImage(mockImg,mockDisp)

    assert Img.x()      == 25
    assert Img.y()      == 25
    assert Img.width()  == mockImg.width()/2
    assert Img.height() == mockImg.height()/2

def test_zoom_double_center_setZoom_cropImage():
    mockDisp = Mockup(0,0,100,100)
    mockImg  = Mockup(0,0,100,100)
    zoomDisp = ZoomScope(100,100)

    zoomDisp.setZoom(25,75,25,75,mockDisp)
    zoomDisp.setZoom(25,75,25,75,mockDisp)

    Img = zoomDisp.cropImage(mockImg,mockDisp)

    assert Img.x()      == 37
    assert Img.y()      == 37
    assert Img.width()  == mockImg.width()/4
    assert Img.height() == mockImg.height()/4

def test_zoom_right_setZoom_cropImage():
    mockDisp = Mockup(0,0,100,100)
    mockImg  = Mockup(0,0,100,100)
    zoomDisp = ZoomScope(100,100)

    zoomDisp.setZoom(50,100,50,100,mockDisp)
  
    Img = zoomDisp.cropImage(mockImg,mockDisp)

    assert Img.x()      == 50
    assert Img.y()      == 50
    assert Img.width()  == mockImg.width()/2
    assert Img.height() == mockImg.height()/2

def test_zoom_right_double_setZoom_cropImage():
    mockDisp = Mockup(0,0,100,100)
    mockImg  = Mockup(0,0,100,100)
    zoomDisp = ZoomScope(100,100)

    zoomDisp.setZoom(50,100,50,100,mockDisp)
    zoomDisp.setZoom(50,100,50,100,mockDisp)
  
    Img = zoomDisp.cropImage(mockImg,mockDisp)

    assert Img.x()      == 75
    assert Img.y()      == 75
    assert Img.width()  == mockImg.width()/4
    assert Img.height() == mockImg.height()/4

def test_zoom_diff_image_display_cropImage():
    mockDisp = Mockup(0,0,100,100)
    mockImg  = Mockup(0,0,90,90)
    zoomDisp = ZoomScope(100,100)

    Img = zoomDisp.cropImage(mockImg,mockDisp)

    assert Img.x()      == mockImg.x()
    assert Img.y()      == mockImg.y()
    assert Img.width()  == mockImg.width()
    assert Img.height() == mockImg.height()