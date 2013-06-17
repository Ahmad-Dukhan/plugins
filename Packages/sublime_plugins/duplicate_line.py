'''
Fork of the built-in duplicate_line command. Features are:
* duplicate current line (without selection made)
* duplicate selection in line
* duplicate selected block
It does this by pasting the selected area right after the selection.

@author: Oktay Acikalin <ok@ryotic.de>

@license: MIT (http://www.opensource.org/licenses/mit-license.php)

@since: 2011-02-12
'''

import sublime_plugin


class DuplicateLineCommand(sublime_plugin.TextCommand):
    '''
    A text command to duplicate current line or selection.
    '''

    def run(self, edit):
        '''
        Duplicates line or selection.

        @type  edit: sublime.Edit
        @param edit: Object used for replacement actions.

        @return: None
        '''
        for region in self.view.sel():
            line = region
            if line.empty():
                line = self.view.full_line(region)
            line_contents = self.view.substr(line)
            self.view.insert(edit, line.end(), line_contents)
