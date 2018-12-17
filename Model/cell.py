class Cell:
    def __init__(self, color, border_coordinates):
        self.color = color
        self.border_coordinates = border_coordinates
        self.checker_stay = None
