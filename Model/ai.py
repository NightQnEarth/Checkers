import random
from Model import logic


def ai(model):
    """Бот"""

    if model.CheckersForBitWithChains:
        checker = random.choice(list(model.CheckersForBitWithChains.keys()))

        _cell = model.CheckersForBitWithChains[checker][0][0]

        logic.focus_on(checker)
        cell = model.BorderMatrix[logic.row(_cell)][logic.column(_cell)]
        logic.chains_processing(model, _cell)

        model.IsSaved = False

        won_side = logic.check_end_game(model, [], True)

        if not won_side:
            logic.king_check(model, cell)
            logic.focus_off()
        else:
            return won_side
    else:
        checkers_for_step = {}
        checkers_for_step_set_filling(checkers_for_step, model)

        model.IsSaved = False

        won_side = logic.check_end_game(model, checkers_for_step)

        if not won_side:
            bot_step_create(model, checkers_for_step)
        else:
            return won_side


def checkers_for_step_set_filling(checkers_for_step, model):
    """Заполнение словаря шашка - цепь клеток"""

    for _checker in model.CheckersSet:
        if _checker.color != model.PlayerSide:
            logic.focus_on(_checker)
            chains = logic.possible_cells_for_steps_or_hit(_checker)

            if chains:
                checkers_for_step[_checker] = chains
            logic.focus_off()


def bot_step_create(model, checkers_for_step):
    """Осуществляется ход произвольной из доступных шашек"""

    checker = random.choice(list(checkers_for_step.keys()))

    logic.focus_on(checker)

    cell_for_step = random.choice(checkers_for_step[checker])[0]

    model.CheckerInFocus.cell.checker_stay = None
    model.CheckerInFocus.cell = cell_for_step
    cell_for_step.checker_stay = model.CheckerInFocus

    logic.king_check(model, cell_for_step)

    logic.focus_off()

    logic.switch_color(model)
