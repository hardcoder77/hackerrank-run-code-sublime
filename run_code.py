import sublime, sublime_plugin, os
import sys


sys.path.append(os.path.dirname(__file__))
from hacker_rank_client import HackerRankClient

class HackerRankRunCommand(sublime_plugin.TextCommand):


    def run(self, edit):
        self.language_map = {"py": "python2"}
        file_name = self.get_file_name()
        problem_name = self.get_problem_name(file_name)
        extension = self.get_file_extension(file_name)
        language = self.get_language(extension)
        content = self.get_file_content()
        hacker_rank_client = HackerRankClient()
        hacker_rank_client.run_code(problem_name, language, content)

    def get_file_name(self):
        return os.path.basename(self.view.file_name())

    def get_problem_name(self, file_name):
        return os.path.splitext(file_name)[0]

    def get_language(self, extension):
        return self.language_map[extension]


    def get_file_extension(self, file_name):
        return os.path.splitext(file_name)[1][1:]

    def get_file_content(self):
        return self.view.substr(sublime.Region(0, self.view.size()))