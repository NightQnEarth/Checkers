import socket
import pickle
import time
import select
from Model import logic
from View import dialog_boxes, view_methods
import View
import Controller
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
from Model import colors


MainPort = 16180
BroadcastPort = 40000
OpponentAddress = ('', MainPort)
MyAddress = None
SecondPlayerGreeting = b'Hello from second player!'


class WaitClientThread(QThread):
    def __init__(self, model):
        super().__init__()

        self.model = model

    def run(self):
        with socket.socket() as server:
            server.bind(('', MainPort))
            server.listen(1)
            sender_socket, sender_address = server.accept()

            global OpponentAddress
            OpponentAddress = (sender_address[0], MainPort)

        logic.turn_matrix(self.model)
        data = logic.data_for_pickle_create(self.model)
        pickled_data = pickle.dumps(data)
        logic.turn_matrix(self.model)

        with socket.socket() as server:
            server.connect(OpponentAddress)
            time.sleep(2)
            server.sendall(pickled_data)


class WaitOpponentThread(QThread):
    def __init__(self, server, model):
        super().__init__()

        self.server = server
        self.model = model

    def run(self):
        logic.turn_matrix(self.model)
        loading_data = pickle.dumps(logic.data_for_pickle_create(self.model))
        logic.turn_matrix(self.model)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) \
                as broadcast_server:
            broadcast_server.setsockopt(
                socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            broadcast_server.bind(('', MainPort))

            data = None
            while data != b'Am i server?':
                data = broadcast_server.recv(1024)

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as \
                    broadcast_client:
                broadcast_client.setsockopt(socket.SOL_SOCKET,
                                            socket.SO_BROADCAST, 1)
                broadcast_client.connect(('255.255.255.255', BroadcastPort))
                time.sleep(2)
                broadcast_client.sendall(b'No')

            sender_socket, sender_address = self.server.accept()
            global OpponentAddress
            OpponentAddress = (sender_address[0], MainPort)
            sender_socket.sendall(loading_data)
            sender_socket.close()

        self.server.close()


class ReceiveModelThread(QThread):
    def __init__(self, logic_model, is_first_time=False):
        super().__init__()

        self.logic_model = logic_model
        self.is_first_time = is_first_time

    def run(self):
        received_model = None

        with receiver_socket_open() as server:
            read_list = [server]
            while True:
                ready_to_read, _, _ = select.select(read_list, [], [], 1)

                break_flag = False

                for ready_server in ready_to_read:
                    with ready_server.accept()[0] as sender_socket:
                        received_model = None
                        while not received_model:
                            received_model = receive(sender_socket)
                    break_flag = True

                if break_flag:
                    break

        if received_model == b'I left.':
            self.logic_model.ReceivedThreadIsRunning = False
            dialog_boxes.abort_connection_window_raise()
            QApplication.processEvents()
        else:
            data = pickle.loads(received_model)

            self.logic_model.Stroke = data[1]
            self.logic_model.SinglePlayer = data[3]
            self.logic_model.BorderMatrix = data[4]
            self.logic_model.CheckersSet = data[5]
            self.logic_model.CheckersForBitWithChains.clear()

            if self.is_first_time:
                self.logic_model.Size = data[0]
                self.logic_model.PlayerSide = colors.Colors.BlackChecker if \
                    data[2] == colors.Colors.WhiteChecker \
                    else colors.Colors.WhiteChecker


def get_own_ip_address():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.connect(('1.1.1.1', 1))
        return client.getsockname()[0]


def create_connection_or_server():

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as _socket:
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        _socket.connect(('255.255.255.255', MainPort))
        _socket.sendall(b'Am i server?')

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as broadcast_server:
        global OpponentAddress
        broadcast_server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_server.bind(('', BroadcastPort))
        broadcast_server.settimeout(3)
        try:
            OpponentAddress = (broadcast_server.recvfrom(1024)[1][0], MainPort)
            return
        except socket.timeout:
            return receiver_socket_open()


def receiver_socket_open():
    server = socket.socket()

    while True:
        try:
            server.bind(OpponentAddress)
            break
        except socket.error as e:
            if e.errno == 10048:
                pass
            else:
                raise e
    server.listen(1)

    return server


def receive(sender_socket):
    result = b''
    while True:
        data = sender_socket.recv(1024)
        if not data:
            break
        result += data

    return result


def send_model(model):
    try:
        with socket.socket() as sender_socket:
            sender_socket.settimeout(3)
            sender_socket.connect(OpponentAddress)
            logic.turn_matrix(model)
            data_for_pickle = logic.data_for_pickle_create(model)
            pickled_data = pickle.dumps(data_for_pickle)
            logic.turn_matrix(model)
            sender_socket.sendall(pickled_data)
    except OSError:
        dialog_boxes.abort_connection_window_raise()


def view_processing_after_model_receive(is_first_receive=False):
    from Model import logic_model
    from View import view_model

    if is_first_receive:
        view_setting_after_first_received(view_model, logic_model)

    logic.chains_create(logic_model)

    for item in View.view_model.Scene.items():
        if isinstance(item, View.view_checker.Checker) or isinstance(
                item, View.view_cell.Cell):
            Controller.controller_methods.checkers_delete(item)

    View.view_methods.cells_drop(logic_model.BorderMatrix)
    View.view_methods.checkers_drop(logic_model.BorderMatrix)

    QApplication.processEvents()

    end_game = logic.check_end_game(logic_model, [], True)
    if end_game:
        dialog_boxes.win_dialog_raise(end_game)

    logic_model.ReceivedThreadIsRunning = False

    if logic_model.Stroke != logic_model.PlayerSide:
        receive_model_thread = ReceiveModelThread(logic_model)
        receive_model_thread.started.connect(running_thread_flag)
        receive_model_thread.finished.connect(
            view_processing_after_model_receive)
        receive_model_thread.start()
        time.sleep(1)


def view_setting_after_first_received(view_model, logic_model):
    view_methods.widgets_set(view_model, logic_model)
    view_methods.cells_drop(logic_model.BorderMatrix)
    view_methods.checkers_drop(logic_model.BorderMatrix)
    QApplication.processEvents()


def running_thread_flag():

    from Model import logic_model

    logic_model.ReceivedThreadIsRunning = True


def getting_and_receive_loading_data(logic_model):

    with socket.socket() as client:
        client.connect(OpponentAddress)
        data = pickle.loads(receive(client))

    logic_model.Size = data[0]
    logic_model.Stroke = data[1]

    logic_model.PlayerSide = colors.Colors.BlackChecker if \
        data[2] == colors.Colors.WhiteChecker \
        else colors.Colors.WhiteChecker

    logic_model.SinglePlayer = data[3]
    logic_model.BorderMatrix = data[4]
    logic_model.CheckersSet = data[5]
    logic_model.CheckersForBitWithChains = data[6]
