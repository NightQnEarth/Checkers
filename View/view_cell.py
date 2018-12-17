from PyQt5.QtWidgets import QGraphicsItem
from View import view_methods, view_checker
from Controller import controller_methods
from Model.colors import Colors


class Cell(QGraphicsItem):
    def __init__(self, logic_cell_object):
        super().__init__()
        from View import view_model

        self.color = (view_model.WhiteCellColor if logic_cell_object.color ==
                      Colors.WhiteCell else view_model.BlackCellColor)
        self.logic_cell_object = logic_cell_object

    def boundingRect(self):
        return view_methods.cell_bounding_rect(self)

    def paint(self, painter, option, widget=None):
        view_methods.cell_paint(self, painter)

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        from View import view_model

        for item in view_model.Scene.items():
            if isinstance(item, view_checker.Checker) and \
                    item.logic_checker_object.cell is self.logic_cell_object:
                view_checker.Checker.mouseReleaseEvent(item, event)
                return
        controller_methods.cell_event(self)
