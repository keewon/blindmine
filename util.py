class Option:
    def __init__(self):
	self.rows = 9
	self.cols = 9
	self.mines = 10
	self.lang = 'ko'

    def load(self):
	pass
    
    def save(self):
	pass

MENU_EXIT=0
MENU_SIZE=1
MENU_LANG=2
MENU_HIGHSCORE=3
MENU_OPINION=4

class Menu:
    def __init__(self):
	self.cursor = 0
	self.list = []

# vim: ts=8 sts=4 sw=4 expandtab
