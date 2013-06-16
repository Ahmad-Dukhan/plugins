'''
Wrapper of the built-in exec.py file. Changes are:
* Execute commands (run_command()) thru an optional shell wrapper.
This can be used to ensure a specific environment before running the
intended command like make, tidy etc..

You have to set exec_arg_list_wrapper in your Global.sublime-settings file
to something like this to make it work:
"exec_arg_list_wrapper": ["bash", "-l", "-c"]

@author: Oktay Acikalin <ok@ryotic.de>

@license: MIT (http://www.opensource.org/licenses/mit-license.php)

@since: 2011-02-12
'''

import sublime


try:
    _exec_is_wrapped
except NameError:
    _exec_is_wrapped = True
    
    class AsyncProcess(AsyncProcess):
        '''
        Wrapper of the built-in AsyncProcess class.
        '''

        def __init__(self, arg_list, *args, **kwargs):
            '''
            Initializes the object and modifies the arg_list.

            @type  arg_list: list
            @param arg_list: Command line splitted up as a list of strings.
            @type      args: list
            @param     args: Additional positional args.
            @type    kwargs: dict
            @param   kwargs: Additional named args.

            @return: None
            '''
            settings = sublime.load_settings("Global.sublime-settings")
            arg_list_wrapper = settings.get("exec_arg_list_wrapper", [])
            if arg_list_wrapper:
                from pipes import quote
                arg_list = map(quote, arg_list)
                arg_list = arg_list_wrapper + [' '.join(arg_list)]
            super(AsyncProcess, self).__init__(arg_list, *args, **kwargs)
