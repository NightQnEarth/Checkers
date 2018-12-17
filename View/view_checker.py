from PyQt5.QtWidgets import QGraphicsItem
from View import view_methods
from Controller import controller_methods
from Model.colors import Colors


class Checker(QGraphicsItem):
    def __init__(self, logic_checker_object):
        super().__init__()
        from View import view_model

        self.color = (view_model.WhiteCheckerColor if
                      logic_checker_object.color ==
                      Colors.WhiteChecker else view_model.BlackCheckerColor)
        self.logic_checker_object = logic_checker_object

    def boundingRect(self):
        return view_methods.checker_bounding_rect(self)

    def paint(self, painter, option, widget=None):
        view_methods.checker_paint(self, painter)

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        controller_methods.checker_event(self)
