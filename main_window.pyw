from PyQt5.QtWidgets import QGraphicsView, QApplication
from Model import logic
from View import view_methods, scene, dialog_boxes
from Controller import controller_methods, multiplayer
from pathlib import Path
import socket
import time
import sys


class MainWindow(QGraphicsView):
    def __init__(self):
        super().__init__()

        from Model import logic_model
        from View import view_model

        view_methods.view_setting(self)
        view_model.Scene = scene.Scene()
        self.setScene(view_model.Scene)

        dialog_boxes.game_mode_window_raise(logic_model)

        if logic_model.NetworkGame:
            multiplayer.MyAddress = (
                multiplayer.get_own_ip_address(), multiplayer.MainPort)

            if dialog_boxes.choose_opponent_search_mode():
                this_first_player = multiplayer.create_connection_or_server()

                if not this_first_player:
                    multiplayer.getting_and_receive_loading_data(logic_model)

                    multiplayer.view_setting_after_first_received(
                        view_model, logic_model)
                else:
                    self.main_components_set(logic_model, view_model, False)
                    QApplication.processEvents()
                    self.checkers_drop(logic_model)
                    QApplication.processEvents()

                    self.wait_thread_start(this_first_player, logic_model)

                if logic_model.PlayerSide != logic_model.Stroke:
                    self.received_thread_start(logic_model)
            else:
                if dialog_boxes.host_determine():
                    self.main_components_set(logic_model, view_model, False)
                    QApplication.processEvents()
                    self.checkers_drop(logic_model)
                    QApplication.processEvents()

                    wait_dialog_text = "Host's IP: {}\nPlease, wait your " \
                                       "opponent."\
                        .format(multiplayer.MyAddress[0])
                    self.wait_client_thread_start(wait_dialog_text)
                else:
                    multiplayer.OpponentAddress = (
                        dialog_boxes.host_ip_enter(), multiplayer.MainPort)

                    with socket.socket() as client:
                        client.connect(multiplayer.OpponentAddress)
                    receive_model_thread = multiplayer.ReceiveModelThread(
                        logic_model, True)
                    receive_model_thread.started.connect(
                        multiplayer.running_thread_flag)
                    receive_model_thread.finished.connect(
                        lambda:
                        multiplayer.view_processing_after_model_receive(True))
                    receive_model_thread.start()
                    time.sleep(1)
        else:
            self.main_components_set(logic_model, view_model, True)
            QApplication.processEvents()
            self.checkers_drop(logic_model)
            QApplication.processEvents()

            controller_methods.bot_stroke(logic_model)
        view_model.Scene.update()

    @staticmethod
    def wait_client_thread_start(text):
        from Model import logic_model
        wait_client_thread = multiplayer.WaitClientThread(logic_model)
        wait_client_thread.started.connect(
            lambda: dialog_boxes.wait_opponent_window_raise(text))
        wait_client_thread.finished.connect(dialog_boxes.close_wait_dialog)
        wait_client_thread.start()

        QApplication.processEvents()
        time.sleep(0.5)

    @staticmethod
    def set_border_size(model):
        if Path(model.SavedSingleGame).exists():
            model.Size = logic.load_game_data()[0]
        else:
            model.Size = dialog_boxes.size_window_raise()
            if not model.Size:
                quit(0)

    @staticmethod
    def set_border_matrix(model, is_single_player):
        if is_single_player:
            saved_file = model.SavedSingleGame
        else:
            saved_file = model.SavedNetworkGame

        if Path(saved_file).exists():
            logic.install_loading_data(model)
            model.NetworkGame = not is_single_player
            model.SinglePlayer = is_single_player
        else:
            model.BorderMatrix = logic.border_matrix_create(
                model.Size)
        view_methods.cells_drop(model.BorderMatrix)

    def main_components_set(self, logic_model, view_model, is_single_game):
        self.set_border_size(logic_model)
        view_methods.widgets_set(view_model, logic_model)
        self.set_border_matrix(logic_model, is_single_game)

    @staticmethod
    def checkers_drop(model):
        if not model.PlayerSide:
            dialog_boxes.color_choice_dialog_raise()
            if not model.Size:
                quit(0)
            logic.checkers_drop(model)
        view_methods.checkers_drop(model.BorderMatrix)

    @staticmethod
    def wait_thread_start(this_first_player, model):
        wait_thread = multiplayer.WaitOpponentThread(this_first_player, model)
        wait_thread.started.connect(
            dialog_boxes.wait_opponent_window_raise)
        wait_thread.finished.connect(dialog_boxes.close_wait_dialog)
        wait_thread.start()

        QApplication.processEvents()
        time.sleep(0.5)

    @staticmethod
    def received_thread_start(model):
        receive_model_thread = multiplayer.ReceiveModelThread(model)
        receive_model_thread.started.connect(multiplayer.running_thread_flag)
        receive_model_thread.finished.connect(
            multiplayer.view_processing_after_model_receive)
        receive_model_thread.start()
        time.sleep(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec())
