#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import socket
import threading
import traceback

HOST = '0.0.0.0'
PORT = 11123

LEAST_LEN = 3
LEAST_BONUS = 2
LONGEST_LEN = 6

PLAY_TIME = 150
SCORE_TIME = 20
RANK_TIME = 10

dictfile =  'dictionary/newdict'
characters = {
	u'あ':  3, u'い':  1, u'う':  1, u'え':  5, u'お':  3,
	u'か':  2, u'き':  2, u'く':  1, u'け':  5, u'こ':  2,
	u'が':  5, u'ぎ':  9, u'ぐ': 10, u'げ':  9, u'ご':  9,
	u'さ':  4, u'し':  1, u'す':  4, u'せ':  4, u'そ':  8,
	u'ざ': 11, u'じ':  3, u'ず': 11, u'ぜ': 12, u'ぞ': 12,
	u'た':  3, u'ち':  4, u'つ':  2, u'て':  6, u'と':  3,
	u'だ':  7, u'ぢ': 13, u'づ': 13, u'で': 10, u'ど':  6,
	u'な':  6, u'に':  8, u'ぬ': 12, u'ね': 10, u'の':  6,
	u'は':  7, u'ひ':  8, u'ふ':  7, u'へ': 12, u'ほ':  9,
	u'ば':  8, u'び': 10, u'ぶ':  7, u'べ': 11, u'ぼ': 10,
	u'ぱ': 11, u'ぴ': 13, u'ぷ': 11, u'ぺ': 13, u'ぽ': 12,
	u'ま':  5, u'み':  6, u'む':  9, u'め':  7, u'も':  8,
	u'や':  5, u'ゆ':  4, u'よ':  2, u'わ':  8, u'ん':  1
}

class BoardGenerator(threading.Thread):
	def __init__(self, queue, adjacent, wordlist):
		threading.Thread.__init__(self)

		self.queue = queue
		self.adjacent = adjacent
		self.dict = wordlist

	def getPoint(self, word):
		res = len(word) ** 5 / 150
		for i in word:
			res += characters[i]
		return res

	def search(self, word):
		down = 0
		up = len(self.dict) - 1
		while up - down > 2:
			mid = (up + down) / 2
			if self.dict[mid] < word :
				down = mid
			else:
				up = mid

		pos = down
		while pos < len(self.dict) - 1 and self.dict[pos] < word:
			pos += 1
		if word == self.dict[pos]:
			return 1
		if word in self.dict[pos]:
			return 2
		return 0

	def getWordlist(self, board):
		used = [False] * 16
		wordlist = []

		def dfs(i, word, index):
			res = 0
			p = self.search(word)
			if p == 0:
				return res
			elif p == 1:
				wordlist.append([word, index])
				res += 1

			used[i] = True
			for j in self.adjacent[i]:
				if used[j]:
					continue
				res += dfs(j, word + board[j], index + [j])
			used[i] = False

			return res
	
		longest = 0
		for i in range(16):
			dfs(i, board[i], [i])

		if len(wordlist) == 0:
			return wordlist, -1

		res = []
		for i in range(16):
			res.append([])
			for word in wordlist:
				if i in word[1]:
					res[i].append(word)
		res.append(wordlist)

		ret = []
		for i in range(17):
			ret.append([])
			res[i].sort()

			last = '111'
			for j in range(len(res[i])):
				if(res[i][j][0] == last):
					continue
				ret[i].append(res[i][j])
				last = res[i][j][0]

			ret[i].sort(key = lambda n:self.getPoint(n[0]),reverse = True)

		longest = max([len(word[1]) for word in wordlist])
		return ret, longest

	def run(self):
		while True:
			board = [random.choice(characters.keys()) for x in range(16)]
			wordlist, longest = self.getWordlist(board)
			if longest < LONGEST_LEN:
				continue
			if min([len(word) for word in wordlist]) < LEAST_BONUS:
				continue
			self.queue.append(str(board) + '|' + str(wordlist))

class GameManager(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)

		self.queue = queue
		self.nextTurn = self.getNextTurn()
		self.ranking = []
		self.rankSorted = False

		self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serverSock.bind((HOST, PORT))
		self.serverSock.listen(5)

	def getNextTurn(self):
		total = PLAY_TIME + SCORE_TIME + RANK_TIME
		turn = (time.time() + RANK_TIME + SCORE_TIME + 5) / total
		return (turn + 1) * total - SCORE_TIME - RANK_TIME - 5

	def recieve(self, clientSock):
		rcvmsg = clientSock.recv(4096)

		if time.time() > self.nextTurn:
			self.queue.pop(0)
			self.ranking = []
			self.rankSorted = False
			self.nextTurn = self.getNextTurn()

		response = None
		if rcvmsg == 'gettime':
			response = '%f,%d,%d,%d' % (time.time(), PLAY_TIME, SCORE_TIME, RANK_TIME)
		elif rcvmsg == 'getboard':
			response = self.queue[0]
		elif rcvmsg == 'getranking':
			if not self.rankSorted:
				self.ranking.sort(key = lambda x: x[1], reverse = True)
				self.rankSorted = True
			response = str(self.ranking)
		elif rcvmsg.split('|')[0] == 'sendscore':
			self.ranking.append(eval(rcvmsg.split('|')[1]))
		if response != None:
			try:
				clientSock.sendall(response)
			except:
				traceback.print_exc()
		clientSock.close()

	def run(self):
		while True:
			clientSock, clientAddress = self.serverSock.accept()
			connection = threading.Thread(target = self.recieve, args = (clientSock,))
			connection.start()

def makeAdjacent():
	res = [[] for i in range(16)]
	for x in range(4):
		for y in range(4):
			for i in range(-1, 2):
				for j in range(-1, 2):
					if i == j == 0:
						continue
					if -1 < x + i < 4 and -1 < y + j < 4:
						res[x * 4 + y].append((x + i) * 4 + (y + j))
	return res

def loadDict(filename):
	f = open(filename, 'r')

	wordlist = set()
	for line in f:
		line = line.strip().decode('UTF-8')
		word = line.split(',')[0]
		if len(word) < LEAST_LEN :
			continue
		wordlist.add(word)
	
	return sorted(list(wordlist))


def main():
	queue = []
	adjacent = makeAdjacent()
	wordlist = loadDict(os.path.dirname(os.path.abspath(__file__)) + '/' + dictfile)

	thread = [BoardGenerator(queue, adjacent, wordlist) for i in range(2)]
	for i in thread:
		i.start()

	while True:
		if len(queue) > 3:
			break
		time.sleep(5)

	manager = GameManager(queue)
	manager.start()

if __name__ == '__main__':
	main()
