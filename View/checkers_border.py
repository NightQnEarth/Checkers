from PyQt5.QtWidgets import QGraphicsItem
from View import view_methods


class CheckersBorder(QGraphicsItem):
    def __init__(self, size):
        super().__init__()
        self.cell_size = 50
        self.border_size = size
        self.indent_frame_from_border = 0.5
        self.pen_width = 3
        self.font = 'Constantia'
        self.font_size = 14

    def boundingRect(self):
        return view_methods.checkers_border_bounding_rect(self)

    def paint(self, painter, option, widget=None):
        view_methods.checkers_border_paint(self, painter)
