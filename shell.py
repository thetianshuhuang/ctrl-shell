"""ctrlshell:
    ___ _       _ ___ _        _ _
   / __| |_ _ _| / __| |_  ___| | |
  | (__|  _| '_| \__ \ ' \/ -_) | |
   \___|\__|_| |_|___/_||_\___|_|_|
               v0.1 | Tianshu Huang

Sublime utility shell inspired by emacs' [ctrl+x, ctrl+f] behavior

Commands
--------
<filepath>
    Change directory and list files or open file and create if not present;
    emulates emacs' [ctrl+x, ctrl+f] behavior
.proj [aliases: ...]
    List current project folders
.add <filepath>
    Add folder to current project
.remove <basename>
    Remove folder from project folders
.about [aliases: .help, .info]
    Show information
.cmd [aliases: .bash] <command>
    Run command
.eval <command>
    Evaluate expression in python
"""

import os
import sys
import subprocess
import sublime_plugin

from .view import get_return


class ctrlshellCommand(sublime_plugin.WindowCommand):
    """ctrlshell Plugin Main Command

    Attributes
    ----------
    __PROJ_LABEL : str
        Label for command output of list project folders (.proj, alias '...')
    """

    __PROJ_LABEL = '// Project Folders //'
    __LS_COMMAND = {'posix': "ls -l -a", "nt": "dir"}
    __DOC = """
    ___ _       _ ___ _        _ _
   / __| |_ _ _| / __| |_  ___| | |
  | (__|  _| '_| \__ \ ' \/ -_) | |
   \___|\__|_| |_|___/_||_\___|_|_|
               v0.2 | Tianshu Huang

Sublime utility shell inspired by emacs' [ctrl+x, ctrl+f] behavior

Commands
--------
<filepath>
    Change directory and list files or open file and create if not present;
    emulates emacs' [ctrl+x, ctrl+f] behavior
.proj [aliases: ...]
    List current project folders
.add <filepath>
    Add folder to current project
.remove <basename>
    Remove folder from project folders
.about [aliases: .help, .info]
    Show information
.cmd [aliases: .bash] <command>
    Run command
.eval <command>
    Evaluate expression in python
"""

    def run(self):
        self.window.show_input_panel(
            ": ", "", self.on_done, None, None)

    def on_done(self, text):

        self.window.run_command(
            "viewmanager", {"method": "is_registered_view", "label": ""})
        view_id = get_return("view_id")
        previous = get_return("label")

        # Close current view if current view is a generated view
        if view_id != 0:
            self.window.run_command(
                "viewmanager", {"method": "close_view", "label": ""})

        sp = text.split(" ")
        base = sp[0]
        arg = " ".join(sp[1:])

        if base in ["...", ".proj"]:
            self.__show_proj()
        elif base in [".about", ".info", ".help"]:
            self.__show(self.__DOC)
        elif base in [".add"]:
            self.__add_folder(arg)
        elif base in [".remove"]:
            self.__remove(arg)
        elif base in [".cmd", ".bash"]:
            self.__cmd(arg)
        elif base in [".eval"]:
            self.__eval(arg)
        else:
            self.__file_explore(text, previous)

    def __eval(self, arg):
        """Evaluate python expression"""

        self.__show("[Python {ver}]\n>>> {expr}\n{val}\n".format(
            ver=sys.version.split(" ")[0],
            expr=arg,
            val=eval(arg)))

    def __cmd(self, text):
        """Execute shell command

        Parameters
        ----------
        text : str
            Command to run
        """

        self.__show(
            "[shell][{cwd}]: {cmd}\n\n{res}".format(
                cwd=os.getcwd(), cmd=text,
                res=subprocess.check_output(text, shell=True)
                .decode("utf-8")))

    def __remove(self, target):
        """Remove folder from project

        Parameters
        ----------
        target : str
            Folder to remove
        """

        f = self.window.project_data()
        f['folders'] = [
            folder for folder in f['folders'] if
            os.path.basename(folder['path']) != target]

        self.window.set_project_data(f)

    def __add_folder(self, target):
        """Add folder to project

        Parameters
        ----------
        target : str
            Folder to add (if present)
        """

        current = os.getcwd()

        try:
            os.chdir(os.path.expanduser(target))

            f = self.window.project_data()
            add = {'follow_symlinks': True, 'path': os.getcwd()}
            if not f:
                f = {'folders': [add]}
            else:
                f['folders'].append(add)

            self.window.set_project_data(f)

        except FileNotFoundError:
            print("Folder does not exist.")
        except NotADirectoryError:
            print("Target directory must be a folder.")
        finally:
            os.chdir(current)

    def __file_explore(self, target, previous):
        """Standard file-explorer command

        Parameters
        ----------
        target : str
            Target name
        previous : str
            Previous target
        """

        targetpath = self.__search_proj(target, previous)
        try:
            os.chdir(targetpath)
            self.__show(self.__get_ls())
        except (FileNotFoundError, NotADirectoryError):
            self.window.open_file(os.path.join(os.getcwd(), targetpath))

    def __search_proj(self, target, previous):
        """Search for a target basename in current open folders if the
        previous window was a project listing

        Parameters
        ----------
        target : str
            Target basename or filepath
        previous : str
            Previous name; triggers search if previous is project listing
        """

        # search in folders if previous is project folder listing
        if previous == self.__PROJ_LABEL:
            target = target.split(os.sep)[0]
            for folder in self.window.folders():
                if os.path.basename(folder) == target:
                    return folder
        # default - normal user input
        return os.path.expanduser(target)

    def __get_ls(self, target=None):
        """Get contents of target directory

        Parameters
        ----------
        target : str or None
            Target directory; if None, the current working dir is used.

        Returns
        -------
        str
            Result of 'ls -l -a' with added header
        """

        # Change directory
        if target is not None:
            current = os.getcwd()
            os.chdir(target)

        fpath = os.path.basename(os.getcwd())
        ret = subprocess.check_output(
            self.__LS_COMMAND[os.name], shell=True).decode("utf-8")

        # Restore working dir
        if target is not None:
            os.chdir(current)

        return "{div}\n|   {fpath}   |\n{div}\n[{fullpath}]\n\n{ret}".format(
            ret=ret,
            fullpath=target if target is not None else os.getcwd(),
            fpath=fpath,
            div='-' * (len(fpath) + 8))

    def __show_proj(self):
        """Show project folder contents"""

        self.__show(
            "\n".join([
                self.__get_ls(folder)
                for folder in self.window.folders()]),
            label=self.__PROJ_LABEL)

    def __show(self, text, label=None):
        """Show text in a new temp view

        Parameters
        ----------
        text : str
            Text to show
        label : str or None
            File label; if None, uses the current directory
        """

        self.window.run_command(
            "viewmanager", {
                "method": "create_new_view",
                "label": os.getcwd() if label is None else label
            })

        self.window.active_view().run_command(
            "inserttext", {"text": text, "point": 0})
