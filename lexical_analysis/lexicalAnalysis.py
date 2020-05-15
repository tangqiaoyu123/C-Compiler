import json
from lexical_analysis.NFA import *
from lexical_analysis.DFA import DFA


class Token:
    def __init__(self, ttype, value):
        self.ttype = ttype
        self.value = value

    def __str__(self):
        return "{}, value: {}".format(str(self.ttype), str(self.value))

    def __repr__(self):
        return self.__str__()


class Reference:
    def __init__(self, filename, line_no, char_no):
        self.filename = filename
        self.line_no = line_no
        self.char_no = char_no


class Error:
    def __init__(self, filename, line_no, char_no, line, error_info):
        self.filename = filename
        self.line_no = line_no
        self.char_no = char_no
        self.line = line
        self.error_info = error_info

    def __str__(self):
        return "\033[31;31m  File \"{}\", line {}\n{}\n{}\n{}\n\033[0m".format(
            self.filename,
            self.line_no,
            self.line,
            self.char_no*" " + "^",
            self.error_info
        )

    def __repr__(self):
        return self.__str__()


class LexicalAnalyzer:
    def __init__(self, config_file="../lexical_analysis/config.json", continue_analysis_when_error=True):
        self.continue_analysis = continue_analysis_when_error

        conf = json.load(open(config_file))
        self.keywords = conf["keyword"]
        self.punctuators = conf["punctuator"]
        nfa = NFA(self.keywords, self.punctuators)
        nfa.buildNFA()
        self.DFA = DFA.NFA2DFA(nfa)

    def analysis_file(self, c_file):
        with open(c_file) as f:
            text = f.read()
        return self.analysis_text(text, c_file)

    def analysis_text(self, text, file="<input>"):
        tokens = []
        errors = []
        code_lines = 0
        comment_lines = 0
        total_chars = 0
        chars_until_last_line = 0
        lexical = {}

        text += ' '
        tlen = len(text)
        lines = text.split('\n')
        p_start = 0
        p_forward = 0
        while p_forward < tlen:
            pre, curr = self.DFA.move(text[p_forward])
            if pre != -1 and curr == -1:
                if pre != "delimiter" and pre != "comments":
                    word = text[p_start:p_forward]
                    tokens.append(Token(pre, word))
                    # print(tokens[-1])
                    lexical[word] = lexical.get(word, 0) + 1
                    total_chars += len(word)

                else:
                    if text[p_start:p_forward] == "\n":
                        code_lines += 1
                        chars_until_last_line = p_forward
                    elif pre == "comments":
                        tmp = text[p_start:p_forward].split('\n')
                        if tmp[-1] == "":
                            comment_lines += len(tmp) - 1
                        else:
                            comment_lines += len(tmp)
                            code_lines -= 1
                p_start = p_forward
                p_forward -= 1
                self.DFA.reset()
            elif pre == curr == -1:
                # p_forward -= 1
                t = ''
                errors.append(
                    Error(file, code_lines + comment_lines + 1, p_forward - chars_until_last_line,
                          lines[code_lines + comment_lines], "SyntaxError: invalid syntax"))
                print(errors[-1])
                while t not in self.punctuators["delimiter"] and p_forward < tlen-1:
                    p_forward += 1
                    t = text[p_forward]
                p_start = p_forward
                self.DFA.reset()


            p_forward += 1
        self.DFA.move('*')
        self.DFA.move('/')
        pre, cur = self.DFA.move(' ')
        if pre == "comments":
            errors.append(
                Error(file, len(lines), len(lines[-1]),
                      lines[-1], "SyntaxError: EOF while scanning comments, expect '*/' here. "))
            print(errors[-1])
        return tokens, errors


if __name__ == "__main__":
    la = LexicalAnalyzer()
    a, b = la.analysis_file("./test.c")


