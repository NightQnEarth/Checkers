from PyQt5.QtWidgets import QApplication
from Model import logic
import Model.ai
from View import dialog_boxes, view_methods, view_checker
import time
from Model.colors import Colors
from Controller import multiplayer


def checker_event(obj):
    from Model import logic_model
    from View import view_model

    if logic_model.CheckerInFocus is None:
        logic.focus_on(obj.logic_checker_object)
    elif logic_model.CheckerInFocus is not obj.logic_checker_object:
        logic.focus_off()
        logic.focus_on(obj.logic_checker_object)

    view_model.Scene.update()


def cell_event(obj):
    from Model import logic_model
    from View import view_model

    end_game = False
    receive_model_thread = None

    if logic_model.CheckerInFocus:
        if ((logic_model.NetworkGame and logic_model.PlayerSide ==
             logic_model.Stroke) or (not logic_model.NetworkGame)):
            if logic_model.CheckersForBitWithChains:
                logic.chains_processing(logic_model, obj.logic_cell_object)
                logic_model.IsSaved = False
                end_game = logic.check_end_game(logic_model, [], True)
                step_flag = checkers_delete(checker_for_delete_search())
            else:
                step_flag = step_actions(logic_model, obj)
                logic_model.IsSaved = False
            if not end_game:
                logic.king_check(logic_model, obj.logic_cell_object)
                logic.focus_off()
                if logic_model.NetworkGame and \
                        logic_model.CheckersForBitWithChains and step_flag:
                    multiplayer.send_model(logic_model)
                logic.chains_create(logic_model)

            if logic_model.NetworkGame and step_flag:
                if logic_model.PlayerSide != logic_model.Stroke:
                    multiplayer.send_model(logic_model)
                    receive_model_thread = multiplayer.ReceiveModelThread(
                        logic_model)
                    receive_model_thread.started.connect(
                        multiplayer.running_thread_flag)
                    receive_model_thread.finished.connect(
                        multiplayer.view_processing_after_model_receive)
                    receive_model_thread.start()

    if end_game:
        dialog_boxes.win_dialog_raise(end_game)
    else:
        end_game = bot_stroke(logic_model)

        if logic_model.NetworkGame and logic_model.PlayerSide != \
                logic_model.Stroke:
            if logic_model.CheckerInFocus:
                logic.focus_off()

        view_model.Scene.update()
        QApplication.processEvents()

        if end_game:
            dialog_boxes.win_dialog_raise(end_game)
    if logic_model.NetworkGame and receive_model_thread and \
            receive_model_thread.isRunning():
        time.sleep(1)


def step_actions(model, cell):
    """Осуществляет ход шашки без атаки шашек противника"""

    cells_for_step = set()

    for chain in logic.possible_cells_for_steps_or_hit(model.CheckerInFocus):
        for _cell in chain:
            cells_for_step.add(_cell)

    if not logic.check_end_game(model, cells_for_step):
        if model.Stroke == model.CheckerInFocus.color \
                and cell.logic_cell_object in cells_for_step:
            model.CheckerInFocus.cell.checker_stay = None
            model.CheckerInFocus.cell = cell.logic_cell_object
            cell.logic_cell_object.checker_stay = model.CheckerInFocus
            logic.switch_color(model)
            return True

    return


def checkers_delete(checker):
    """Удаления графического объекта шашки со сцены"""

    if checker:
        from View import view_model

        view_model.Bin.add(checker)
        view_model.Scene.removeItem(checker)
        return True
    return


def bot_stroke(model):
    """Решает, передать ли ход боту и, если передаёт, то совершает этот ход"""

    from View import view_model
    won_side = None
    single_player_flag = False
    while model.SinglePlayer and model.Stroke != model.PlayerSide:
        update_and_sleep(view_model.Scene)
        won_side = Model.ai.ai(model)

        while checker_for_delete_search():
            checkers_delete(checker_for_delete_search())

        single_player_flag = True
        view_model.Scene.update()

        if won_side:
            return won_side

    if single_player_flag and not won_side:
        logic.chains_create(model)


def checker_for_delete_search():
    from View import view_model
    from View import view_checker
    from Model import logic_model

    for item in view_model.Scene.items():
        if isinstance(item, view_checker.Checker) and \
                item.logic_checker_object not in logic_model.CheckersSet:
            return item
    return


def update_and_sleep(scene):
    """Перерисовывает сцену и блокирует программу на некоторое время"""

    scene.update()
    QApplication.processEvents()
    time.sleep(0.5)


def new_game_create():
    """Начинает игру заново"""

    from Model import logic_model
    from View import view_model

    for item in view_model.Scene.items():
        if isinstance(item, view_checker.Checker):
            checkers_delete(item)

    for checker in logic_model.CheckersSet:
        checker.cell.checker_stay = None

    logic_model.CheckersSet = set()
    logic_model.CheckerInFocus = None
    logic_model.Stroke = Colors.WhiteChecker
    logic_model.CheckersForBitWithChains = {}

    logic_model.PlayerSide = None

    logic_model.IsSaved = False

    dialog_boxes.color_choice_dialog_raise()

    logic.checkers_drop(logic_model)
    view_methods.checkers_drop(logic_model.BorderMatrix)

    view_model.Scene.update()

    bot_stroke(logic_model)
