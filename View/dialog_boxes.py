from PyQt5.QtWidgets import QPushButton, QMessageBox, QInputDialog
from PyQt5.Qt import QCoreApplication, QApplication
from PyQt5.QtGui import QBrush, QPainter, QFont
from PyQt5.QtCore import QRectF, QSize
from PyQt5.QtCore import Qt
from pathlib import Path
import socket
from Model import logic
from Model.colors import Colors
from Controller import controller_methods, multiplayer
from View import widgets
import time

WaitDialog = None


class ColorDialogButton(QPushButton):
    def __init__(self, color):
        super().__init__()
        self.color = color
        self.setMinimumSize(QSize(30, 30))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(self.color))
        painter.drawRoundedRect(QRectF(0, 0, 30, 30), 100.0, 100.0)


class GameModeDialogButton(QPushButton):
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.setText(text)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawRect(QRectF(0, 0, 30, 30))


def quit_game():
    """Выходит из игры. Если в текущем сеансе игра не сохранялась, 
    то удаляет загрузочный файл(если он есть)"""

    from Model import logic_model
    if not logic_model.WasSaveInThisGame:
        if Path(logic_model.SavedSingleGame).exists():
            Path(logic_model.SavedSingleGame).unlink()
        elif Path(logic_model.SavedNetworkGame).exists():
            Path(logic_model.SavedNetworkGame).unlink()

    if logic_model.NetworkGame and not logic_model.ReceivedThreadIsRunning:
        with socket.socket() as _socket:
            try:
                _socket.connect(multiplayer.OpponentAddress)
                _socket.sendall(b'I left.')
            except OSError:
                pass

    QCoreApplication.quit()


def win_dialog_raise(side):
    """Вызывает диалоговое окно, сообщающее о победе"""

    from Model import logic_model

    color_str = 'White' if side == Colors.WhiteChecker else 'Black'

    text = "{} won!".format(color_str)

    dialog_window = QMessageBox()

    dialog_create(dialog_window, text)

    quit_game_button = QPushButton('Quit the game')
    quit_game_button.clicked.connect(save_and_exit_dialog_raise)

    if not logic_model.NetworkGame:
        new_game_button = QPushButton('New game')
        new_game_button.clicked.connect(controller_methods.new_game_create)
        dialog_window.addButton(new_game_button, QMessageBox.AcceptRole)
    dialog_window.addButton(quit_game_button, QMessageBox.RejectRole)

    dialog_window.exec()
    dialog_window.close()


def color_choice_dialog_raise():
    """Вызывает диалоговое окно выбора цвета"""

    from Model import logic_model
    from View import view_model
    text = "Choose side!"

    dialog_window = QMessageBox()

    dialog_create(dialog_window, text)

    dialog_window.addButton(ColorDialogButton(view_model.WhiteCheckerColor),
                            QMessageBox.AcceptRole)
    dialog_window.addButton(ColorDialogButton(view_model.BlackCheckerColor),
                            QMessageBox.RejectRole)

    answer = dialog_window.exec()

    if answer == 0:
        logic_model.PlayerSide = Colors.WhiteChecker
    else:
        logic_model.PlayerSide = Colors.BlackChecker


def dialog_create(dialog_window, text):
    """Вынесены общие для всех диалоговых окон свойства"""

    dialog_window.setWindowFlag(Qt.FramelessWindowHint)
    dialog_window.setText(text)
    dialog_window.setStyleSheet(
        'background-color: rgb(219, 169, 116);'
        'color: black;'
        'font: 900 normal large "Constantia";')
    dialog_window.setMinimumSize(200, 200)


def exit_dialog_raise():
    """Вызывает диалоговое окно, если пользователь хочет закрыть игру и 
    игра сохранена"""

    question = 'Quit the game?'

    dialog_window = QMessageBox()
    dialog_create(dialog_window, question)
    dialog_window.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
    dialog_window.setDefaultButton(QMessageBox.Yes)

    answer = dialog_window.exec()

    if answer == dialog_window.Yes:
        quit_game()


def save_and_exit_dialog_raise():
    """Вызывает диалоговое окно, если пользователь закрывает игру не 
    сохранив изменения"""

    text = "Game wasn't saved."
    informative_text = 'Do you want to exit without save?'
    dialog_window = QMessageBox()

    dialog_create(dialog_window, text)
    dialog_window.setInformativeText(informative_text)
    dialog_window.setStandardButtons(QMessageBox.Yes | QMessageBox.Save
                                     | QMessageBox.Cancel)
    dialog_window.setDefaultButton(QMessageBox.Save)

    answer = dialog_window.exec()

    if answer == dialog_window.Yes:
        quit_game()
    elif answer == dialog_window.Save:
        logic.save_game()

        save_dialog_raise()
        exit_dialog_raise()


def save_dialog_raise():
    """Вызывает диалоговое окно, оповещающее об успешном сохранении игры"""

    from Model import logic_model

    logic_model.IsSaved = True
    logic_model.WasSaveInThisGame = True

    text = "Game has been saved!"
    dialog_window = QMessageBox()

    dialog_create(dialog_window, text)
    dialog_window.setStandardButtons(QMessageBox.Ok)
    dialog_window.setDefaultButton(QMessageBox.Ok)

    dialog_window.exec()
    QApplication.processEvents()


def help_window_raise():
    """Вызывается диалоговое окно с некоторыми общими сведениями о программе"""

    help_dialog = QMessageBox()
    help_text = ('If u wanna save current game, press "Save".\n'
                 'Press "New game" for restart game.\n'
                 'Click a checker to set focus, next click green or red cells '
                 'for make step.')
    dialog_create(help_dialog, help_text)

    help_dialog.exec()


def size_window_raise():
    """Вызывается диалоговое окно, предлагающее ввести пользователю размер 
    доски"""

    size, ok = QInputDialog.getInt(QApplication.desktop(), 'Border size',
                                   "Enter a border's size (since 4 to 12):",
                                   value=10, min=4, max=12, step=1)
    if ok:
        return size
    return


def game_mode_window_raise(model):

    text = 'Please, choose game mode:'
    dialog_window = QMessageBox()

    dialog_create(dialog_window, text)

    single_player_button = QPushButton('Single player')
    network_player_button = QPushButton('Network game')

    dialog_window.addButton(single_player_button,
                            QMessageBox.AcceptRole)
    dialog_window.addButton(network_player_button,
                            QMessageBox.RejectRole)

    answer = dialog_window.exec()

    if answer == 0:
        model.SinglePlayer = True
    else:
        model.NetworkGame = True


def abort_connection_window_raise():

    def save_button_actions():
        logic.save_game()
        save_dialog_raise()

        QApplication.processEvents()
        QCoreApplication.quit()

    def exit_button_action():
        abort_dialog.close()
        QApplication.processEvents()
        QCoreApplication.quit()

    text = 'Your opponent left the game.'

    abort_dialog = QMessageBox()
    dialog_create(abort_dialog, text)

    save_button = QPushButton('Save')
    save_button.clicked.connect(save_button_actions)

    exit_button = QPushButton('Exit')
    exit_button.clicked.connect(exit_button_action)

    abort_dialog.addButton(save_button, QMessageBox.AcceptRole)
    abort_dialog.addButton(exit_button, QMessageBox.AcceptRole)

    abort_dialog.exec()


def wait_opponent_window_raise(text=None):

    if not text:
        text = 'Please, wait your opponent.'

    global WaitDialog
    WaitDialog = QMessageBox()

    exit_button = QPushButton('Exit')
    exit_button.setFont(QFont('Constantia', 11))
    exit_button.clicked.connect(QCoreApplication.quit)

    WaitDialog.addButton(exit_button, QMessageBox.AcceptRole)
    WaitDialog.setWindowFlag(Qt.FramelessWindowHint)
    WaitDialog.setText(text)
    WaitDialog.setFont(QFont('Constantia', 11))
    WaitDialog.setStyleSheet('background-color: rgb(219, 169, 116);')
    WaitDialog.setMinimumSize(200, 200)

    WaitDialog.exec()


def close_wait_dialog():
    global WaitDialog
    WaitDialog.close()


def choose_opponent_search_mode():
    opponent_search_dialog = QMessageBox()
    text = 'Choose opponent search mode:'

    dialog_create(opponent_search_dialog, text)

    automatic_search_button = QPushButton('Automatic search')
    through_ip_enter_button = QPushButton('Handmade search')

    opponent_search_dialog.addButton(automatic_search_button,
                                     QMessageBox.AcceptRole)
    opponent_search_dialog.addButton(through_ip_enter_button,
                                     QMessageBox.RejectRole)

    return opponent_search_dialog.exec() == 0


def host_determine():
    determine_dialog = QMessageBox()
    text = 'Will you be host?'

    dialog_create(determine_dialog, text)

    determine_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    determine_dialog.setDefaultButton(QMessageBox.Yes)

    return determine_dialog.exec() == QMessageBox.Yes


def host_ip_enter():
    ip_address, ok = QInputDialog.getText(
        QApplication.desktop(), "Host's address", "Please, enter the host's "
                                                  "address:")

    if ok:
        return ip_address
    return
