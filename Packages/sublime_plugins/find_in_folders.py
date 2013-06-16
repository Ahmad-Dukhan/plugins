import sublime_plugin


class FindInFoldersCommand(sublime_plugin.TextCommand):

    def run(self, edit, dirs):
        dirs = ','.join(dirs)
        window = self.view.window()
        window.run_command('show_panel',
                           dict(panel='find_in_files', location=dirs))
