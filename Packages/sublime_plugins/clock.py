'''
Shows a very simple clock within the status bar.

@todo Only show when in fullscreen mode.
@todo Disable clock by default.
@todo Make format string user definable.
@todo Make weekdays user definable.
@todo Code cleanup.
'''

from datetime import datetime

import sublime
import sublime_plugin

from support.view import view_is_widget


# FORMAT = '%(weekday)s %%d %%H:%%M'
FORMAT = '%%H:%%M'
WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
STATUS_KEY = 'clock'

if 'active_clock_id' not in globals().keys():
    active_clock_id = 0

if 'active_views' not in globals().keys():
    active_views = dict()


class Clock(object):

    def __init__(self):
        global active_clock_id, active_views
        self.views = active_views
        active_clock_id += 1
        self.id = active_clock_id
        # print 'new clock', self.id
    
    def add_view(self, view):
        if view.id() not in self.views:
            self.views[view.id()] = view, None
            self.update()
    
    def del_view(self, view):
        if view.id() in self.views:
            del self.views[view.id()]
            # print 'erase'
            view.erase_status(STATUS_KEY)
    
    def update(self):
        for id, data in self.views.iteritems():
            view, last = data
            now = datetime.now()
            format = FORMAT % dict(
                weekday=WEEKDAYS[int(now.strftime('%w'))],
            )
            new = now.strftime(format)
            if new != last:
                view.set_status(STATUS_KEY, new)
                self.views[id] = view, new
                # print 'updated', id, new, type(new)

    def run(self):
        global active_clock_id
        if self.id == active_clock_id:
            self.update()
            rest = 60 - int(datetime.now().strftime('%S'))
            sublime.set_timeout(self.run, rest * 1000)
        # else:
        #     print 'dropped clock', self.id

class ClockListener(sublime_plugin.EventListener):

    def __init__(self, *args, **kwargs):
        self.clock = Clock()
        self.clock.run()

    def on_load(self, view):
        if view_is_widget(view) and view.is_visible():
            return
        # import os
        # print 'load', type(view), view.id(), os.path.basename(view.file_name())
        self.clock.add_view(view)

    def on_post_save(self, view):
        if view_is_widget(view) and view.is_visible():
            return
        # import os
        # print 'post_save', type(view), view.id(), os.path.basename(view.file_name())
        self.clock.add_view(view)

    def on_activated(self, view):
        if view_is_widget(view):
            return
        # import os
        # print 'activated', view.id(), os.path.basename(view.file_name())
        self.clock.add_view(view)

    def on_deactivated(self, view):
        if view_is_widget(view):
            return
        # import os
        # print 'deactivated', view.id(), os.path.basename(view.file_name())
        self.clock.del_view(view)
