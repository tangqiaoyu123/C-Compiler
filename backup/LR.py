from utils import *

remaining_word = ["id", "decimal", "octal", "hex", "float_num", "character", "string"]

class Item:
    id = 0
    id2item = []

    def __init__(self, left, right, dot, pre):
        self.iid = Item.id
        Item.id2item.append(self)
        Item.id += 1
        self.left = left
        self.right = right
        self.dot = dot
        self.pre = pre
        self.end = self.dot == len(self.right)

    def move(self):
        return Item.get(self.left, self.right, self.dot+1, self.pre)

    def __str__(self):
        r = self.left + ' -> '
        for i in self.right[:self.dot]:
            r += i + " "
        r += " . "
        for i in self.right[self.dot:]:
            r += i + " "
        r += " | " + self.pre
        return r

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.left == other.left and self.right == other.right and self.dot == other.dot and self.pre == other.pre

    @staticmethod
    def get(left, right, dot, pre):
        if type(right) == str:
            right = [right]
        for i in range(len(Item.id2item)):
            it = Item.id2item[i]
            if left == it.left and right == it.right and dot == it.dot and pre == it.pre:
                return i
        return Item(left, right, dot, pre).iid


class LR:
    def __init__(self):
        self.terminal_symbols = []
        self.nonterminal_symbols = []
        self.symbol2terminal = {}
        self.grammar = read_grammar()
        self.get_symbols()
        self.firsts = {}
        self.closures = {}
        self.gotos = {}

    def closure(self, items):
        aaaa = str(items)
        if self.closures.get(aaaa, -1) != -1:
            return self.closures[aaaa]
        it = items[:]
        it2 = it[:]
        while len(it) != 0:
            i = Item.id2item[it[0]]
            if not i.end and not self.symbol2terminal[i.right[i.dot]]:
                tmp = EPSILON if len(i.right) == i.dot+1 else i.right[i.dot+1]
                aaa = str(tmp) + " " + str(i.pre)
                self.firsts[aaa] = self.firsts.get(aaa, first([tmp, i.pre], self.symbol2terminal, self.grammar))
                f = self.firsts[aaa]
                for j in f:
                    if j == EPSILON: continue
                    for k in self.grammar[i.right[i.dot]]:
                        ii = Item.get(i.right[i.dot], k, 0, j)
                        if ii in it2: continue
                        it2.append(ii)
                        it.append(ii)
            it.pop(0)
        self.closures[aaaa] = it2[:]
        return self.closures[aaaa]

    def goto(self, items, symbol):
        aaaa = str(items) + "|" + str(symbol)
        if self.gotos.get(aaaa, -1) != -1:
            return self.gotos[aaaa]
        out = []
        for j in items:
            i = Item.id2item[j]
            if not i.end and i.right[i.dot] == symbol:
                out.append(i.move())
        self.gotos[aaaa] = self.closure(out)
        return self.gotos[aaaa]

    def get_items(self):
        items = [self.closure([Item.get(SSTART, START, 0, END)])]
        # print(items)
        # for i in Item.id2item:
        #     print(i)
        transfer = {0: {}}
        items2 = [self.closure([Item.get(SSTART, START, 0, END)])]
        offset = 0
        while len(items) != 0:
            print("----------------------------------------", len(items), len(items2), len(Item.id2item))
            items[0] = list(set(items[0]))
            out = items[0]
            out = list(set(out))
            # print("out: ", out)
            # print(transfer)
            # print("&&&&", items2)
            # # if len(items2) > 5:
            # #     print("hhh: ", items2[1])
            # #     print("aaa: ", items2[5])
            # #     break
            tt = {}
            while len(out) != 0:
                # print("---------------------", len(out))
                # if len(out) == 263:
                #     print(out)
                    # exit(0)
                i = out[0]
                # print("*********", i)
                # print("i: ", i)
                # ttttt = 0
                for j in self.symbol2terminal.keys():
                    # print(ttttt + 1)
                    # ttttt += 1
                    # if ttttt == 67:
                    #     print(j)

                        # print(len(tmp))
                    if j == EPSILON: continue
                    tmp = self.goto([i], j)
                    # print("  ", len(tmp))
                    # print("tmp: ", tmp)
                    tt[j] = tt.get(j, [])

                    for tm in tmp:
                        if tm not in tt[j]:
                            tt[j].append(tm)
                out.pop(0)
            for tk, tv in tt.items():
                if len(tv) == 0: continue
                index = len(items2)
                for its in range(len(items2)):
                    if items2[its] == tv:
                        index = its
                if index == len(items2):
                    items2.append(tv[:])
                    items.append(tv[:])
                transfer[offset][tk] = index
                transfer[index] = transfer.get(index, {})
            items.pop(0)
            offset += 1
        return transfer, items2

    def transfer(self, trans, items):
        def check_lr1(index, post, i, it):
            pre = action[i].get(index, -1)

            if pre != -1 and pre != post:
                print(it)
                print(pre)
                print(i)
                print(index)
                print(post)
                raise Exception("NOT LR(1)!!!")
            else:
                action[i][index] = post

        action = {i: {} for i in range(len(items))}
        goto = {i: {} for i in range(len(items))}
        for i in range(len(items)):
            for j in items[i]:
                it = Item.id2item[j]
                print(it)
                if not it.end:
                    if self.symbol2terminal[it.right[it.dot]]:
                        print(i, trans[i][it.right[it.dot]])
                        check_lr1(it.right[it.dot], (1, trans[i][it.right[it.dot]]), i, it)
                    else:
                        goto[i][it.right[it.dot]] = trans[i][it.right[it.dot]]
                if it.end and it.left != SSTART:
                    check_lr1(it.pre, (2, it.left, it.right), i, it)
                if it.end and it.left == SSTART and it.pre == END:
                    check_lr1(it.pre, (0,), i, it)

        return action, goto

    def analysis_text(self, text, action, goto):
        stack = [0]
        inp = text[:] + [END]
        i = 0
        while i < len(inp):
            print(len(inp), i)
            print("analysis...  ", inp[i])
            act = action[stack[-1]].get(inp[i], ())
            print(act)
            if len(act) == 0:
                raise Exception("Error")
            elif len(act) == 1:
                print("ok")
                return True
            elif len(act) == 2:
                stack.append(act[1])
                i += 1
            elif len(act) == 3:
                tmp = len(act[2])
                stack = stack[:len(stack) - tmp]
                stack.append(goto[stack[-1]][act[1]])

            # print(stack)

    def analysis_tokens(self, tokens):
        text = []
        for i in tokens:
            if i.ttype == "id":
                text.append(i.ttype)
            else:
                text.append(i.value)
        t, aa = self.get_items()
        # print("haha")
        with open("./ti.txt", "w") as f:
            for i in t:
                f.write(str(i))
                f.write('\n')
            f.write("\n\n\n")
            for i in aa:
                f.write(str(i))
                f.write('\n')
            f.write("\n\n\n")
            for i in Item.id2item:
                f.write(str(i))
                f.write('\n')
        #         # exit(0)
        a, g = self.transfer(t, aa)
        with open("./ac.txt", "w") as f:
            for i in a:
                f.write(str(i))
                f.write('\n')
            f.write("\n\n\n")
            for i in g:
                f.write(str(i))
                f.write('\n')
        self.analysis_text(text, a, g)

    def get_symbols(self):
        import json
        conf = json.load(open('../lexical_analysis/config.json'))
        keywords = conf["keyword"]
        punctuators = conf["punctuator"]
        for i in keywords:
            if i not in self.terminal_symbols:
                self.terminal_symbols.append(i)
        for k, v in punctuators.items():
            for i in v:
                if i not in self.terminal_symbols:
                    self.terminal_symbols.append(i)
        self.terminal_symbols.extend(remaining_word)
        self.terminal_symbols.append(EPSILON)
        self.terminal_symbols.append(SSTART)
        self.terminal_symbols.append(END)
        print(self.terminal_symbols)
        for gk, gv in self.grammar.items():
            if gk not in self.terminal_symbols:
                self.nonterminal_symbols.append(gk)
        print(self.nonterminal_symbols)
            # for i in gv:
            #     for j in i:
            #         if i not in self.terminal_symbols:
            #             self.terminal_symbols.append(i)
        for i in self.terminal_symbols:
            self.symbol2terminal[i] = True
        for i in self.nonterminal_symbols:
            self.symbol2terminal[i] = False
        print(self.symbol2terminal)


if __name__ == "__main__":
    from lexical_analysis.lexicalAnalysis import LexicalAnalyzer
    la = LexicalAnalyzer()
    a, b = la.analysis_file("../lexical_analysis/test2.c")
    lr = LR()
    print(lr.grammar)
    print(lr.analysis_tokens(a))
    # for i in lr.nonterminal_symbols:
    #     print(i)
    #     print(first([i], lr.symbol2terminal, lr.grammar))
