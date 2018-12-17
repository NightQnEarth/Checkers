from PyQt5.QtCore import Qt, QRectF, QPointF, QSizeF
from PyQt5.QtGui import QFont, QPen, QBrush, QColor, QPixmap
from PyQt5.QtWidgets import QDesktopWidget, QGraphicsView, QApplication
from View import view_cell, view_checker, checkers_border, widgets
from Model import logic


def scene_draw_background(painter, rect):
    from View import view_model

    painter.drawPixmap(
        rect.topLeft(),
        QPixmap(view_model.Background),
    )


def checkers_border_paint(obj, painter):
    """Здесь производится рисование фона, рамок и градуировки для 
    шашечной доски"""

    from View import view_model

    pen = QPen()
    pen.setWidthF(obj.pen_width)
    pen.setColor(QColor(89, 65, 37))
    painter.setPen(pen)

    painter.drawPixmap(
        QPointF(obj.cell_size * (1 - obj.indent_frame_from_border),
                obj.cell_size * (1 - obj.indent_frame_from_border)),
        QPixmap(view_model.FrameBorderColor),
        QRectF(QPointF(obj.cell_size * (1 - obj.indent_frame_from_border),
                       obj.cell_size * (1 - obj.indent_frame_from_border)),
               QPointF(obj.cell_size * (obj.border_size + 1)
                       + obj.cell_size * obj.indent_frame_from_border,
                       obj.cell_size * (obj.border_size + 1) +
                       obj.cell_size * obj.indent_frame_from_border))
    )

    painter.drawRect(
        QRectF(QPointF(obj.cell_size * (1 - obj.indent_frame_from_border),
                       obj.cell_size * (1 - obj.indent_frame_from_border)),
               QPointF(obj.cell_size * (obj.border_size + 1)
                       + obj.cell_size * obj.indent_frame_from_border,
                       obj.cell_size * (obj.border_size + 1) +
                       obj.cell_size * obj.indent_frame_from_border))
    )
    set_graduation(obj, painter)


def checkers_border_bounding_rect(obj):
    return QRectF(
        -obj.pen_width + obj.cell_size
        * (1 - obj.indent_frame_from_border),
        -obj.pen_width + obj.cell_size
        * (1 - obj.indent_frame_from_border),
        obj.cell_size * (obj.border_size + 2 *
                         obj.indent_frame_from_border) + 2 *
        obj.pen_width,
        obj.cell_size * (obj.border_size + 2 *
                         obj.indent_frame_from_border) + 2 *
        obj.pen_width)


def checker_bounding_rect(obj):
    return rect_coordinates_create(
        obj.logic_checker_object.cell.border_coordinates)


def checker_paint(obj, painter):
    from Model import logic_model
    from View import view_model

    indent_from_border_cell = 5
    indent_from_outer_circle = 4
    indent_from_border_cell_text = 16

    rect_coordinates = rect_coordinates_create(
        obj.logic_checker_object.cell.border_coordinates)

    circle_draw(painter,
                rect_coordinates,
                obj.color,
                indent_from_border_cell)

    if obj.color == view_model.WhiteCheckerColor:
        circle_draw(painter,
                    rect_coordinates,
                    QColor(194, 194, 196),
                    indent_from_border_cell,
                    indent_from_outer_circle)
    else:
        circle_draw(painter,
                    rect_coordinates,
                    QColor(89, 91, 96),
                    indent_from_border_cell,
                    indent_from_outer_circle)

    if obj.logic_checker_object.isKing:
        draw_color = view_model.WhiteCheckerColor
        if obj.color == view_model.WhiteCheckerColor:
            draw_color = view_model.BlackCheckerColor

        text_draw(painter, rect_coordinates, draw_color,
                  indent_from_border_cell_text)

    if obj.logic_checker_object.inFocus:
        blue_rect_draw(painter, obj)

        if ((logic_model.NetworkGame and logic_model.PlayerSide ==
             logic_model.Stroke) or (not logic_model.NetworkGame)):
            if obj.logic_checker_object.color == logic_model.Stroke:

                if (logic_model.CheckersForBitWithChains and
                    obj.logic_checker_object in
                        logic_model.CheckersForBitWithChains.keys()):

                    chains_focus_draw(
                        logic_model.CheckersForBitWithChains, obj, painter)

                elif not logic_model.CheckersForBitWithChains:
                    steps_focus_draw(painter, obj.logic_checker_object)


def cell_bounding_rect(obj):
    return rect_coordinates_create(obj.logic_cell_object.border_coordinates)


def cell_paint(obj, painter):
    """Здесь аккуратнее, многое зависит от изображения. Оно должно 
    быть не меньше игрового поля"""

    painter.drawPixmap(
        rect_coordinates_create(obj.logic_cell_object.border_coordinates),
        QPixmap(obj.color),
        rect_coordinates_create(obj.logic_cell_object.border_coordinates)
    )


def steps_focus_draw(painter, checker):
    """Проихводится отрисовка зелёных обрамлений на доступных для простого 
    хода клетках"""

    pen = QPen(QColor(78, 237, 42))
    pen.setWidthF(2)
    painter.setPen(pen)

    for chain in logic.possible_cells_for_steps_or_hit(checker):
        for cell in chain:
            painter.drawRect(rect_coordinates_create(cell.border_coordinates))


def chains_focus_draw(checkers_for_bit_with_chains, checker, painter):
    """Производится отрисовка красных и фиолетовых обрамлений на доступных 
    цепях"""

    if checkers_for_bit_with_chains and checker.logic_checker_object in \
            checkers_for_bit_with_chains.keys():
        pen = QPen(QColor(249, 37, 37))
        pen.setWidthF(2)
        painter.setPen(pen)

        nearest_cells = set()

        for chain in \
                checkers_for_bit_with_chains[checker.logic_checker_object]:
            nearest_cells.add(chain[0])

        for chain in \
                checkers_for_bit_with_chains[checker.logic_checker_object]:
            for _cell in chain:
                if _cell in nearest_cells:
                    pen = QPen(QColor(249, 37, 37))
                    pen.setWidthF(2)
                    painter.setPen(pen)
                else:
                    pen = QPen(QColor(150, 72, 206))
                    pen.setWidthF(2)
                    painter.setPen(pen)
                painter.drawRect(rect_coordinates_create(
                    _cell.border_coordinates))


def blue_rect_draw(painter, checker):
    """Производится отривоска синего обрамления на клетке, на которой стоит 
    шашка в фокусе"""

    pen = QPen(QColor(66, 134, 244))
    pen.setWidthF(1.5)
    painter.setPen(pen)

    brush = QBrush()
    painter.setBrush(brush)

    painter.drawRect(rect_coordinates_create(
        checker.logic_checker_object.cell.border_coordinates))


def circle_draw(painter, cell_coordinates, color,
                indent_from_border_cell, indent_from_outer_circle=0):
    """Рисует круги. Используется для отрисовки шашек"""

    pen = QPen()

    pen.setColor(color)
    painter.setPen(pen)
    painter.setBrush(QBrush(color))

    rect_coordinates = QRectF(
        QPointF(
            cell_coordinates.left() + indent_from_border_cell
            + indent_from_outer_circle,
            cell_coordinates.top() + indent_from_border_cell
            + indent_from_outer_circle),
        QSizeF(
            cell_coordinates.width() - 2 * (
                indent_from_border_cell + indent_from_outer_circle),
            cell_coordinates.height() - 2 * (
                indent_from_border_cell + indent_from_outer_circle))
    )
    painter.drawEllipse(rect_coordinates)


def text_draw(painter, rect_coordinates, color, indent_from_border_cell):
    """Рисует символ K на дамке"""

    pen = QPen(color)

    painter.setPen(pen)
    painter.setFont(QFont('Constantia', 16))

    rect_coordinates = QRectF(
        QPointF(
            rect_coordinates.left() + indent_from_border_cell,
            rect_coordinates.top() + indent_from_border_cell),
        QSizeF(
            rect_coordinates.width() - 2 * indent_from_border_cell,
            rect_coordinates.height() - 2 * indent_from_border_cell)
    )
    painter.drawText(rect_coordinates, Qt.AlignCenter, 'K')


def set_graduation(obj, painter):
    """Рисует вертикальную шкалу из цифр и горизонтальную шкалу из букв 
    на шашечной доске (градуирует шашечную доску)"""

    from Model import logic_model

    painter.setFont(QFont(obj.font, obj.font_size))
    pen = QPen(QColor(Qt.white))
    painter.setPen(pen)

    i = obj.border_size

    while i != 0:
        number = str(obj.border_size - i + 1)
        character = chr(ord(logic_model.BeginGraduationLetter) + i - 1)

        painter.drawText(
            QRectF(obj.cell_size * (1 - obj.indent_frame_from_border),
                   obj.cell_size * i,
                   obj.cell_size * obj.indent_frame_from_border,
                   obj.cell_size),
            Qt.AlignCenter,
            number)

        painter.drawText(
            QRectF(obj.cell_size * i,
                   obj.cell_size * (obj.border_size + 1),
                   obj.cell_size,
                   obj.cell_size * obj.indent_frame_from_border),
            Qt.AlignCenter,
            character)

        i -= 1


def view_setting(obj):
    """Производится настройка представления"""

    obj.setCacheMode(QGraphicsView.CacheBackground)
    obj.setWindowTitle('Checkers Border')
    obj.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    obj.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    obj.setFixedSize(700, 700)

    desktop_geometry = QApplication.desktop().availableGeometry()

    if not desktop_geometry.contains(obj.frameGeometry()):
        if desktop_geometry.width() < obj.width():
            obj.setFixedWidth(desktop_geometry.width())
        if desktop_geometry.height() < obj.height():
            obj.setFixedHeight(desktop_geometry.height())

    move_center(obj)


def move_center(obj):
    """Производит точное центрирование представления на экране"""

    obj.move(obj.width() * -2, 0)
    obj.show()
    exact_window_form = obj.frameGeometry()
    exact_desktop_center = QDesktopWidget().availableGeometry().center()
    exact_window_form.moveCenter(exact_desktop_center)
    obj.move(exact_window_form.topLeft())


def cells_drop(border_matrix):
    """Устанавливает графические объекты клеток на сцену"""

    from View import view_model

    for i in range(len(border_matrix)):
        for j in range(len(border_matrix[i])):
            logic_cell_obj = border_matrix[i][j]
            cell = view_cell.Cell(logic_cell_obj)
            view_model.Scene.addItem(cell)


def checkers_drop(border_matrix):
    """Устанавливает графические объекты шашек на сцену"""

    from View import view_model

    for i in range(len(border_matrix)):
        for j in range(len(border_matrix[i])):
            logic_checker_obj = border_matrix[i][j].checker_stay
            if logic_checker_obj:
                checker = view_checker.Checker(logic_checker_obj)
                view_model.Scene.addItem(checker)


def rect_coordinates_create(border_coordinates):
    """По координатам доски возвращает rect-координаты относительно сцены"""

    from Model import logic_model
    from View import view_model

    i = view_model.CheckersBorder.border_size - border_coordinates[1]
    j = ord(border_coordinates[0]) - ord(
        logic_model.BeginGraduationLetter)

    return QRectF(
        QPointF((j + 1), (i + 1)) * view_model.CheckersBorder.cell_size,
        QSizeF(view_model.CheckersBorder.cell_size,
               view_model.CheckersBorder.cell_size))


def widgets_set(view_model, logic_model):
    view_model.CheckersBorder = checkers_border.CheckersBorder(
        logic_model.Size)
    view_model.Scene.addItem(view_model.CheckersBorder)

    view_model.UpperWidget = widgets.UpperWidget()
    view_model.Scene.addWidget(view_model.UpperWidget)

    view_model.HelpButton = widgets.HelpButton()
    view_model.Scene.addWidget(view_model.HelpButton)
