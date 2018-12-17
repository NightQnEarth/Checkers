import unittest
from Model import *


class LogicTests(unittest.TestCase):

    def setUp(self):
        logic_model.Size = 10
        logic_model.CheckersSet = set()
        logic_model.CheckerInFocus = None
        logic_model.Stroke = colors.Colors.WhiteChecker
        logic_model.CheckersForBitWithChains = {}

        logic_model.PlayerSide = None
        logic_model.SinglePlayer = True

        logic_model.IsSaved = False

        logic_model.BorderMatrix = logic.border_matrix_create(
            logic_model.Size)

    def test_king_check(self):
        logic_model.PlayerSide = colors.Colors.WhiteChecker

        logic_model.BorderMatrix[0][1].checker_stay = checker.Checker(
            colors.Colors.WhiteChecker, logic_model.BorderMatrix[0][1])

        _cell = logic_model.BorderMatrix[0][1]

        logic_model.CheckerInFocus = _cell.checker_stay
        logic_model.CheckerInFocus.inFocus = True

        logic.king_check(logic_model, _cell)

        self.assertTrue(_cell.checker_stay.isKing)

    def test_chains_create(self):
        logic_model.PlayerSide = colors.Colors.WhiteChecker

        logic_model.BorderMatrix[6][5].checker_stay = checker.Checker(
            colors.Colors.WhiteChecker, logic_model.BorderMatrix[6][5])
        white_checker = logic_model.BorderMatrix[6][5].checker_stay
        logic_model.BorderMatrix[5][6].checker_stay = checker.Checker(
            colors.Colors.BlackChecker, logic_model.BorderMatrix[5][6])
        black_checker = logic_model.BorderMatrix[5][6].checker_stay
        logic_model.CheckersSet.add(white_checker)
        logic_model.CheckersSet.add(black_checker)

        logic.chains_create(logic_model)

        self.assertIn(white_checker,
                      logic_model.CheckersForBitWithChains.keys())

        self.assertEqual(logic_model.CheckersForBitWithChains[white_checker],
                         [[logic_model.BorderMatrix[4][7]]])

        logic_model.CheckersForBitWithChains.clear()
        white_checker.isKing = True
        logic.chains_create(logic_model)

        self.assertIn(white_checker,
                      logic_model.CheckersForBitWithChains.keys())
        self.assertIn([logic_model.BorderMatrix[4][7]],
                      logic_model.CheckersForBitWithChains[
                             white_checker])
        self.assertIn([logic_model.BorderMatrix[3][8]],
                      logic_model.CheckersForBitWithChains[
                          white_checker])
        self.assertIn([logic_model.BorderMatrix[2][9]],
                      logic_model.CheckersForBitWithChains[
                          white_checker])
        self.assertEqual(len(logic_model.CheckersForBitWithChains[
                                 white_checker]), 3)

    def test_switch_color(self):
        logic.switch_color(logic_model)

        self.assertEqual(logic_model.Stroke, colors.Colors.BlackChecker)

    def test_checkers_drop(self):
        logic_model.Size = 4
        logic_model.PlayerSide = colors.Colors.WhiteChecker

        logic.checkers_drop(logic_model)

        self.assertEqual(len(logic_model.CheckersSet), 4)

        self.assertEqual(logic_model.BorderMatrix[0][1].checker_stay.color,
                         colors.Colors.BlackChecker)
        self.assertEqual(logic_model.BorderMatrix[0][3].checker_stay.color,
                         colors.Colors.BlackChecker)
        self.assertEqual(logic_model.BorderMatrix[3][0].checker_stay.color,
                         colors.Colors.WhiteChecker)
        self.assertEqual(logic_model.BorderMatrix[3][2].checker_stay.color,
                         colors.Colors.WhiteChecker)

    def test_focus(self):
        _checker = checker.Checker(
            colors.Colors.WhiteChecker, logic_model.BorderMatrix[0][1])
        logic_model.BorderMatrix[0][1].checker_stay = _checker

        logic.focus_on(_checker)

        self.assertIs(logic_model.CheckerInFocus, _checker)

        logic.focus_off()

        self.assertIsNone(logic_model.CheckerInFocus)

    def test_checker_for_delete_search(self):
        next_cell = logic_model.BorderMatrix[0][5]
        source_cell = logic_model.BorderMatrix[4][5]

        source_cell.checker_stay = checker.Checker(
            colors.Colors.WhiteChecker, source_cell)
        logic_model.BorderMatrix[2][5].checker_stay = checker.Checker(
            colors.Colors.BlackChecker, source_cell)

        self.assertIs(logic.checker_for_delete_search(
            source_cell, next_cell, logic_model.BorderMatrix),
            logic_model.BorderMatrix[2][5].checker_stay)

    def test_bot_step(self):
        logic_model.Size = 4
        logic_model.Stroke = colors.Colors.WhiteChecker
        logic_model.PlayerSide = colors.Colors.BlackChecker
        logic_model.BorderMatrix = logic.border_matrix_create(
            logic_model.Size)
        logic.checkers_drop(logic_model)

        ai.ai(logic_model)

        if logic_model.BorderMatrix[1][0].checker_stay is None and \
                logic_model.BorderMatrix[1][2].checker_stay is None:
            print('!')

        self.assertTrue(logic_model.BorderMatrix[1][0].checker_stay or
                        logic_model.BorderMatrix[1][2].checker_stay)

    def test_bot_final_hit(self):
        logic_model.Size = 4
        logic_model.Stroke = colors.Colors.BlackChecker
        logic_model.PlayerSide = colors.Colors.WhiteChecker

        _checker_first = checker.Checker(
            colors.Colors.BlackChecker, logic_model.BorderMatrix[0][1])
        _checker_second = checker.Checker(
            colors.Colors.WhiteChecker, logic_model.BorderMatrix[1][2])

        logic_model.CheckersSet.add(_checker_first)
        logic_model.CheckersSet.add(_checker_second)
        logic_model.CheckerInFocus = _checker_first
        _checker_first.inFocus = True

        logic_model.BorderMatrix[0][1].checker_stay = _checker_first
        logic_model.BorderMatrix[1][2].checker_stay = _checker_second

        logic.chains_create(logic_model)

        self.assertEqual(ai.ai(logic_model), colors.Colors.BlackChecker)

        self.assertIsNone(logic_model.BorderMatrix[1][2].checker_stay)
        self.assertIs(logic_model.BorderMatrix[2][3].checker_stay,
                      _checker_first)


if __name__ == '__main__':
    unittest.main()
