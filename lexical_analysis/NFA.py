
letters = [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)] + ["_"]
digits = [chr(i) for i in range(48, 58)]
EPSILON = "epsilon"


class NFANode:
    node_id = 0
    id2nodes = {}

    def __init__(self):
        self.id = NFANode.node_id
        NFANode.node_id += 1
        NFANode.id2nodes[self.id] = self
        self.transfer = {}
        self.acc = False
        self.token_type = None

    def add_edge(self, chars, node):
        for char in chars:
            self.transfer[char] = self.transfer.get(char, [])
            self.transfer[char].append(node)
        return node

    def add_edge2self(self, chars):
        return self.add_edge(chars, self)

    def add_edge2new(self, chars):
        return self.add_edge(chars, NFANode())

    def set_end(self, token_type):
        self.acc = True
        self.token_type = token_type
        return self

    def __str__(self):
        s = str(self.id) + ": " + str(self.token_type) + "\n"
        for k, i in self.transfer.items():
            s += k + ": "
            for j in i:
                s += str(j.id) + ", "
            s += "\n"
        return s


def get_digits(start, end):
    d = []
    for i in range(start, end+1):
        if i < 10:
            d += chr(48+i)
        elif i < 16:
            d += chr(55+i)
            d += chr(87+i)
    return d


class NFA:
    def __init__(self, keywords, punctuators):
        self.keywords = keywords
        self.punctuators = punctuators
        self.start = NFANode()
        self.chars = [chr(i) for i in range(32, 127)] + ['\n', '\t']
        self.accept_states = []

    def get_accepts(self):
        acc = {}
        for i in self.accept_states:
            try:
                acc[i] = NFANode.id2nodes[i].token_type
            except KeyError as e:
                print(e)
                print(i)
                exit(-1)
        return acc

    def simple_connect(self, word, token_type):
        start = NFANode()
        tmp = start
        for i in word:
            tmp = tmp.add_edge2new([i])
        tmp.set_end(token_type)
        self.accept_states.append(tmp.id)
        return start

    def build_keyword(self):
        starts = []
        for i in self.keywords:
            starts.append(self.simple_connect(i, i))
        return starts

    def build_zid(self):
        s = NFANode()
        tmp = s.add_edge2new(letters)
        tmp.set_end("id")
        tmp.add_edge2self(letters).add_edge2self(digits)
        self.accept_states.append(tmp.id)
        return [s]

    def build_punctuator(self):
        starts = []
        for k, v in self.punctuators.items():
            for i in v:
                starts.append(self.simple_connect(i, k))
        return starts

    def build_integer_dec(self):
        digits_19 = get_digits(1, 9)
        s_dec = NFANode()
        self.accept_states.append(s_dec.add_edge2new(["+", "-", EPSILON])
                                  .add_edge2new(digits_19).add_edge2self(digits).set_end("decimal").id)
        return [s_dec]

    def build_integer_oct(self):
        s_oct = NFANode()
        digits_07 = get_digits(0, 7)
        self.accept_states.append(s_oct.add_edge2new(["+", "-", EPSILON]).add_edge2new(["0"])
                                  .add_edge2self(digits_07).set_end("octal").id)
        return [s_oct]

    def build_number_hex(self):
        s_oct = NFANode()
        digits_0f = get_digits(0, 15)
        self.accept_states.append(s_oct.add_edge2new(["+", "-", EPSILON]).add_edge2new(["0"])
                                  .add_edge2new(["x", "X"]).add_edge2new(digits_0f)
                                  .add_edge2self(digits_0f).set_end("hex").id)
        return [s_oct]

    def build_float(self):
        f1 = NFANode()
        tmp = f1.add_edge2new(["+", "-", EPSILON]).add_edge2new(digits).add_edge2self(digits)\
            .add_edge2new(["."]).set_end("float_num")
        f2 = NFANode()
        tmp2 = f2.add_edge2new(["+", "-", EPSILON]).add_edge2self(digits).add_edge2new(["."])\
            .add_edge2new(digits).add_edge2self(digits).set_end("float_num")
        f3 = NFANode()
        tmp3 = f3.add_edge2new(["+", "-", EPSILON]).add_edge2new(digits).add_edge2self(digits)
        exp = tmp.add_edge2new(["E", "e"])
        tmp2.add_edge(["E", "e"], exp)
        tmp3.add_edge(["E", "e"], exp)
        self.accept_states.append(exp.add_edge2new(["+", "-", EPSILON])
                                  .add_edge2new(digits).add_edge2self(digits).set_end("float_num").id)
        self.accept_states += [tmp.id, tmp2.id]
        return [f1, f2, f3]

    def build_char(self):
        special_chars = [chr(i) for i in range(32, 127)]
        special_chars.remove('\'')
        special_chars.remove('\\')
        s = NFANode()
        t1 = s.add_edge2new(['\''])
        t2 = t1.add_edge2new(special_chars).add_edge2new(['\''])
        t1.add_edge2new(['\\']).add_edge2new\
            (['\'', '"', '?', '\\', 'a', 'b', 'f', 'n', 'r', 't', 'v']).add_edge(['\''], t2)
        t2.set_end("character")
        self.accept_states.append(t2.id)
        return [s]

    def build_string(self):
        special_chars = [chr(i) for i in range(32, 127)]
        special_chars.remove('"')
        special_chars.remove('\\')
        s = NFANode()
        t1 = s.add_edge2new(['"'])
        t2 = t1.add_edge2self(special_chars).add_edge2new(['\"'])
        t1.add_edge2new(['\\']).add_edge(['\'', '"', '?', '\\', 'a', 'b', 'f', 'n', 'r', 't', 'v'], t1)
        t2.set_end("string")
        self.accept_states.append(t2.id)
        return [s]

    def build_comment(self):
        special_chars = [chr(i) for i in range(32, 127)]
        special_chars.remove('*')
        s = NFANode()
        t1 = s.add_edge2new(['/'])
        e1 = t1.add_edge2new(['/']).add_edge2self([chr(i) for i in range(32, 127)]).add_edge2new(['\n']).set_end("comments")
        t2 = t1.add_edge2new(['*']).add_edge2self(special_chars + ['\n'])
        t3 = t2.add_edge2new(['*']).add_edge2self(['*'])
        special_chars.remove('/')
        t3.add_edge(special_chars, t2)
        e2 = t3.add_edge2new(['/']).set_end("comments")
        self.accept_states += [e1.id, e2.id]
        return [s]

    def buildNFA(self):
        for i in dir(self):
            if i.startswith("build_"):
                tmp = getattr(self, i)()
                for j in tmp:
                    self.start.add_edge([EPSILON], j)
# def build_NFA():


# if __name__ == "__main__":
#     import json
#     conf = json.load(open("./config.json"))
#     keyword_list = conf["keyword"]
#     punctuator = conf["punctuator"]
#     a = NFA(keyword_list, punctuator)
#     a.buildNFA()
#     for i in NFANode.id2nodes.values():
#         print(i)
#     d = DFA.NFA2DFA(a)
#     print("="*30)
#     print(a.accept_states)
#     print(len(d.transfer_matrix))
#     print(d.accept_states)
#
#     aa = "elseb "
#     for i in aa:
#         print(d.move(i))