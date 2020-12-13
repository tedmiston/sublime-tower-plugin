"""
Open git repos from Sublime Text in Tower.

If you regularly open a shell to run `$ gittower .`, this is faster.
"""

import os.path
import subprocess

import sublime
import sublime_plugin


def build_cmd_is_in_repo(path):
    return 'cd "{}" && git rev-parse --is-inside-work-tree'.format(path)


def build_cmd_get_repo_root(path):
    return 'cd "{}" && git rev-parse --show-toplevel'.format(path)


def build_cmd_open_in_tower(path):
    return 'gittower "{}"'.format(path)


def is_in_repo(path):
    """
    Return true if current file is inside of a repo.
    """
    cmd = build_cmd_is_in_repo(path)
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                         shell=True, universal_newlines=True,
                                         timeout=2)
        return output.strip() == 'true'
    except subprocess.CalledProcessError as e:
        return False


def get_repo_root(path):
    """
    Determine the repo root directory from a nested path.
    """
    cmd = build_cmd_get_repo_root(path)
    output = subprocess.check_output(cmd, shell=True, universal_newlines=True,
                                     timeout=2)
    return output.strip()


def open_in_tower(path):
    """
    Open a repo in Tower.app [0], launching it if not running.

    [0]: https://www.git-tower.com/
    """
    cmd = build_cmd_open_in_tower(path)
    try:
        subprocess.check_output(cmd, shell=True, timeout=5)
    except subprocess.CalledProcessError as e:
        sublime.error_message(
            'Error: Tower CLI is not installed.\n\nEnable it at: Tower > '
            'Preferences... > Integration > Tower Command Line Utility'
        )


class TowerOpenCommand(sublime_plugin.TextCommand):
    """
    Open the repo of the currently viewed file in Tower.
    """

    def run(self, edit):
        """
        Sublime entrypoint.
        """
        current_file_path = self.view.file_name()

        if not current_file_path:
            msg = 'Error: Cannot open an unsaved file in Tower.'
            sublime.error_message(msg)
            return

        current_dir = os.path.dirname(current_file_path)

        if is_in_repo(current_dir):
            path = get_repo_root(current_dir)
            open_in_tower(path)

    def is_visible(self):
        current_file_path = self.view.file_name()
        
        if not current_file_path:
            return False

        current_dir = os.path.dirname(current_file_path)

        return is_in_repo(current_dir)        


class TowerOpenFromSidebarCommand(sublime_plugin.WindowCommand):
    """
    Open the repo of the given paths[] in Tower.
    paths[] may contain multiple files/directories if the user selected multiple
    elements from the Side Bar, hide the menu entry.
    """

    def run(self, paths):
        given_path = paths[0]
        
        if os.path.isfile(given_path):
            current_dir = os.path.dirname(given_path)
        else:
            current_dir = given_path

        if is_in_repo(current_dir):
            path = get_repo_root(current_dir)
            open_in_tower(path)

    def is_visible(self, paths):
        if len(paths) != 1:
            return False

        given_path = paths[0]

        if os.path.isfile(given_path):
            current_dir = os.path.dirname(given_path)
        else:
            current_dir = given_path

        return is_in_repo(current_dir)


class TowerCreateNewRepositoryFromSidebarCommand(sublime_plugin.WindowCommand):
    """
    If a single directory is given as argument, initialize Git repository
    with Tower.
    """

    def run(self, dirs):
        given_path = dirs[0]
        open_in_tower(given_path)           

    def is_visible(self, dirs):
        if len(dirs) != 1:
            return False

        given_path = dirs[0]

        if os.path.isfile(given_path):
            current_dir = os.path.dirname(given_path)
        else:
            current_dir = given_path

        return not is_in_repo(current_dir)
