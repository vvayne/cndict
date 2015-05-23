
import sublime_plugin
import urllib.request
import urllib.error
from threading import Thread
from urllib.parse import quote
import json
import sublime


class CndictCommand(sublime_plugin.WindowCommand):

    def run(self, **kwargs):
        settings = sublime.load_settings("cndict.sublime-settings")
        self.args = settings.get("Default Dict")
        if 'dict' in kwargs.keys():
            self.args = kwargs['dict']
        window = self.window
        view = window.active_view()
        sel = view.sel()
        region = sel[0]
        word = view.substr(region)
        func = LookUpDict(window, word, self.args)
        func.start()


class LookUpDict(Thread):

    def __init__(self, window, word, args):
        Thread.__init__(self)
        self.window = window
        self.word = word
        self.args = args

    def checkword(self, word):
        if self.word == '':
            return False
        else:
            return True

    def acquiredata(self, word):
        if self.args == 'Youdao':
            request = "http://fanyi.youdao.com/openapi.do?keyfrom=divinites&key=1583185521&type=data&doctype=json&version=1.1&q=" + quote(self.word)
        elif self.args == 'Jinshan':
            request = "http://dict-co.iciba.com/api/dictionary.php?w="+quote(self.word)+"&type=json&key=0EAE08A016D6688F64AB3EBB2337BFB0"
        else:
            print("Invalid dictionary!")
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.URLError:
            raise Exception(u'网速不给力还是怎么回事，再试试？')

        data = response.read().decode('utf-8')
        return(json.loads(data))

    def format(self, json_data):
        snippet = ''
        if self.args == 'Youdao':
            if 'basic' in json_data:
                for explain in json_data['basic'].items():
                    if explain[0] == 'explains':
                        for i in explain[1:]:
                            snippet += '\n'.join(i)
                snippet += "\n------------------------\n"
            if "web" in json_data:
                for explain in json_data['web']:
                    net_explain = ','.join(explain['value'])
                    snippet += "{} : {}\n".format(explain['key'], net_explain)
        elif self.args == 'Jinshan':
            if 'symbols' in json_data:
                for explain in json_data['symbols'][0]['parts']:
                    if isinstance(explain['means'][0], str):
                        snippet += '{} : {}\n'.format(explain["part"], ','.join(explain["means"]))
                    if isinstance(explain['means'][0], dict):
                        for i in explain['means']:
                            snippet += '{}:{}\n'.format("释义", i["word_mean"])
                snippet += "\n------------------------\n"
        else:
            snippet += "可能太长了……词典里没有"
        return snippet

    def run(self):
        if self.checkword(self.word):
            json_data = self.acquiredata(self.word)
            snippet = self.format(json_data)
        else:
            snippet = "忘记选字了吧？"
        board = self.window.create_output_panel("tran")
        board.run_command('append', {'characters': snippet})
        self.window.run_command("show_panel", {"panel": "output.tran"})