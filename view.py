
import sublime
import sublime_plugin


def get_return(var_label):
    ret = sublime.load_settings("return_drop_file.sublime-settings")
    return ret.get(var_label)


class viewmanagerCommand(sublime_plugin.WindowCommand):
    """
    """

    active_explorer_windows = {}

    def run(self, method, label):
        """
        """

        ret = sublime.load_settings(
            'return_drop_file.sublime-settings')

        (return_id, return_label) = getattr(self, method)(label)

        ret.set("view_id", return_id)
        ret.set("label", return_label)

    def create_new_view(self, label):
        """
        """

        # Create file
        self.window.new_file()
        self.window.active_view().set_scratch(True)
        self.window.active_view().set_name(label)

        view_id = self.window.active_view().id()

        # log the ID and label in the database
        self.active_explorer_windows.update(
            {view_id: label})

        return((view_id, label))

    def is_registered_view(self, label):
        """
        """

        # get current view ID
        current_view = self.window.active_view().id()

        # current_view found => provide the corresponding filepath
        if(current_view in self.active_explorer_windows):
            return((current_view, self.active_explorer_windows[current_view]))
        else:
            return((0, ""))

    def close_if_registered(self, label):

        if self.is_registered_view(""):
            return self.close_view("")
        else:
            return ((0, ""))

    def close_view(self, label):
        """
        """

        # get current view
        view_id = self.window.active_view().id()
        # deregister view_id
        del(self.active_explorer_windows[view_id])
        # close current view.
        self.window.run_command("close")

        return((view_id, label))


class inserttextCommand(sublime_plugin.TextCommand):
    """Base insert text command

    Since sublime 'edit' objects can only be created by TextCommands, any
    view edits must pass through an external command.

    Usage
    -----
    self.window.run_command(
        "inserttext", {
            "text": text_to_insert,
            "point": sublime_text_point
        })
    """

    def run(self, edit, text, point):

        self.view.insert(edit, point, text)
