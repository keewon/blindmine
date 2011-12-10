#!/usr/bin/env python

# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA, 02111-1307.
#
# Last revised: $Date: 2006/01/07 00:48:28 $

import math, os, random, sys, time, traceback

from game import Field
from util import Option


def fail(error, debug = 0):
    """Print an error message, with traceback if desired, and exit.

    This function will print an error message with the given body.  It will
    also print an exception traceback if debug is true.  It will then exit
    with an exit code of 1.

    error is the body of the error message.  If debug is a true value, a
    traceback will be printed.
    """
    print "Error: %s; exiting...." % error
    if debug:
        traceback.print_exc()
    sys.exit(1)


def init_ui( option ):
    """Initialize a game interface and return it.

    This function attempts to import and initialize a user interface for the
    game.  If successful, it returns the initialized interface.  Otherwise,
    it aborts the program, with a traceback if debug is true.

    """
    try:
        error_type = "import"
        import sdl_ui
        error_type = "initialize"
        ui = sdl_ui.SDL_UI( option.rows, option.cols, option.mines, 40 )
    except (ImportError, 'UIError'), reason:
        fail("failed to %s UI (%s)" % (error_type, reason), 1)
    return ui


def run(option, ui):
    """Run the game with the given options and interface.

    This function runs the main game loop with the given options and
    interface.  It exits only when the player quits.

    ui is the interface to use for the game.
    """

    saved = []
    cursor = [0, 0]
    examine_keydown = [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
    direction_keydown = [ 0, 0 ]
    tab_used = [0, 0]

    def get_dxdy(a):
        return ( a/3 -1, a%3 -1)

    def get_hash(a):
        return (a[0]+1)*3 + (a[1]+1)

    def field_do(field_func, pos, rows, cols):
        for key in range(0, 9):
            if examine_keydown[key]:
                tmp_x = pos[0] + get_dxdy(key)[0]
                tmp_y = pos[1] + get_dxdy(key)[1]
                if ((0 <= tmp_x < cols) or
                    (0 <= tmp_y < rows)):
                    return field_func(tmp_x, tmp_y), (tmp_x, tmp_y)

        return field_func(pos[0], pos[1]), (pos[0], pos[1])

    def ui_feedback_information():
        n_unveiled, n_unknown, n_flagged =  field.get_adjacent_info(cursor[0], cursor[1])
        ui.feedback( "information %s %d %d %d %d"% 
             (field.read( cursor[0], cursor[1] ), 
             n_flagged, n_unknown, cursor[0]+1, cursor[1]+1 ))

    no_quit = 1
    while no_quit:
        field = Field(9, 9, 10) # FIXME
        ui.reset(option.rows, option.cols, option.mines)

        cursor = [0, 0]
        no_reset = 1
        while no_reset:
            input = ui.get_input()
            # This loop generates the list of commands for ui.update().
            #
            # This loop also takes other internal actions as necessary
            # given the input -- for example, prints debugging information.
            for act, pos in input:
                # cursor_*
                if act in ['cursor_sweep', 'cursor_flag' ]:
                    pos = cursor

                # menu
                if act == 'quit':
                    no_reset = 0
                    no_quit = 0
                elif act == 'reset':
                    no_reset = 0

                # cursor pressed -> move and store pressed key information
                elif act == 'direction_pressed':
                    if pos[0]:
                        direction_keydown[0] = pos[0]
                    if pos[1]:
                        direction_keydown[1] = pos[1]
                    cursor[0] = cursor[0] + pos[0]
                    cursor[1] = cursor[1] + pos[1]

                    #print "down : ", direction_keydown[0], direction_keydown[1]
                elif act == 'direction_up':
                    if pos[0]:
                        direction_keydown[0] = 0
                        tab_used[0] = 0
                    if pos[1]:
                        direction_keydown[1] = 0
                        tab_used[1] = 0

                    #print "up   : ", direction_keydown[0], direction_keydown[1]

                elif act == 'tab':
                    if direction_keydown[0] or direction_keydown[1]:
                        tab_used = [1, 1]
                        def tab_group(symbol):
                            if symbol == 'unknown':
                                return -1
                            elif symbol == 'out':
                                return -2
                            else:
                                return -3
                            
                        mark = field.read( cursor[0], cursor[1] )
                        mark = tab_group(mark)
                        iter_num = 0
                            
                        while 1:
                            new_cursor0 = cursor[0] + direction_keydown[0]
                            new_cursor1 = cursor[1] + direction_keydown[1]
                            new_mark = field.read(new_cursor0, new_cursor1)
                            new_mark = tab_group(new_mark)

                            if new_mark == -2 or iter_num > 0 and mark != new_mark:
                                break
                            cursor[0] = new_cursor0; cursor[1] = new_cursor1
                            mark = new_mark
                            iter_num = iter_num + 1
                        ui.feedback("position %d %d" % (cursor[0]+1, cursor[1]+1))

                            
                    
                # inform
                elif act == 'inform':
                    ui.feedback("number %d %d" % (field.mines, field.flags))
                    ui.feedback("position %d %d" % (cursor[0]+1, cursor[1]+1))
                    ui.feedback("elapsed %d" % field.playtime_in_second()  )

                # load/save
                elif act == 'save_position':
                    ui.feedback("position %d %d" % (cursor[0]+1, cursor[1]+1))
                    saved = [ cursor[0], cursor[1] ]
                elif act == 'load_position':
                    if saved:
                        cursor[0] = saved[0]
                        cursor[1] = saved[1]
                    ui.feedback("position %d %d" % (cursor[0]+1, cursor[1]+1))

                # examine
                elif act == 'examine_pressed':
                    if 0: #pos[0] == 0 and pos[1] == 0:
                        ui_feedback_information()
                    else:
                        ui.feedback( field.read( cursor[0] + pos[0], 
                                                cursor[1] + pos[1] ) )
                    examine_keydown[ get_hash(pos) ] = 1
                elif act == 'examine_up':
                    #print "up   : ", get_hash(pos), pos[0], pos[1] 
                    examine_keydown[ get_hash(pos) ] = 0

                elif act in ('open', 'sweep', 'cursor_sweep'):
                    if act == 'cursor_sweep':
                        mark = field.read( pos[0], pos[1] )
                        if mark == 'unknown':
                            #print "pos[0] = ", pos[0], " pos[1] = ", pos[1]
                            act = 'cursor_open'

                    if act == 'open':
                        opened = field.open(pos[0], pos[1])

                    elif act == 'cursor_sweep':
                            opened, _ = field_do(field.open_adjacent, 
                                            pos, field.rows, field.cols)
                    elif act == 'cursor_open':
                            opened, _ = field_do(field.open, 
                                            pos, field.rows, field.cols)
                    else:
                        opened = field.open_adjacent(pos[0], pos[1])

                    if (act == 'cursor_sweep' or act == 'sweep') and opened:
                        ui.feedback("sweep")
                    elif (act == 'open' or act == 'cursor_open') and opened:
                        if len(opened) > 1:
                            ui.feedback("openmany")
                        else:
                            ui.feedback("open")
                        ui.feedback("%d" % opened[0][1])
                    else:
                        ui.feedback("invalid")
                        ui_feedback_information()

                    for result in opened:
                        if result[1] == 0:
                            break  # We couldn't have hit any mines.
                        if result[1] == -1:
                            field.lose = 1
                            break
                elif act == 'flag' or act == 'cursor_flag':
                    result = -1

                    if act == 'cursor_flag':
                        result, pos = field_do( field.flag, pos,
                                                field.rows, field.cols)
                    else:
                        result = field.flag(pos[0], pos[1])
                    if result == 1:
                        ui.feedback("flagged")
                    elif result == 0:
                        ui.feedback("unflagged")
                elif act == 'read_all':
                    nesw = [ (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1) ]
                    all = ""
                    

            # check for invalid input
            if cursor[0] < 0:
                cursor[0] = 0
                ui.feedback('out')
            elif cursor[0] >= field.cols:
                cursor[0] = field.cols-1
                ui.feedback('out')

            if cursor[1] < 0:
                cursor[1] = 0
                ui.feedback('out')
            elif cursor[1] >= field.rows:
                cursor[1] = field.rows-1
                ui.feedback('out')

            ui.update_game(field.board, field.rows, field.cols, field.flags, field.playtime(), field.playtime_in_second(), field.won(), cursor)
            ui.wait()


if __name__ == '__main__':
    #sys.path.append(os.path.normpath(os.path.join(sys.prefix,
    #                                              'lib/games/pysweeper')))

    random.seed()
    option = Option()

    ui = init_ui( option )
    run( option , ui)

# vim: ts=8 sts=4 sw=4 expandtab
