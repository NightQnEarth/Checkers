from PyQt5.QtGui import QColor
from os import path

Scene = None
View = None
CheckersBorder = None

Bin = set()

UpperWidget = None
HelpButton = None

WhiteCheckerColor = QColor(237, 238, 239)
BlackCheckerColor = QColor(32, 33, 35)
WhiteCellColor = path.join('Images', 'white_cell_color.jpg')
BlackCellColor = path.join('Images', 'black_cell_color.jpg')
FrameBorderColor = path.join('Images', 'frame_border_color.jpg')
Background = path.join('Images', 'background.jpg')
