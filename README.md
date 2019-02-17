# ctrl-shell
A sublime utility shell inspired by emacs' [ctrl+x, ctrl+f] behavior

## Installation
Copy the ```ctrl-shell``` directory to the ```sublime-text-3/Packages``` 

## ctrlshellCommand
Assigned to [ctrl+x, ctrl+f]; behaves like the open file command in Emacs. Enter a filepath; if the filepath is a directory, the directory contents will be displayed. If the filepath is a file, the file will be opened. If the filepath is neither a directory or file, a new file will be created at that filepath.

Several special commands are available:

- ```.proj```, ```...```: List current project folders
- ```.add <filepath>```: Add folder to current project
- ```.remove <basename>```: Remove folder from project folders
- ```.about```, ```.help```, ```.info```: Show information
- ```.cmd <command>```, ```.bash <command>```: Run command
