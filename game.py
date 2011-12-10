import random, time, math

class Field:
    """Provide a playing field for a Minesweeper game.

    This class internally represents a Minesweeper playing field, and provides
    all functions necessary for the basic manipulations used in the game.
    """
    def __init__(self, rows = 16, cols = 16, mines = 40):
        """Initialize the playing field.

        This function creates a playing field of the given size, and randomly
        places mines within it.

        rows and cols are the numbers of rows and columns of the playing
        field, respectively.  mines is the number of mines to be placed within
        the field.
        """
        for var in (rows, cols, mines):
            if var < 0:
                raise ValueError, "all arguments must be > 0"
        if mines >= (rows * cols):
            raise ValueError, "mines must be < (rows * cols)"
                
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.cleared = 0
        self.flags = 0
        self.start_time = None
        self.lose = 0

        minelist = []
        self.freecoords = {}
        for col in range(cols):
            self.freecoords[col] = range(rows)
        while mines > 0:
            y = random.choice(self.freecoords.keys())
            x = random.randrange(len(self.freecoords[y]))
            minelist.append((self.freecoords[y][x], y))
            del self.freecoords[y][x]
            if not self.freecoords[y]:
                del self.freecoords[y]
            mines = mines - 1

        self.board = []
        for col in range(cols):
            self.board.append([(-2, 0)] * rows)
            for row in range(rows):
                if (row, col) in minelist:
                    self.board[col][row] = (-1, 0)


    def _get_adjacent(self, x, y):
        """Provide a list of all tiles adjacent to the given tile.

        This function takes the x and y coordinates of a tile, and returns a
        list of a 2-tuples containing the coordinates of all adjacent tiles.

        x and y are the x and y coordinates of the base tile, respectively.
        """
        adjlist = [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
                   (x - 1, y), (x + 1, y),
                   (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)]
        rmlist = []
        for adjpair in adjlist:
            for value, index in [(-1, 0), (-1, 1), (self.cols, 0),
                                 (self.rows, 1)]:
                if adjpair[index] == value:
                    rmlist.append(adjpair)
                    break
        for item in rmlist:
            adjlist.remove(item)
        return adjlist


    def open(self, coordlist, y = None):
        """Open one or more tiles.

        This function opens all the tiles provided, and others as
        appropriate, and returns a list indicating which tiles were opened
        and the result of the open.  If a tile is opened which has no
        adjacent mines, all adjacent tiles will be opened automatically.

        The function returns a list of 2-tuples.  The first value is a
        2-tuple with the x and y coordinates of the opened tile; the second
        value indicates the number of mines adjacent to the tile, or -1 if
        the tile contains a mine.

        If a value for y is given, the tile at (coordlist, y) will be
        opened; otherwise, the function will open the tiles whose
        coordinates are given in 2-tuples in coordlist.
        """
        if y is not None:
            coordlist = [(coordlist, y)]
        opened = []
        while len(coordlist) != 0:
            x, y = coordlist.pop()
            not_done = 1
            if (self.board[x][y][1] == 1) or (self.board[x][y][0] >= 0):
                not_done = 0
            elif self.board[x][y][0] == -1:
                if self.cleared > 0:
                    self.board[x][y] = (-1, -1)
                    opened.append(((x, y), -1))
                    not_done = 0
                else:
                    while self.board[x][y][0] == -1:
                        # The first opened block is a mine; move it elsewhere.
                        newx = random.choice(self.freecoords.keys())
                        newy = random.randrange(len(self.freecoords[newx]))
                        self.board[x][y] = (-2, 0)
                        self.board[newx][newy] = (-1,
                                                  self.board[newx][newy][1])
            if not_done:
                adjlist = self._get_adjacent(x, y)
                adjcount = 0
                for adjx, adjy in adjlist:
                    if self.board[adjx][adjy][0] == -1:
                        adjcount = adjcount + 1
                self.board[x][y] = (adjcount, -1)
                if self.cleared is 0:
                    del self.freecoords
                    self.start_time = time.time()
                self.cleared = self.cleared + 1
                opened.append(((x, y), adjcount))
                if adjcount == 0:
                    coordlist.extend(adjlist)
        return opened


    def open_adjacent(self, x, y):
        """Open all unflagged tiles adjacent to the given one, if appropriate.

        This function counts the number of tiles adjacent to the given one
        which are flagged.  If that count matches the number of mines adjacent
        to the tile, all unflagged adjacent tiles are opened, using
        Field.open().

        x and y are the x and y coordinates of the tile to be flagged,
        respectively.
        """
        adjmines = self.board[x][y][0]
        if self.board[x][y][1] != -1:
            return []
        adjlist = self._get_adjacent(x, y)
        flagcount = 0
        for adjx, adjy in adjlist:
            if self.board[adjx][adjy][1] == 1:
                flagcount = flagcount + 1
        if adjmines == flagcount:
            return self.open(adjlist)
        else:
            return []
        

    def flag(self, x, y):
        """Flag or unflag an unopened tile.

        This function attempts to toggle the flagged status of the tile at
        the given coordinates, and returns a value indicating the action
        which occurred.  A return value of -1 indicates that the tile is
        opened and cannot be flagged; 0 indicates that the tile is unflagged;
        and 1 indicates that the tile was flagged.

        x and y are the x and y coordinates of the tile to be flagged,
        respectively.
        """
        if self.board[x][y][1] == -1:
            return -1
        elif self.board[x][y][1] == 0:
            self.board[x][y] = (self.board[x][y][0], 1)
            self.flags = self.flags + 1
            return 1
        else:
            self.board[x][y] = (self.board[x][y][0], 0)
            self.flags = self.flags - 1
            return 0

    def read(self, x, y):
        """Get visual of (x,y)"""

        if x < 0 or x >= self.cols or y < 0 or y >= self.rows:
            return "out"
        elif self.board[x][y][1] == 1: # mine
            return "flagged"
        elif self.board[x][y][1] == 0: # unknown
            return "unknown"
        else:
            return "%d" % self.board[x][y][0]

    def get_adjacent_info(self, x, y):
        n_unveiled = 0; n_unknown = 0; n_flagged = 0
        adjlist = self._get_adjacent(x, y)
        for adjx, adjy in adjlist:
            if self.board[adjx][adjy][1] == 1: # mine
                n_flagged = n_flagged + 1
            elif self.board[adjx][adjy][1] == 0: # unknown
                n_unknown = n_unknown + 1
            else:
                n_unveiled = n_unveiled + 1
        return n_unveiled, n_unknown, n_flagged
        


    def playtime(self):
        """Return a string representing the current play time.

        This function returns a string which provides a human-readable
        representation of the amount of time the current game has been
        played, starting when the first tile is opened.  If the player
        takes an inordinate amount of time (9999 minutes, 0 seconds -- or
        longer), the returned string will be '9999:00+'.
        """
        if self.start_time is None:
            return '00:00'
        rawtime = int(time.time() - self.start_time)
        mins = int(math.floor(rawtime / 60.0))
        secs = rawtime % 60
        if mins > 9998:
            return '9999:00+'
        elif (mins < 10) and (secs < 10):
            return '0%i:0%i' % (mins, secs)
        elif mins < 10:
            return '0%i:%i' % (mins, secs)
        elif secs < 10:
            return '%i:0%i' % (mins, secs)
        else:
            return '%i:%i' % (mins, secs)

    def playtime_in_second(self):
        if self.start_time is None:
	    return 0
        return int(time.time() - self.start_time)

    def won(self):
        """Indicate whether or not the game has been won.

        This function will return a true value if the game has been won, and
        a false value otherwise.
        """
        if self.lose:
            return -1
        return ((self.flags == self.mines) and
                (self.cleared == (self.rows * self.cols) - self.mines))
                
