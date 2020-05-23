# -*- coding: utf-8 -*-
import logging
from enum import Enum, auto
from vindauga.constants.grow_flags import gfGrowHiX, gfGrowHiY
from vindauga.types.group import Group
from .background import Background

logger = logging.getLogger(__name__)


class GrowDirection(Enum):
    GrowHorizontal = auto()
    GrowVertical = auto()


class FlexBox(Group):

    def __init__(self, bounds, direction: GrowDirection):
        super().__init__(bounds)
        self.growMode = gfGrowHiX | gfGrowHiY
        self.__grow_direction = direction
        self.background = self.initBackground(self.getExtent())
        if self.background:
            self.background.growMode = gfGrowHiX | gfGrowHiY
            self.insert(self.background)

    @staticmethod
    def initBackground(r):
        return Background(r, ' ')

    def changeBounds(self, bounds):
        super().changeBounds(bounds)
        self._repackCurrent(self.getBounds())

    def locate(self, bounds):
        super().locate(bounds)
        self._repackCurrent(self.getBounds())

    def _repackCurrent(self, bounds):
        # Sub 1 for background

        numChildren = len(self.children) - 1
        if numChildren < 1:
            return

        size = bounds.bottomRight - bounds.topLeft
        width = size.x
        height = size.y

        if self.__grow_direction == GrowDirection.GrowHorizontal:
            width -= numChildren - 1
            width, gap = divmod(width, numChildren)
        else:
            height -= numChildren - 1
            height, gap = divmod(height, numChildren)

        if not (width and height):
            return

        x = 0
        y = 0
        gap = min(1, gap)
        for c in reversed(self.children[:-1]):
            bounds = c.getBounds()
            bounds.topLeft.x = x
            bounds.topLeft.y = y
            bounds.bottomRight.x = x + width
            bounds.bottomRight.y = y + height
            c.locate(bounds)
            if self.__grow_direction == GrowDirection.GrowHorizontal:
                x += width + gap
            else:
                y += height + gap

    def insertView(self, view, target=None):
        super().insertView(view, target)

        if self.owner:
            self._repackCurrent(self.getBounds())

    def remove(self, view):
        super().removeView(view)
        if self.owner:
            self._repackCurrent(self.getBounds())

    def __str__(self):
        return '<FlexBox {} ({})>'.format(self.size, len(self.children))
