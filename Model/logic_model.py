from Model.colors import Colors

Size = None
BorderMatrix = None

CheckersSet = set()
CheckerInFocus = None
Stroke = Colors.WhiteChecker
CheckersForBitWithChains = {}
BeginGraduationLetter = 'a'

PlayerSide = None
SinglePlayer = False
NetworkGame = False
ReceivedThreadIsRunning = False

SavedNetworkGame = 'SavedNetworkGame.txt'
SavedSingleGame = 'SavedSingleGame.txt'
IsSaved = False
WasSaveInThisGame = False
