
import sublime
import sublime_plugin


def get_return(var_label):
    """Get return value corresponding to a given label

    Parameters
    ----------
    var_label : str
        Key of return value to fetch from return_drop_file

    Returns
    -------
    arbitrary type
        Fetched return value
    """
    ret = sublime.load_settings("return_drop_file.sublime-settings")
    return ret.get(var_label)


class viewmanagerCommand(sublime_plugin.WindowCommand):
    """View Manager command for creating, tracking, and destroying generated
    views"""

    active_explorer_windows = {}

    def run(self, method, label):
        """Command run method (as per sublime API)

        Parameters
        ----------
        method : str
            Method to call
        label : str
            Parameter to pass to the called method (usually the name of
            the new view / file)

        Returns
        -------
        All returns via get_return // return_drop_file.sublime-settings
        view_id : int
            View ID of the created / destroyed / found view
        label : str
            View name
        """

        ret = sublime.load_settings(
            'return_drop_file.sublime-settings')

        try:
            (return_id, return_label) = getattr(self, method)(label)
            ret.set("view_id", return_id)
            ret.set("label", return_label)
        except AttributeError:
            print(
                "Method name not valid. Valid method names: "
                "create_new_view\n"
                "is_registered_view\n"
                "close_if_registered\n"
                "close_view")

    def create_new_view(self, label):
        """Create a new view with the provided label

        Parameters
        ----------
        label : str
            View label

        Returns
        -------
        (int, str)
            (Created View ID, View label (same as arg))
        """

        # Create file
        self.window.new_file()
        self.window.active_view().set_scratch(True)
        self.window.active_view().set_name(label)

        view_id = self.window.active_view().id()

        # log the ID and label in the database
        self.active_explorer_windows.update(
            {view_id: label})

        return (view_id, label)

    def is_registered_view(self, label):
        """Check if a given label corresponds to a registered view

        Parameters
        ----------
        label : str
            View name to check

        Returns
        -------
        (int, str)
            (view_id, view_label) if found; else (0, "")
        """

        # get current view ID
        current_view = self.window.active_view().id()

        # current_view found => provide the corresponding filepath
        if(current_view in self.active_explorer_windows):
            return((current_view, self.active_explorer_windows[current_view]))
        else:
            return((0, ""))

    def close_if_registered(self, label):
        """Check if a label is registered, and close it if it is.

        Parameters
        ----------
        label : str
            Ignored

        Returns
        -------
        (int, str)
            Same as is_registered_view.
        """

        if self.is_registered_view(""):
            return self.close_view("")
        else:
            return ((0, ""))

    def close_view(self, label):
        """Close the target view

        Parameters
        ----------
        label : str
            Ignored

        Returns
        -------
        (int, str)
            Same as is_registered_view.
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
