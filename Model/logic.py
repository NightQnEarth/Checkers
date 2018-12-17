import itertools
import pickle
from pathlib import Path
import Model.checker
from Model.colors import Colors
import Model.cell


def chains_create(model):
    """Производится заполнения словаря шашка - цепь"""

    if not model.CheckersForBitWithChains:
        max_chain_length = 1
        for checker in model.CheckersSet:
            if checker.color == model.Stroke:
                for chain in possible_cells_for_steps_or_hit(checker, True):
                    if len(chain) > max_chain_length:
                        max_chain_length = len(chain)
                        model.CheckersForBitWithChains.clear()
                        model.CheckersForBitWithChains.setdefault(
                            checker, []).append(chain)
                    elif len(chain) == max_chain_length:
                        model.CheckersForBitWithChains.setdefault(
                            checker, []).append(chain)


def return_result(result_copies, border_matrix):
    result = []

    for _chain in result_copies:
        temporary = []
        for _copy_cell in _chain:
            temporary.append(
                border_matrix[row(_copy_cell)][column(_copy_cell)])
        if temporary:
            result.append(temporary)

    return result


def return_max_chains(result):
    """Возвращает максимально длинные цепи"""

    max_chain_length = 0
    max_chains = []

    for _chain in result:
        if len(_chain) > max_chain_length:
            max_chain_length = len(_chain)
            max_chains.clear()

        if len(_chain) >= max_chain_length:
            max_chains.append(_chain)

    return max_chains


def chains_filter_for_simple_checkers(checker, chains, hit_flag=False):

    def condition(_source_cell, _next_cell):
        return not(
            (abs(_source_cell.border_coordinates[1] -
                 _next_cell.border_coordinates[1]) == 4
             and _source_cell.border_coordinates[0] ==
             _next_cell.border_coordinates[0])
            or (abs(ord(_source_cell.border_coordinates[0]) -
                    ord(_next_cell.border_coordinates[0])) == 4
                and _source_cell.border_coordinates[1] ==
                _next_cell.border_coordinates[1])
            or abs(_source_cell.border_coordinates[1] -
                   _next_cell.border_coordinates[1]) == 2)

    from Model import logic_model

    result = []

    if hit_flag:
        for chain in chains:
            flag = True
            if condition(checker.cell, chain[0]):
                flag = False

            i = 1
            while i < len(chain):
                if condition(chain[i-1], chain[i]):
                    flag = False
                i += 1

            if flag:
                result.append(chain)
    else:
        for chain in chains:
            for cell in chain:
                dif = checker.cell.border_coordinates[1] - \
                             cell.border_coordinates[1]
                if checker.color == logic_model.PlayerSide and dif == -1 or \
                   checker.color != logic_model.PlayerSide and dif == 1:
                        result.append(chain)
    return result


def switch_color(model):
    """Меняет сторону, которая сейчас ходит"""

    model.Stroke = Colors.BlackChecker \
        if model.Stroke == Colors.WhiteChecker else Colors.WhiteChecker


def checkers_drop(model):
    """Расставляет шашки по клеткам, находящимся в матрице"""

    def checker_create(color, i, j):
        checker = Model.checker.Checker(color, model.BorderMatrix[i][j])
        model.BorderMatrix[i][j].checker_stay = checker
        model.CheckersSet.add(checker)

    rows_count = 4
    if model.Size == 4:
        rows_count = 1
    elif model.Size < 8:
        rows_count = 2
    elif model.Size < 10:
        rows_count = 3
    elif model.Size == 12:
        rows_count = 5

    for i in range(model.Size):
        for j in range(model.Size):
            if model.BorderMatrix[i][j].color == Colors.BlackCell:
                if 1 <= i + 1 <= rows_count:
                    checker_create(Colors.BlackChecker
                                   if model.PlayerSide != Colors.BlackChecker
                                   else Colors.WhiteChecker, i, j)
                elif model.Size - rows_count + 1 <= i + 1 <= model.Size:
                    checker_create(model.PlayerSide, i, j)


def some_logic_actions(chain_copy, cell, checker_copy, border_matrix_copy,
                       helper, hit_flag, result_copies):
    """Ряд логических действий, связанных с перемещением шашки на новую 
    позицию во время удара, удалением срубленной шашки и рекурсивным 
    вызовом helper"""

    cell_with_dead_checker = checker_for_delete_search(
        checker_copy.cell, cell, border_matrix_copy,
        True)

    deleted_checker = cell_with_dead_checker.checker_stay
    cell_with_dead_checker.checker_stay = None

    checker_copy.cell.checker_stay = None
    border_matrix_copy[
            len(border_matrix_copy) - checker_copy.cell.border_coordinates[
                1]][column(checker_copy.cell)].checker_stay = None

    checker_copy.cell = cell
    cell.checker_stay = checker_copy

    helper(checker_copy, border_matrix_copy, chain_copy, result_copies,
           hit_flag)

    cell_with_dead_checker.checker_stay = deleted_checker
    border_matrix_copy[
        len(border_matrix_copy) - checker_copy.cell.border_coordinates[1]][
        column(checker_copy.cell)].checker_stay = None


def copies_create(border_matrix_copy, chain_copy,
                  border_matrix, checker, chain):
    """Создаёт копии ряда объектов и возвращает копию шашки"""

    for _list in border_matrix:
        _row = []
        border_matrix_copy.append(_row)
        for _c in _list:
            _row.append(cell_copy(_c))

    for i in chain:
        chain_copy.append(cell_copy(i))

    return checker_c(checker)


def cell_copy(_c):
    """Создаёт копию клетки"""

    result = Model.cell.Cell(_c.color, _c.border_coordinates)
    result.checker_stay = _c.checker_stay
    return result


def checker_c(_checker):
    """Создаёт копию шашки"""
    result = Model.checker.Checker(_checker.color, cell_copy(_checker.cell))
    result.isKing = _checker.isKing
    return Model.checker.Checker(_checker.color, cell_copy(_checker.cell))


def row(cell):
    """Возвращает координату клетки по оси i в матрице"""
    from Model import logic_model
    return len(logic_model.BorderMatrix) - cell.border_coordinates[1]


def column(cell):
    """Возвращает координату клетки по оси j в матрице"""

    return ord(cell.border_coordinates[0]) - ord('a')


def possible_cells_for_steps_or_hit(checker_in_focus, hit_flag=False):
    """Возвращает список списков доступных для хода дамки"""

    from Model import logic_model

    def helper(checker_in_focus, border_matrix, chain,
               result_copies, hit_flag):
        """Отдельный метод для организации рекурсии"""

        def line_search(source_row, source_column, i_step, j_step,
                        _border_matrix, shift=False):
            """Возвращает список свободных клеток в определённых деагонале или
            ряде начиная с данной позиции"""

            empty_cells = []
            i = source_row + i_step
            j = source_column + j_step
            if shift:
                if 0 <= i < len(_border_matrix) and \
                    0 <= j < len(_border_matrix) and \
                    _border_matrix[i][j].checker_stay and \
                    _border_matrix[i][j].checker_stay.color == \
                        checker_in_focus.color:
                    return []
                i = i + i_step
                j = j + j_step
            while 0 <= i < len(_border_matrix) and 0 <= j < len(
                    _border_matrix):
                if not _border_matrix[i][j].checker_stay:
                    empty_cells.append(_border_matrix[i][j])
                    i = i + i_step
                    j = j + j_step
                elif _border_matrix[i][j].checker_stay.color != \
                        _border_matrix[source_row][
                            source_column].checker_stay:
                    break
                else:
                    return []

            return empty_cells

        def search(func, i_step, j_step, _border_matrix):
            """Возвращает список клеток, в которые можно переместиться после 
            съедания шашки"""

            cells_list = func(
                len(_border_matrix) -
                checker_in_focus.cell.border_coordinates[1],
                column(checker_in_focus.cell), i_step, j_step, _border_matrix)

            if cells_list:
                cell = cells_list.pop()
                cells_set = \
                    set(func(
                        len(_border_matrix) - cell.border_coordinates[1],
                        column(cell), i_step, j_step, _border_matrix, True))
            else:
                cells_set = set(func(
                    len(_border_matrix) -
                    checker_in_focus.cell.border_coordinates[1],
                    column(checker_in_focus.cell),
                    i_step, j_step, _border_matrix, True))
            return cells_set

        if not hit_flag:
            cells = itertools.chain(
                    *[line_search(row(checker_in_focus.cell),
                                  column(checker_in_focus.cell), i, j,
                                  border_matrix)
                      for i in [-1, 1] for j in [-1, 1]]
                )

            for cell in cells:
                result.append([cell])
        else:
            border_matrix_copy = []
            chain_copy = []
            checker_copy = copies_create(
                border_matrix_copy, chain_copy,
                border_matrix, checker_in_focus,
                chain)

            cells_for_hit = \
                itertools.chain(
                    *[search(line_search, i, j, border_matrix_copy)
                      for i in [-1, 1] for j in [-1, 1]],
                    search(line_search, 2, 0, border_matrix_copy),
                    search(line_search, -2, 0, border_matrix_copy),
                    search(line_search, 0, 2, border_matrix_copy),
                    search(line_search, 0, -2, border_matrix_copy))

            for cell in cells_for_hit:
                chain_copy.append(cell)
                some_logic_actions(chain_copy, cell, checker_copy,
                                   border_matrix_copy,
                                   helper, hit_flag, result_copies)

                checker_copy = checker_c(checker_in_focus)
                chain_copy.pop()

            result_copies.append(chain_copy)

    chain = []
    result_copies = []
    result = []

    helper(checker_in_focus, logic_model.BorderMatrix, chain,
           result_copies, hit_flag)

    if hit_flag:
        result = return_result(result_copies, logic_model.BorderMatrix)

    if not checker_in_focus.isKing:
        result = chains_filter_for_simple_checkers(checker_in_focus, result,
                                                   hit_flag)

    return return_max_chains(result)


def focus_on(checker):
    """Устанавливает фокус на шашку"""

    from Model import logic_model

    checker.inFocus = True
    logic_model.CheckerInFocus = checker


def focus_off():
    """Снимает фокус с шашки"""

    from Model import logic_model

    logic_model.CheckerInFocus.inFocus = False
    logic_model.CheckerInFocus = None


def checker_for_delete_search(source_cell, next_cell, border_matrix,
                              flag=None):
    """Возвращает шашку (или, при включённом флаге, клетку) которую можно 
    срубить при переходе из начальной позиции в конечную"""

    i = row(source_cell)
    j = column(source_cell)
    next_cell_row = row(next_cell)
    next_cell_column = column(next_cell)
    row_step = 1
    column_step = 1

    if next_cell_row < i:
        row_step = -1
    elif next_cell_row == i:
        row_step = 0
    if next_cell_column < j:
        column_step = -1
    elif next_cell_column == j:
        column_step = 0

    def return_lam(i, j, m):
        return m[i][j] if flag else m[i][j].checker_stay

    def search(iterator, i, j, stop, inc_i, inc_j):
        while iterator != stop:
            iterator += max(inc_i, inc_j)
            i += inc_i
            j += inc_j
            if border_matrix[i][j].checker_stay:
                return return_lam(i, j, border_matrix)

    if row_step == 0:
        return search(j, i, j, next_cell_column, 0, column_step)
    elif column_step == 0:
        return search(i, i, j, next_cell_row, row_step, 0)
    else:
        return search(i, i, j, next_cell_row, row_step, column_step)


def border_matrix_create(checkers_border_size):
    """Возвращает матрицу tuple-ов, содержащих цвет и координаты каждой 
    клетки"""

    from Model import logic_model

    border_matrix = []
    for i in range(checkers_border_size):
        temporary = []
        for j in range(checkers_border_size):
            border_coordinates = (chr(ord(logic_model.BeginGraduationLetter)
                                      + j),
                                  checkers_border_size - i)
            color = Colors.WhiteCell if (i + j) % 2 == 0 else Colors.BlackCell

            temporary.append(Model.cell.Cell(color, border_coordinates))
        border_matrix.append(temporary)

    return border_matrix


def save_game():
    """Сохраняет слепок игры в файл"""

    from Model import logic_model

    if logic_model.NetworkGame:
        path_to_file = Path(logic_model.SavedNetworkGame)
    else:
        path_to_file = Path(logic_model.SavedSingleGame)
    path_to_file.touch()

    data = data_for_pickle_create(logic_model)

    with path_to_file.open(mode='wb') as file:
        pickle.dump(data, file)


def load_game_data():
    """Загружает слепок игры из загрузочного файла"""

    from Model import logic_model

    if logic_model.NetworkGame:
        path_to_file = Path(logic_model.SavedNetworkGame)
    else:
        path_to_file = Path(logic_model.SavedSingleGame)

    with path_to_file.open(mode='rb') as file:
        return pickle.load(file)


def data_for_pickle_create(model):
    """Возвращает данные, подготовленные для сохранения в загрузочный файл"""

    if model.CheckerInFocus:
        model.CheckerInFocus.inFocus = False

    result = list()

    result.append(model.Size)
    result.append(model.Stroke)
    result.append(model.PlayerSide)
    result.append(model.SinglePlayer)
    result.append(model.BorderMatrix)
    result.append(model.CheckersSet)
    result.append(model.CheckersForBitWithChains)

    if model.NetworkGame and model.PlayerSide == model.Stroke:
        result.append(model.CheckersForBitWithChains)
    else:
        result.append({})

    return result


def install_loading_data(model):
    """Устанавливаем в модель загруженные данные"""

    if model.NetworkGame:
        path_to_file = Path(model.SavedNetworkGame)
    else:
        path_to_file = Path(model.SavedSingleGame)

    with path_to_file.open(mode='rb') as file:
        data = pickle.load(file)

    model.Size = data[0]
    model.Stroke = data[1]
    model.PlayerSide = data[2]
    model.SinglePlayer = data[3]
    model.BorderMatrix = data[4]
    model.CheckersSet = data[5]
    model.CheckersForBitWithChains = data[6]


def chains_processing(model, cell):
    """Производится обработка словаря "шашка-цепь" и удаление шашки, 
    если это требуется"""

    if model.CheckerInFocus in model.CheckersForBitWithChains:
        cell_in_the_chain_flag = False
        chains = []
        for chain in (model.CheckersForBitWithChains[
                          model.CheckerInFocus]):
            chains.append(chain)

        for chain in chains:
            if chain[0] == cell:
                cell_in_the_chain_flag = True
                break

        if cell_in_the_chain_flag:
            keys_to_del_set = set(model.CheckersForBitWithChains.keys())
            keys_to_del_set.remove(model.CheckerInFocus)
            for _key in keys_to_del_set:
                del model.CheckersForBitWithChains[_key]

            for chain in (model.CheckersForBitWithChains[
                              model.CheckerInFocus]):
                if chain[0] != cell:
                    chain.clear()
                else:
                    chain.pop(0)

            while [] in (model.CheckersForBitWithChains[
                             model.CheckerInFocus]):
                model.CheckersForBitWithChains[
                    model.CheckerInFocus].remove([])

            if not model.CheckersForBitWithChains[model.CheckerInFocus]:
                del model.CheckersForBitWithChains[model.CheckerInFocus]

            hit_actions(model, cell)


def hit_actions(model, cell):
    """Ряд действий связанных с перемещением шашки во время удара, удалением 
    срубленной шашки и передачей хода противнику"""

    dead_checker = checker_for_delete_search(
        model.CheckerInFocus.cell,
        cell,
        model.BorderMatrix)
    model.CheckerInFocus.cell.checker_stay = None
    model.CheckerInFocus.cell = cell
    cell.checker_stay = model.CheckerInFocus
    dead_checker.cell.checker_stay = None
    model.CheckersSet.remove(dead_checker)

    if not model.CheckersForBitWithChains:
        switch_color(model)


def check_end_game(model, available_set, checkers_are_over=False):
    """Возвращает цвет победившей стороны, если игра закончена и False в 
    противном случае"""

    if not available_set and not checkers_are_over:
        flag = False
        for checker in model.CheckersSet:
            if model.Stroke != checker.color:
                flag = checker.color
                break
        win_side = model.CheckerInFocus.color if not flag else flag

        return win_side
    elif checkers_are_over:
        for checker in model.CheckersSet:
            if model.Stroke == checker.color:
                return False
        win_side = Colors.BlackChecker if model.Stroke == Colors.WhiteChecker \
            else Colors.WhiteChecker

        return win_side
    return False


def king_check(model, cell):
    """Проверяет, можно ли сделать шашку, находящуюся в фокусе, дамкой и, 
    если можно, делает"""

    if (not model.CheckersForBitWithChains and
            cell.checker_stay and
            cell.checker_stay == model.CheckerInFocus and
            ((model.CheckerInFocus.color == model.PlayerSide and
             cell.border_coordinates[1] == model.Size) or (
                            model.CheckerInFocus.color != model.PlayerSide
             and cell.border_coordinates[1] == 1))):
        model.CheckerInFocus.isKing = True


def turn_matrix(model):
    """Осуществляется разворот доски"""

    turned_cells = set()
    for i in range(len(model.BorderMatrix)):
        for j in range(len(model.BorderMatrix[i])):
            if model.BorderMatrix[i][j] not in turned_cells and \
                    model.BorderMatrix[i][j].checker_stay:
                temporary = model.BorderMatrix[i][j].checker_stay
                model.BorderMatrix[i][j].checker_stay = model.BorderMatrix[
                    model.Size - i - 1][model.Size - j - 1].checker_stay

                if model.BorderMatrix[i][j].checker_stay:
                    model.BorderMatrix[i][j].checker_stay.cell = \
                        model.BorderMatrix[i][j]

                model.BorderMatrix[
                    model.Size - i - 1][model.Size - j - 1].checker_stay = \
                    temporary
                temporary.cell = model.BorderMatrix[model.Size - i - 1][
                    model.Size - j - 1]

                turned_cells.add(model.BorderMatrix[i][j])
                turned_cells.add(model.BorderMatrix[model.Size - i - 1][
                                     model.Size - j - 1])
