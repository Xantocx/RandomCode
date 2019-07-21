import numpy as np

class TTTPlayer(object):

	def __init__(self, displaySymbol):
		self.__displaySymbol = displaySymbol
		self.__isValidPlayer = True

	@property
	def displaySymbol(self):
		return self._displaySymbol

	@displaySymbol.setter
	def displaySymbol(self, displaySymbol):
		self.__displaySymbol = displaySymbol

	@property
	def isValidPlayer(self):
		return self._isValidPlayer

	@isValidPlayer.setter
	def isValidPlayer(self, boolean):
		self.__isValidPlayer = boolean

	def doTurn(self, game):
		row = int(input("Please enter the row: "))
		col = int(input("Please enter the column: "))

		game.placeAt((row, col))

	def invalidSet(self, game, position):
		self.doTurn(game)

	def win(self):
		pass

	def draw(self):
		pass

	def lose(self):
		pass


class TTTNullPlayer(TTTPlayer):

	def __init__(self):
		super().__init__(" ")

		self.isValidPlayer = False


class TTTLogger(object):
	
	def __init__(self, game, mode=0):
		self.__game = game
		self.__mode = mode

		#modes (every stage contains all of the stages before itself):
		#0: logging nothing, but important messages 
		#1: logging the game result
		#2: logging the game
		#3: logging unexpected errors
		#4: logging object trace
		#5: logging logging objects to related errors
		#6: logging everything, the game, errors, messages, just everything

	@property
	def game(self):
		return self.__game
	
	@game.setter
	def game(self, game):
		self.__game = game

	@property
	def mode(self):
		return self.__mode
	
	@mode.setter
	def mode(self, mode):
		self.__mode = mode

	def logResult(self, outcome, winner=TTTNullPlayer()):
		if outcome == "draw":
			self.writeMessage("The game ended in a draw!", 1)
		else:
			self.writeMessage("The winner is the player with \"" + str(winner.displaySymbol) + "\"!", 1)

	def logGameRound(self):
		field = self.game.field
		print(field)
		#for row in field.shape[0]:
		#	symbol0 = self.game.mapSymbolToPlayer(field[row][0]).displaySymbol
		#	symbol1 = self.game.mapSymbolToPlayer(field[row][1]).displaySymbol
		#	symbol2 = self.game.mapSymbolToPlayer(field[row][2]).displaySymbol

		#	line = " ", symbol0, " | ", symbol1, " | ", symbol2, " "
		#	self.writeMessage(line, 2)

	def logGameFinished(self):
		self.logImportantMessage("The game is over.")

	def logImportantMessage(self, message):
		self.logMessage(message, True)

	def logUnexpectedError(self, message):
		self.logError(message)

	def logUnexpectedErrorWithObject(self, message, obj):
		self.logErrorWithObject(message, obj)

	def logExpectedError(self, message):
		self.logError(message, True)

	def logExpectedErrorWithObject(self, message, obj):
		self.logErrorWithObject(message, obj, True)

	def logErrorWithObject(self, message, obj, expected=False):
		self.logError(message, expected)
		self.writeMessage("Related object:", 4)
		self.logObject(obj)

	def logMessage(self, message, important=False):
		if important:
			self.writeMessage(message, 0)
		else:
			self.writeMessage(message, 6)

	def logError(self, message, expected=False):
		if expected:
			self.writeMessage("Known Error: " + str(message), 5)
		else:
			self.writeMessage("Error: " + str(message), 3)

	def logObject(self, obj):
		self.writeObject(str(obj), 4)

	def writeObject(self, obj, mode):
		self.writeMessage(str(obj), mode)

	def writeMessage(self, message, mode):
		if self.mode >= mode:
			print(message)


class TTTGame(object):

	def __init__(self, playerOne=None, playerTwo=None):
		self.__field = np.zeros((3, 3))

		self.__playerOne = playerOne
		self.__playerTwo = playerTwo

		self.__freeSymbol = 0
		self.__symbolDict = {self.playerOne : -1, self.playerTwo : 1, TTTNullPlayer() : self.freeSymbol}

		self.__turn = self.playerOne

		self.logger = TTTLogger(self, 6)

	@property
	def field(self):
		return self.__field
	
	@field.setter
	def field(self, field):
		self.__field = field

	@property
	def playerOne(self):
		return self.__playerOne
	
	@playerOne.setter
	def playerOne(self, player):
		self.__playerOne = player

	@property
	def playerTwo(self):
		return self.__playerTwo
	
	@playerTwo.setter
	def playerTwo(self, player):
		self.__playerTwo = player

	@property
	def freeSymbol(self):
		return self.__freeSymbol
	
	@freeSymbol.setter
	def freeSymbol(self, symbol):
		self.__freeSymbol = symbol

	@property
	def symbolDict(self):
		return self.__symbolDict
	
	@symbolDict.setter
	def symbolDict(self, symbolDict):
		self.__symbolDict = symbolDict

	@property
	def turn(self):
		return self.__turn
	
	@turn.setter
	def turn(self, player):
		self.__turn = player

	@property
	def logger(self):
		return self.__logger
	
	@logger.setter
	def logger(self, logger):
		self.__logger = logger

	def mapPlayerToSymbol(self, player):
		if isinstance(player, TTTNullPlayer):
			self.logger.logExpectedErrorWithObject("This is a NullPlayer, you get an empty symbol!", player)
			return 0
		elif player not in self.symbolDict:
			#print("Error: There is no symbol for player \"", str(player), "\"!\n")
			self.logger.logUnexpectedErrorWithObject("There is no symbol for given player!", player)
			return 0
		return self.symbolDict[player]

	def mapSymbolToPlayer(self, symbol):
		if symbol < -1 or symbol > 1:
			#print("Error: There is no player represented by the symbol \"", str(symbol), "\"!\n")
			self.logger.logUnexpectedErrorWithObject("There is no player represented by the given symbol!", symbol)
			return TTTNullPlayer()
		elif symbol == self.freeSymbol:
			self.logger.logExpectedErrorWithObject("This is an empty symbol, you get a NullPlayer.", symbol)
		return self.symbolDict.keys()[self.symbolDict.values().index(symbol)]

	def getAt(self, position):
		return self.field[position[0]][position[1]]

	def setAt(self, position, symbol):
		self.field[position[0]][position[1]] = symbol

	def placeAt(self, position):
		if self.getAt(position) == self.freeSymbol:
			self.setAt(position, self.mapPlayerToSymbol(self.turn))
		else:
			self.turn.invalidSet(self, position)

	def start(self):
		self.runTurn()

	def runTurn(self):
		self.logger.logGameRound()
		self.turn.doTurn(self)

		if self.checkForFinish():
			#print("The game ended.")
			self.logger.logGameFinished()
		else:
			self.switchPlayers()

	def checkForFinish(self):
		winner = self.checkForWinner()
		if winner.isValidPlayer:
			winner.win()
			self.otherPlayer(player).lose()
			#print("Player \"", str(winner), "\" won!\n")
			self.logger.logResult("win", winner)
			return True
		elif self.checkForFullField():
			self.playerOne.draw()
			self.playerTwo.draw()
			self.logger.logResult("draw")
			return True
		return False

	def switchPlayers():
		self.turn = self.otherPlayer(self.turn)
		self.runTurn()

	def otherPlayer(self, player):
		if player == self.playerOne:
			return self.playerTwo
		elif player == self.playerTwo:
			return self.playerOne
		else:
			#print("Error: Cannot find given player \"", str(player), "\" to convert it to other player!\n")
			self.logger.logUnexpectedErrorWithObject("Cannot find given player and as a result cannot find other player!", player)
			return TTTNullPlayer()

	def checkForWinner(self):
		winnerSymbol = self.checkForCompleteLines(0, 0)
		winnerSymbol = self.checkForCompleteLines(1, 1)
		winnerSymbol = self.checkForCompleteLines(2, 2)

		winner = self.mapSymbolToPlayer(winnerSymbol)
		return winner

	def checkForFullField():
		if np.any(self.field[:, 0] == self.freeSymbol):
			return True
		return False

	def checkForCompleteLines(self, row, col):
		winnerSymbol = self.checkRow(row)

		nextSymbol = self.checkCol(col)
		if nextSymbol != self.freeSymbol:
			winnerSymbol = nextSymbol

		#winnerSymbol = self.checkDiagonal(row, col)

		return winnerSymbol

	def checkRow(self, row):
		firstSymbol = self.field[row][0]
		for col in range(self.field.shape[1]):
			symbol = self.field[row][col]
			if symbol == self.freeSymbol or symbol != firstSymbol:
				return self.freeSymbol
		return firstSymbol

	def checkCol(self, col):
		firstSymbol = self.field[0][col]
		for row in range(self.field.shape[0]):
			symbol = self.field[row][col]
			if symbol == self.freeSymbol or symbol != firstSymbol:
				return self.freeSymbol
		return firstSymbol

	def checkDiagonal(self, row, col):
		pass


def main():
	playerOne = TTTPlayer("X")
	playerTwo = TTTPlayer("O")

	game = TTTGame(playerOne, playerTwo)
	game.start()

main()