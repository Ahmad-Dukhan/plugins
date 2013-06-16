'''
A text command which shows the end of the selection at center and blinks the
block a cuple of times to support visual localization.

For use add something like this to your user definable key bindings file:
{ "keys": ["super+k"], "command": "show_at_center_and_blink" },
{ "keys": ["super+shift+k"], "command": "show_at_center_and_blink",
  "args": {"do_center": false} },

@author: Oktay Acikalin <ok@ryotic.de>

@license: MIT (http://www.opensource.org/licenses/mit-license.php)

@since: 2011-02-25
'''

import sublime
import sublime_plugin


BLINK_FREQUENCY = 200
BLINK_MAX_COUNT = 2


active_repeater = 0


class ShowAtCenterAndBlinkCommand(sublime_plugin.TextCommand):

    def run(self, edit, do_center=True):
        global active_repeater
        
        if do_center:
            self.view.run_command('show_at_center')
        sel = self.view.sel()[0]
        sel = self.view.line(sel)
        
        def add():
            self.view.add_regions('ShowAtCenterAndBlinkCommand', [sel],
                                  'bookmark', 'bookmark',
                                  sublime.DRAW_OUTLINED)
        def remove():
            self.view.erase_regions('ShowAtCenterAndBlinkCommand')
        
        def repeater(id, count=0):
            if active_repeater != id:
                return
            def stub():
                repeater(id, count + 1)
            if count > BLINK_MAX_COUNT * 2 - 1:
                return
            elif count % 2 == 0:
                add()
            else:
                remove()
            sublime.set_timeout(stub, BLINK_FREQUENCY)
        
        active_repeater += 1
        repeater(active_repeater)
