
import os
import subprocess
import sublime_plugin

from .view import get_return


class ctrlshellCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.window.show_input_panel(
            ": ", "", self.on_done, None, None)

    def on_done(self, text):

        self.window.run_command(
            "viewmanager", {"method": "is_registered_view", "label": ""})
        view_id = get_return("view_id")
        previous = get_return("label")

        if view_id != 0:
            self.window.run_command(
                "viewmanager", {"method": "close_view", "label": ""})

        if text == "...":
            self.__show_proj()
        else:
            targetpath = None
            if previous == '// Project Folders //':
                for folder in self.window.folders():
                    if os.path.basename(folder) == text:
                        targetpath = folder
                        break

            if targetpath is None:
                targetpath = os.path.expanduser(text)

            try:
                os.chdir(targetpath)
                self.__show(self.__get_ls())
            except (FileNotFoundError, NotADirectoryError):
                self.__open_file(text)

    def __get_ls(self, target=None):

        if target is not None:
            current = os.getcwd()
            os.chdir(target)

        fpath = os.path.basename(os.getcwd())
        ret = subprocess.check_output(["ls", "-l", "-a"]).decode("utf-8")

        if target is not None:
            os.chdir(current)

        base = "{div}\n|   {fpath}   |  \n{div}\n".format(
            fpath=fpath, div='-' * (len(fpath) + 8))

        return "{base}[{fullpath}]\n\n{ret}".format(
            ret=ret,
            fullpath=os.getcwd(),
            base=base,)

    def __show_proj(self):

        self.__show(
            "\n".join([
                self.__get_ls(folder)
                for folder in self.window.folders()]),
            label="// Project Folders //")

    def __show(self, text, label=None):

        self.window.run_command(
            "viewmanager", {
                "method": "create_new_view",
                "label": os.getcwd() if label is None else label
            })

        self.window.active_view().run_command(
            "inserttext", {"text": text, "point": 0})

    def __open_file(self, filename):

        self.window.open_file(os.path.join(os.getcwd(), filename))

