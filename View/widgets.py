from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QStyle
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize
from Model import logic
from View import dialog_boxes
from Controller import controller_methods


class UpperWidget(QWidget):
    def __init__(self):
        super().__init__()

        from View import view_model
        from Model import logic_model

        y_begin = x_begin = \
            view_model.CheckersBorder.cell_size * \
            (1 - view_model.CheckersBorder.indent_frame_from_border)\
            - 4 * view_model.CheckersBorder.pen_width

        x_end = (view_model.CheckersBorder.cell_size
                 * (view_model.CheckersBorder.border_size + 2 *
                    view_model.CheckersBorder.indent_frame_from_border) + 4
                 * view_model.CheckersBorder.pen_width) + x_begin

        self.setGeometry(x_begin, -y_begin +
                         view_model.CheckersBorder.pen_width, x_end, 0)

        self.exit_button = self.exit_button_create()
        self.step_back_button = self.step_back_button_create()
        self.step_forward_button = self.step_forward_button_create()
        self.save_players_button = self.save_players_button_create()
        self.new_game_button = self.new_game_button_create()
        if logic_model.NetworkGame:
            self.new_game_button.setDisabled(True)
            self.step_back_button.setDisabled(True)
            self.step_forward_button.setDisabled(True)

        self.setLayout(self.main_layout())

        self.setAttribute(Qt.WA_TranslucentBackground)

    def main_layout(self):
        """Создает горизонтальный контейнер с кнопками"""

        h_box = QHBoxLayout()
        h_box.setSpacing(0)

        h_box.addWidget(self.step_back_button)
        h_box.addWidget(self.step_forward_button)
        h_box.addWidget(self.save_players_button)
        h_box.addWidget(self.new_game_button)
        h_box.addWidget(self.exit_button)
        return h_box

    def exit_button_create(self):
        return self.create_button('Exit', self.exit_button_action)

    def step_back_button_create(self):
        return self.create_button('Back', self.step_back_button_action)

    def step_forward_button_create(self):
        return self.create_button('Forward', self.step_forward_button_action)

    def save_players_button_create(self):
        return self.create_button('Save', self.save_players_button_action)

    def new_game_button_create(self):
        return self.create_button('New game', self.new_game_button_action)

    @staticmethod
    def exit_button_action():
        """Выход из игры"""

        from Model import logic_model
        if logic_model.IsSaved:
            dialog_boxes.exit_dialog_raise()
        else:
            dialog_boxes.save_and_exit_dialog_raise()

    @staticmethod
    def step_back_button_action():
        print("Sorry, it doesn't work now.")

    @staticmethod
    def step_forward_button_action():
        print("Sorry, it doesn't work now.")

    @staticmethod
    def save_players_button_action():
        """Сохранение текущей партии"""

        logic.save_game()
        dialog_boxes.save_dialog_raise()

    @staticmethod
    def new_game_button_action():
        """Создание новой игры"""

        controller_methods.new_game_create()

    @staticmethod
    def create_button(button_name, event_func):
        """Вынесены общие для всех кнопок UpperWidget свойства"""

        result = QPushButton(button_name)
        result.setFont(QFont('Constantia', 10))
        result.setFocusPolicy(Qt.NoFocus)

        result.setStyleSheet(
            'background-color: rgb(229, 192, 146);'
            'padding: 4px;')

        result.clicked.connect(event_func)

        return result


class HelpButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(20, 20))
        self.move(0, 0)
        self.setStyleSheet('background: transparent')
        self.setIcon(self.style().standardIcon(
            QStyle.SP_TitleBarContextHelpButton))

    def mouseReleaseEvent(self, *args, **kwargs):
        pass

    def mousePressEvent(self, *args, **kwargs):
        dialog_boxes.help_window_raise()
