from LR import *
from graphviz import Digraph
import sys
sys.path.append("..")
from lexical_analysis.lexicalAnalysis import *


class Node:
    graph = Digraph("Syntax Tree")
    id = 0

    def __init__(self, token):
        self.id = Node.id
        Node.id += 1
        self.token = token
        self.value = token.ttype if token.ttype in REMAINING_WORD else token.value
        self.children = []
        self.key = self.token.value

    def add_children(self, ch):
        self.children.append(ch)
        return self

    def build_graph(self):
        # builded = [self]
        # while len(builded) != 0:
        #     a = builded.pop(0)
        #     print(a.key, [i.key for i in a.children])
        #     builded.extend(a.children)
        Node.graph.node(str(self.id), self.key)
        for i in self.children:
            Node.graph.node(str(i.id), i.key)
            Node.graph.edge(str(self.id), str(i.id))
            i.build_graph()

class SyntacticAnalyzer:
    def __init__(self, lr):
        self.lr = lr
        self.action = lr.action_matrix
        self.goto = lr.goto_matrix

    def analysis_text(self, text):
        stack = [0]
        inp = text[:] + [END]
        i = 0
        while i < len(inp):
            # print(len(inp), i)
            print("analysis...  ", inp[i])
            act = self.action[stack[-1]].get(inp[i], ())
            print(act)
            if len(act) == 0:
                raise Exception("Error")
            elif len(act) == 1:
                print("Congratulation!")
                return True
            elif len(act) == 2:
                stack.append(act[1])
                i += 1
            elif len(act) == 3:
                tmp = len(act[2])
                stack = stack[:len(stack) - tmp]
                stack.append(self.goto[stack[-1]][act[1]])

    def analysis_tokens(self, tokens):
        nodes = []
        text = []

        for i in tokens:
            nodes.append(Node(i))
            text.append(nodes[-1].value)
        stack = [0]
        nodes2 = []
        inp = text[:] + [END]
        print(inp)
        i = 0
        while i < len(inp):
            # print(len(inp), i)
            # print("analysis...  ", inp[i])
            # print(i)
            act = self.action[stack[-1]].get(inp[i], ())
            print(act)
            if len(act) == 0:
                raise Exception("Error")
            elif len(act) == 1:
                print("Congratulation!")
                return nodes2[0]
            elif len(act) == 2:
                stack.append(act[1])
                if nodes[i] == int:
                    exit(-1)
                nodes2.append(nodes[i])
                i += 1
            elif len(act) == 3:
                tmp = len(act[2])
                n = Node(Token("", act[1]))
                for a in range(tmp, 0, -1):
                    n.add_children(nodes2[len(nodes2)-a])
                    print(n.value, " -> ", nodes2[len(nodes2)-a].value)
                nodes2 = nodes2[:len(nodes2) - tmp]
                nodes2.append(n)
                stack = stack[:len(stack) - tmp]
                stack.append(self.goto[stack[-1]][act[1]])


if __name__ == "__main__":
    # g = Digraph('aaa')
    # g.node(name='a', color='red')
    # g.node(name='b', color='blue')
    # g.edge('a', 'b', color='green')
    # g.view()
    la = LexicalAnalyzer()
    a, b = la.analysis_file("../lexical_analysis/test.c")
    # lr = LR(grammar_file="./simple_grammar.txt", expr_file="./simple_expr.txt")
    # lr.save_action_goto("./ag.json")
    lr = LR.load_action_goto("./ag.json")
    sa = SyntacticAnalyzer(lr)
    root = sa.analysis_tokens(a)
    root.build_graph()
    Node.graph.view()

