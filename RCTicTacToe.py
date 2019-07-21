import numpy as np
import RCNeuralNetwork as nn

class TTTPlayer(object):

	def __init__(self, name, displaySymbol):
		self.__name = name
		self.__displaySymbol = displaySymbol
		self.__isValidPlayer = True

	@property
	def name(self):
		return self.__name

	@name.setter
	def name(self, name):
		self.__name = name

	@property
	def displaySymbol(self):
		return self.__displaySymbol

	@displaySymbol.setter
	def displaySymbol(self, displaySymbol):
		self.__displaySymbol = displaySymbol

	@property
	def isValidPlayer(self):
		return self.__isValidPlayer

	@isValidPlayer.setter
	def isValidPlayer(self, boolean):
		self.__isValidPlayer = boolean

	def doTurn(self, game):
		print(self.name + ", please enter your field!")
		number = int(input("Please enter the field number: "))
		print()

		game.placeAt(game.transformNumberToPosition(number))

	def invalidSet(self, game, position):
		print("Invalid field! Please enter a different field!\n")
		self.doTurn(game)

	def win(self):
		pass

	def draw(self):
		pass

	def lose(self):
		pass


class TTTNeuralNetworkPlayer(TTTPlayer, nn.NeuralNetwork):

	def __init__(self, name, displaySymbol):
		TTTPlayer.__init__(self, name, displaySymbol)
		nn.NeuralNetwork.__init__(self, (9, 12, 18, 12, 9))

	def doTurn(self, game):
		prediction = self.calculate(game.field.reshape(9, 1))
		result = (0, 0)
		for index in range(9):
			prob = prediction[index]
			if result[0] < prob:
				result = (prob, index)

		print("Neural network guessed field " + str(result[1] + 1) + " with a probability of " + str(result[0]) + "!\n")

		game.placeAt(game.transformNumberToPosition(result[1] + 1))

	def invalidSet(self, game, position):
		print("Neural network fucked up!\n")
		game.quit()
		#self.doTurn(game)

	def win(self):
		pass

	def draw(self):
		pass

	def lose(self):
		pass


class TTTNullPlayer(TTTPlayer):

	def __init__(self):
		super().__init__(None, " ")

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
			self.writeMessage("The game ended in a draw!", 1, True)
		else:
			self.writeMessage("The winner is the player " + str(winner.name) + " (" + str(winner.displaySymbol) + ")!", 1, True)

	def logGameRound(self):
		game = self.game
		field = game.field
		for row in range(field.shape[0]):
			symbol0 = game.mapSymbolToPlayer(field[row][0]).displaySymbol
			symbol1 = game.mapSymbolToPlayer(field[row][1]).displaySymbol
			symbol2 = game.mapSymbolToPlayer(field[row][2]).displaySymbol

			line = " " + symbol0 + " | " + symbol1 + " | " + symbol2 + " "
			self.writeMessage(line, 2)
			if row < (field.shape[0] - 1):
				self.writeMessage("-----------", 2)
		self.finishMessage()

	def logGameFinished(self):
		self.logImportantMessage("The game is over.")

	def logGameQuit(self):
		self.logImportantMessage("The game was forced to quit!")

	def logImportantMessage(self, message):
		self.logMessage(message, True, True)

	def logUnexpectedError(self, message):
		self.logError(message, finish=True)

	def logUnexpectedErrorWithObject(self, message, obj):
		self.logErrorWithObject(message, obj, True)

	def logExpectedError(self, message):
		self.logError(message, True, True)

	def logExpectedErrorWithObject(self, message, obj):
		self.logErrorWithObject(message, obj, True)

	def logErrorWithObject(self, message, obj, expected=False):
		self.logError(message, expected)
		self.writeMessage("Related object:", 4, False)
		self.logObject(obj, True)

	def logMessage(self, message, important=False, finish=False):
		if important:
			self.writeMessage(message, 0, finish)
		else:
			self.writeMessage(message, 6, finish)

	def logError(self, message, expected=False, finish=False):
		if expected:
			self.writeMessage("Known Error: " + str(message), 5, finish)
		else:
			self.writeMessage("Error: " + str(message), 3, finish)

	def logObject(self, obj, finish=False):
		self.writeObject(obj, 4, finish)

	def writeObject(self, obj, mode, finish=False):
		self.writeMessage(str(obj), mode, finish)

	def writeMessage(self, message, mode, finish=False):
		if self.mode >= mode:
			print(message)
			if finish:
				self.finishMessage()

	def finishMessage(self):
		print()


class TTTGame(object):

	def __init__(self, playerOne=None, playerTwo=None):
		self.__field = np.zeros((3, 3))

		self.__playerOne = playerOne
		self.__playerTwo = playerTwo

		self.__freeSymbol = 0
		self.__symbolDict = [(self.playerOne, -1), (self.playerTwo, 1), (TTTNullPlayer(), self.freeSymbol)]

		self.__turn = self.playerOne
		self.__end = False

		self.__logger = TTTLogger(self, 3)

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
	def end(self):
		return self.__end
	
	@end.setter
	def end(self, boolean):
		self.__end = boolean

	@property
	def logger(self):
		return self.__logger
	
	@logger.setter
	def logger(self, logger):
		self.__logger = logger

	def mapPlayerToSymbol(self, player):
		if all(element[0] != player for element in self.symbolDict):
			self.logger.logUnexpectedErrorWithObject("There is no symbol for given player!", player)
			return 0
		elif not player.isValidPlayer:
			self.logger.logExpectedErrorWithObject("This is a NullPlayer, you get an empty symbol!", player)
			return 0
		
		for element in self.symbolDict:
			if element[0] == player:
				return element[1]

	def mapSymbolToPlayer(self, symbol):
		if symbol < -1 or symbol > 1:
			self.logger.logUnexpectedErrorWithObject("There is no player represented by the given symbol!", symbol)
			return TTTNullPlayer()
		elif symbol == self.freeSymbol:
			self.logger.logExpectedErrorWithObject("This is an empty symbol, you get a NullPlayer.", symbol)
		
		for element in self.symbolDict:
			if element[1] == symbol:
				return element[0]

	def transformNumberToPosition(self, number):
		if number >= 1 and number <= 9:
			if number == 1:
				return (0, 0)
			elif number == 2:
				return (0, 1)
			elif number == 3:
				return (0, 2)
			elif number == 4:
				return (1, 0)
			elif number == 5:
				return (1, 1)
			elif number == 6:
				return (1, 2)
			elif number == 7:
				return (2, 0)
			elif number == 8:
				return (2, 1)
			elif number == 9:
				return (2, 2)
		else:
			self.logger.logUnexpectedErrorWithObject("Not a valid number for a field!", number)
			return (-1, -1)

	def checkPosition(self, position):
		if position < self.field.shape:
			return True
		else:
			self.logger.logUnexpectedErrorWithObject("The given position is not valid!", position)
			return False

	def getAt(self, position):
		if self.checkPosition(position):
			return self.field[position[0]][position[1]]
		else:
			self.logger.logUnexpectedErrorWithObject("Cannot get value for given position!", position)
			return False

	def setAt(self, position, symbol):
		if self.checkPosition(position):
			self.field[position[0]][position[1]] = symbol
		else:
			self.logger.logUnexpectedErrorWithObject("Cannot set symbol at given position!", (position, symbol))

	def placeAt(self, position):
		if self.checkPosition(position) and self.getAt(position) == self.freeSymbol:
			self.setAt(position, self.mapPlayerToSymbol(self.turn))
		else:
			self.logger.logUnexpectedErrorWithObject("Cannot place at given position!", position)
			self.turn.invalidSet(self, position)

	def start(self):
		self.logger.logGameRound()
		self.runTurn()

	def quit(self):
		self.logger.logGameQuit()
		self.end = True

	def runTurn(self):
		self.turn.doTurn(self)

		if self.end:
			return

		self.logger.logGameRound()

		if self.checkForFinish():
			self.logger.logGameFinished()
		else:
			self.switchPlayers()

	def checkForFinish(self):
		winner = self.checkForWinner()
		if winner.isValidPlayer:
			winner.win()
			self.otherPlayer(winner).lose()
			self.logger.logResult("win", winner)
			return True
		elif self.checkForFullField():
			self.playerOne.draw()
			self.playerTwo.draw()
			self.logger.logResult("draw")
			return True
		return False

	def switchPlayers(self):
		self.turn = self.otherPlayer(self.turn)
		self.runTurn()

	def otherPlayer(self, player):
		if player == self.playerOne:
			return self.playerTwo
		elif player == self.playerTwo:
			return self.playerOne
		else:
			self.logger.logUnexpectedErrorWithObject("Cannot find given player and as a result cannot find other player!", player)
			return TTTNullPlayer()

	def checkForWinner(self):
		winnerSymbol = self.checkForCompleteLines(0, 0)
		if winnerSymbol == self.freeSymbol:
			winnerSymbol = self.checkForCompleteLines(1, 1)
		if winnerSymbol == self.freeSymbol:
			winnerSymbol = self.checkForCompleteLines(2, 2)

		winner = self.mapSymbolToPlayer(winnerSymbol)
		return winner

	def checkForFullField(self):
		if np.all(self.field[:, :] != self.freeSymbol):
			return True
		return False

	def checkForCompleteLines(self, row, col):
		winnerSymbol = self.checkRow(row)
		if winnerSymbol == self.freeSymbol:
			winnerSymbol = self.checkCol(col)
		if winnerSymbol == self.freeSymbol:
			winnerSymbol = self.checkDiagonal(row, col)

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
		symbol = self.freeSymbol
		if row == col:
			symbol = self.checkLRDiagonal()
		if abs(row + col) == 2 and symbol == self.freeSymbol:
			symbol = self.checkRLDiagonal()
		return symbol

	def checkRLDiagonal(self):
		firstSymbol = self.field[0][0]
		for index in range(self.field.shape[0]):
			symbol = self.field[index][index]
			if symbol == self.freeSymbol or symbol != firstSymbol:
				return self.freeSymbol
		return firstSymbol

	def checkLRDiagonal(self):
		row = 0
		col = 2
		firstSymbol = self.field[row][col]
		for index in range(self.field.shape[0]):
			symbol = self.field[row + index][col - index]
			if symbol == self.freeSymbol or symbol != firstSymbol:
				return self.freeSymbol
		return firstSymbol


def main():
	playerOne = TTTPlayer("Player 1", "X")
	playerTwo = TTTNeuralNetworkPlayer("NNPlayer", "N")

	game = TTTGame(playerOne, playerTwo)
	game.start()

main()