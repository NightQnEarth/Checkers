from PyQt5.QtWidgets import QGraphicsScene
import View.view_methods


class Scene(QGraphicsScene):
    def __init__(self):
        super().__init__()

    def drawBackground(self, painter, rect):
        View.view_methods.scene_draw_background(painter, rect)
