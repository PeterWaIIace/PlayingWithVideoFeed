from PyQt5.QtCore import QRect


class Point:
    '''
    Point keeps cartesian coordinates
    '''

    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    def x(self):
        '''
        Returns x axis coordinate
        '''
        return self.__x

    def y(self):
        '''
        Returns y axis coordinate
        '''
        return self.__y


class ROI:
    '''
    RoI - Region of Interest keeps square shape
    which can be passed to zoom utility.
    '''

    def __init__(self, p1=None, p2=None):
        '''
        Pass none, one or two points in cartesian
        coordinate system to create region of interest.

        When passing none or one, there is still required
        to call addPoint to pass rest of points.
        '''
        self.__p1 = p1
        self.__p2 = p2

    def addPoint(self, p):
        '''
        Pass one point to region of interest.
        The oldest point is overwritten.
        '''

        if(self.__p1 is None):
            self.__p1 = p
        elif(self.__p2 is None):
            self.__p2 = p
        else:
            self.__p1 = p
            self.__p2 = None

    def clearRoI(self):
        '''
        Removes both points from RoI
        '''

        self.__p1 = None
        self.__p2 = None

    def getP1(self):
        '''
        Returns first point.
        '''
        return self.__p1

    def getP2(self):
        '''
        Returns second point.
        '''
        return self.__p2


class ZoomScope:
    '''
    ZoomScope is representation of digital zoom on image.
    It scales image into new frame.

    It is possible to do zoom stacking - zoom more when zoom is already applied.
    Appropriate scaling will be applied.

    To use zoom:
    1) first RoI object need to be created, and passed to:
    set() - sets the zoom parameters

    2) to execute zoom on image, you need to image in numpy format to:
    apply() - executes zoom
    '''

    MINIMAL_ZOOM_W_H = 10

    def __init__(self):
        self.__x = 0
        self.__y = 0
        self.__w = 0
        self.__h = 0
        self.__zoom_applied = False

    def width(self):
        return self.__w

    def height(self):
        return self.__h

    def isSet(self):
        return self.__zoom_applied

    def set(self, region, display):
        '''
        Sets zoom based on the region (but zoom is not applied to frame yet).
        It also need to take display (Qt object) for reference.
        '''
        x1 = region.getP1().x()
        y1 = region.getP1().y()
        x2 = region.getP2().x()
        y2 = region.getP2().y()

        x1, x2, y1, y2 = self.__get_rescaled_input(x1, x2, y1, y2, display)

        if self.__check_boundaries(x1, x2, y1, y2):
            self.__set_zoom_ROI(x1, x2, y1, y2)
        else:
            self.reset(display.width(), display.height())

    def reset(self, width, height):
        '''
        Resets zoom to default position. It takes width and height of display.
        '''
        self.__x = 0
        self.__y = 0
        self.__w = width
        self.__h = height
        self.crop_image = False

    def apply(self, img, display):
        '''

        Applies set zoom to the frame.
        It also need to take display (Qt object) for reference.

        '''

        # check if images and display have the same dimensions
        sf_w, sf_h = self.__get_dim_scale_factor(display, img)

        crop_rect = QRect(
            self.__x / sf_w,
            self.__y / sf_h,
            self.__w / sf_w,
            self.__h / sf_h)
        return img.copy(crop_rect)

    def __get_dim_scale_factor(self, size1, size2):

        if size2.width() != 0 and size2.height() != 0:
            sf_w = size1.width() / size2.width()
            sf_h = size1.height() / size2.height()
        else:
            sf_w = 1
            sf_h = 1
        return (sf_w, sf_h)

    def __get_rescaled_input(self, x, w, y, h, display):
        sf_w, sf_h = self.__get_dim_scale_factor(display, self)

        x = x / sf_w + self.__x
        w = w / sf_w + self.__x
        y = y / sf_h + self.__y
        h = h / sf_h + self.__y

        return (x, w, y, h)

    def __check_boundaries(self, x1, x2, y1, y2):
        return (self.MINIMAL_ZOOM_W_H < abs(x1 - x2)
                and
                self.MINIMAL_ZOOM_W_H < abs(y1 - y2))

    def __set_zoom_ROI(self, x1, x2, y1, y2):

        if(x1 < x2):
            self.__x = x1
            self.__w = x2 - x1
        else:
            self.__x = x2
            self.__w = x1 - x2
        if(y1 < y2):
            self.__y = y1
            self.__h = y2 - y1
        else:
            self.__y = y2
            self.__h = y1 - y2
        self.__zoom_applied = True
