'''
A text command to scan selections for Mage classes, open the referenced files
and temporarily bookmark and highlight found symbols.

For use add something like this to your user definable key bindings file:
{ "keys": ["super+shift+o"], "command": "open_mage_file", "context":
    [
        { "key": "selector", "operator": "equal", "operand": "source.php" }
    ]
}

@author: Oktay Acikalin <ok@ryotic.de>

@license: MIT (http://www.opensource.org/licenses/mit-license.php)

@since: 2011-02-23
'''

import os
import re

import sublime
import sublime_plugin

import support.grep


INCLUDE_PATHS = [
    'app/code/core',
    'app/code/community',
    'app/code/local',
    'lib',
]


def php_filter(filename):
    if not os.path.isdir(filename):
        filename = filename.lower()
        return (filename.endswith('.php') or filename.endswith('.html'))
    return True


class Highlighter(object):
    '''
    Class which tries to highlight given symbols as soon as the file has been
    loaded.
    '''

    def __init__(self, view, symbols):
        '''
        Initializes the object.

        @type     view: sublime.View
        @param    view: View to work with.
        @type  symbols: list
        @param symbols: List with strings.

        @return: None
        '''
        self.view = view
        self.symbols = symbols
    
    def run(self):
        '''
        If view is loaded it tries to bookmark and select all symbols.
        If not it waits for 100ms and tries again.

        @return: None
        '''
        if self.view.is_loading():
            sublime.set_timeout(self.run, 100)
        else:
            regions = []
            for symbol in self.symbols:
                if type(symbol) is tuple:
                    symbol = symbol[0]
                # print 'highlight:', symbol
                results = self.view.find_all('(abstract\s+)?(class) %s(.*)' % symbol)
                if results:
                    regions += results
            if regions:
                regions = sorted(regions, key=lambda region: region.begin())
                # print regions
                self.view.add_regions('bookmarks', regions, 'bookmark',
                                      'bookmark', sublime.DRAW_OUTLINED)
                self.view.show_at_center(regions[0])
                sel = self.view.sel()
                sel.clear()
                sel.add(sublime.Region(regions[0].begin(), regions[0].begin()))


class OpenMageFileCommand(sublime_plugin.TextCommand):
    
    def find_index_php(self, basedir):
        testfile = os.path.join(basedir, 'index.php')
        if os.path.exists(testfile):
            return basedir
        elif os.path.dirname(basedir) != basedir:
            return self.find_index_php(os.path.dirname(basedir))
        else:
            return None

    def find_mage_root(self):
        filepath = self.view.file_name()
        basedir = self.find_index_php(os.path.dirname(filepath))
        if not basedir:
            return None
        mage_file = os.path.join(basedir, 'app', 'Mage.php')
        if os.path.exists(mage_file):
            return basedir
        else:
            return None

    def find_file(self, mage_root, filepath):
        include_paths = INCLUDE_PATHS[:]
        include_paths.reverse()
        for path in include_paths:
            testfile = os.path.join(mage_root, path, filepath)
            if os.path.exists(testfile):
                return testfile
        return None
    
    def find_file_by_include_path(self, filepath):
        basedir = os.path.dirname(self.view.file_name())
        join = os.path.join
        exists = os.path.exists
        dirname = os.path.dirname
        for path in INCLUDE_PATHS:
            testdir = basedir
            old_testdir = None
            while old_testdir != testdir:
                testfile = join(testdir, filepath)
                # print 'testfile =', testfile
                if exists(testfile):
                    return testfile
                old_testdir = testdir
                testdir = dirname(testdir)
        return None


    def run(self, edit):
        class_name_regex = re.compile(r'^([\w\d]+)$')
        class_def_syntax_regex = re.compile(r'^(abstract\s+)?class\s+(?P<class_name>[\w\d]+)(\s+(extends|implements)\s+(?P<parent_class_name>[\w\d]+))?')

        mage_root = self.find_mage_root()
        # print 'mage_root =', mage_root
        
        for selection in self.view.sel():
            if selection.empty():
                self.view.run_command('expand_selection', {'to': 'scope'})
        
        for selection in self.view.sel():
            class_name = self.view.substr(selection)
            if not class_name_regex.match(class_name) or '_' not in class_name:
                match = class_def_syntax_regex.match(class_name)
                if match:
                    results = match.groupdict()
                    if results['parent_class_name']:
                        class_name = results['parent_class_name']
                    else:
                        class_name = results['class_name']
            if not class_name_regex.match(class_name) or '_' not in class_name:
                match = class_def_syntax_regex.match(class_name)
                sublime.error_message('Not a valid class name in selection:\n%s' % class_name)
                continue
            
            content = class_name.replace('_', os.sep) + '.php'
            # print 'content =', content

            filepath = None
            # First try by looking into mage_root.
            if mage_root:
                filepath = self.find_file(mage_root, content)
                # print '1. filepath =', filepath
            # Second try by traversing the file path.
            if not filepath:
                filepath = self.find_file_by_include_path(content)
                # print '2. filepath =', filepath
            # Third try by searching in mage_root.
            if mage_root and not filepath:
                search = 'class %s' % class_name.encode('ascii')
                filepath = support.grep(search, [mage_root], recursive=True,
                                        filter_func=php_filter)
                if filepath:
                    filepath = filepath[0]
                # print '3. filepath =', filepath

            if filepath:
                view = self.view.window().open_file(filepath)
                symbols = [class_name]
                highlighter = Highlighter(view, symbols)
                highlighter.run()
            else:
                sublime.error_message('Could not find file for:\n%s' % class_name)
