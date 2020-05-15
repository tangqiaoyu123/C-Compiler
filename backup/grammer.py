import json
from typing import List

# grammars = json.load(open('./grammar.json'))
# grammar = grammars["grammar"]
# operator_grammar = grammar["operator"]

EPSILON = "EPSILON"
HAS_EPSILON = True
SSTART = "SSTART"
START = "S"
END = "$"
terminal_symbols = [EPSILON, END, 'a', 'c', 'd']
nonterminal_symbols = [SSTART, 'S', 'A', 'B']
symbol2terminal = {}
for i in terminal_symbols:
    symbol2terminal[i] = True
for i in nonterminal_symbols:
    symbol2terminal[i] = False

# all grammar like S -> aA in cas is {"S": [["a", "A"]]}
cas = {SSTART: [['S']],
       'S': [['A', 'c', 'A', 'B']],
       'A': [['a', 'A'], ['d'], [EPSILON]],
       'B': [[EPSILON]]}


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
            r += i
        r += " . "
        for i in self.right[self.dot:]:
            r += i
        r += " | " + self.pre
        return r

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.left == other.left and self.right == other.right and self.dot == other.dot and self.pre == other.pre

    @staticmethod
    def get(left, right, dot, pre):
        for i in range(len(Item.id2item)):
            it = Item.id2item[i]
            if left == it.left and right == it.right and dot == it.dot and pre == it.pre:
                return i
        return Item(left, right, dot, pre).iid


def epsilon_analysis(symbols):
    for i in symbols:
        if symbol2terminal[i] and i != EPSILON:
            return False
        elif not symbol2terminal[i] and [EPSILON] not in cas[i]:
            return False
    return True


def simple_first(symbol):
    fi = []
    if symbol2terminal[symbol]:
        fi.append(symbol)
        return fi
    else:
        for i in cas[symbol]:
            if i == [EPSILON]:
                fi.extend(follow(symbol)[0])
                continue
            for j in range(len(i)):
                if epsilon_analysis(i[0:j]):
                    fi.extend(simple_first(i[j]))
                else:
                    break
    print(fi)
    return list(set(fi))


def first(symbols):
    fi = []
    for i in symbols:
        sf = simple_first(i)
        fi.extend(sf)
        if EPSILON not in sf:
            break
        else:
            fi.remove(EPSILON)
    if epsilon_analysis(symbols):
        fi.append(EPSILON)
    return list(set(fi))

follows = {}
def follow(symbol):
    if follows.get(symbol, -1) != -1:
        return follows[symbol]
    foT = []
    foN = []
    if symbol2terminal[symbol]:
        raise Exception("Only nonterminal symbol has follow. ")
    if symbol == SSTART:
        foT.append(END)
    for k, v in cas.items():
        for i in v:
            ind = []
            for j in range(len(i)):
                if symbol == i[j]:
                    ind.append(j)
            for index in ind:
                if index != -1 and index != len(i)-1:
                    if epsilon_analysis(i[index+1:]):
                        tmp = follow(k)
                        foT.extend(tmp[0])
                        foN.extend(tmp[1])
                    else:
                        foT.extend(first(i[index+1:]))
                        for mm in range(index+2, len(i)):
                            if epsilon_analysis(i[index+1:mm]):
                                if not symbol2terminal[i[mm]]:
                                    foN.append(i[mm])
                            else:
                                break
                elif index == len(i)-1:
                    if k in foN:
                        continue
                    if k != symbol:
                        tmp = follow(k)
                    else:
                        continue
                    foT.extend(tmp[0])
                    foN.extend(tmp[1])
    if EPSILON in foT:
        foT.remove(EPSILON)
    follows[symbol] = (list(set(foT)), list(set(foN)))
    return follows[symbol]


def closure(items: List):
    it = items[:]
    it2 = it[:]
    while len(it) != 0:
        i = Item.id2item[it[0]]
        # if i.right == [EPSILON]:
        # if i.right == [EPSILON]:
        #     for k in follow(i.left)[1]:
        #         for mm in cas[k]:
        #             print("999999999999999999999")
        #             ii = Item.get(k, mm, 0, i.pre)
        #             it2.append(ii)
        #             it.append(ii)
        if not i.end and not symbol2terminal[i.right[i.dot]]:
            tmp = EPSILON if len(i.right) == i.dot+1 else i.right[i.dot+1]
            f = first([tmp, i.pre])
            print([tmp, i.pre], f)
            for j in f:
                if j == EPSILON:
                    # print("hahahahhhhhhhhhhh")
                    # for k in follow(i.left)[1]:
                    #     for mm in cas[k]:
                    #         print("999999999999999999999")
                    #         ii = Item.get(k, mm, 0, i.pre)
                    #         it2.append(ii)
                    #         it.append(ii)
                    continue
                for k in cas[i.right[i.dot]]:
                    if k == [EPSILON]:
                        ii = i.move()
                    else:
                        ii = Item.get(i.right[i.dot], k, 0, j)
                    it2.append(ii)
                    it.append(ii)
        it.pop(0)
    return it2


def goto(items: List, symbol):
    out = []
    for j in items:
        i = Item.id2item[j]
        # if i == EPSILON
        if not i.end and i.right[i.dot] == symbol:
            out.append(i.move())
    return closure(out)


def get_items():
    items = [closure([Item.get(SSTART, START, 0, END)])]
    print("-------------------------", items)
    transfer = {0: {}}
    items2 = [closure([Item.get(SSTART, START, 0, END)])]
    offset = 0
    while len(items) != 0:
        out = items[0]
        # print("out: ", out)
        # print(transfer)
        # print("&&&&", items2)
        # # if len(items2) > 5:
        # #     print("hhh: ", items2[1])
        # #     print("aaa: ", items2[5])
        # #     break
        tt = {}
        while len(out) != 0:
            i = out[0]
            # print("i: ", i)
            for j in symbol2terminal.keys():
                if j == EPSILON:
                    if not HAS_EPSILON:
                        continue

                tmp = goto([i], j)
                # print(j, "tmp: ", tmp)
                tt[j] = tt.get(j, [])
                for tm in tmp:
                    if tm not in tt[j]:
                        tt[j].append(tm)
            out.pop(0)
        # print(tt)
        for tk, tv in tt.items():
            if len(tv) == 0: continue
            index = len(items2)
            for its in range(len(items2)):
                if items2[its] == tv:
                    index = its
            if index == len(items2):
                if tv[:] not in items2:
                    items2.append(tv[:])
                    items.append(tv[:])
            transfer[offset][tk] = index
            transfer[index] = transfer.get(index, {})
        items.pop(0)
        offset += 1
    return items2, transfer


def transfer(trans, items):
    def check_lr1(index, post):
        pre = action[i].get(index, -1)
        if pre != -1 and pre != post:
            raise Exception("NOT LR(1)!!!")
        else:
            action[i][index] = post
    action = {i:{} for i in range(len(items))}
    goto = {i:{} for i in range(len(items))}
    for i in range(len(items)):
        for j in items[i]:
            it = Item.id2item[j]
            if not it.end:
                if symbol2terminal[it.right[it.dot]]:
                    check_lr1(it.right[it.dot], (1, trans[i][it.right[it.dot]]))
                else:
                    goto[i][it.right[it.dot]] = trans[i][it.right[it.dot]]
            if it.end and it.left != SSTART:
                check_lr1(it.pre, (2, it.left, it.right))
            if it.end and it.left == SSTART and it.pre == END:
                check_lr1(it.pre, (0,))

    return action, goto


def analysis_text(text, action, goto):
    stack = [0]
    inp = text[:] + END
    i = 0
    while i < len(inp):
        act = action[stack[-1]].get(inp[i], ())
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
            stack = stack[:len(stack)-tmp]
            stack.append(goto[stack[-1]][act[1]])

        print(stack)


class Node:
    def __init__(self, token):
        self.type = token.type if token is not None else None
        self.value = token.value if token is not None else None
        self.children = []

    def __str__(self):
        if self.left is not None:
            return self.value + "[" + str(self.left) + ", " + str(self.middle) + ", " + str(self.right) + "]"
        elif self.middle is not None:
            return self.value + "[" + str(self.middle) + "]"
        else:
            return str(self.value)


if __name__ == "__main__":
    # for i in terminal_symbols:
    #     symbol2terminal[i] = True
    # for i in nonterminal_symbols:
    #     symbol2terminal[i] = False
    a, b = get_items()

    # items = [closure([Item.get(SSTART, START, 0, END)])]
    # print("-------------------------", items)
    print(Item.id2item)
    print(a)
    print(b)
    aa, bb = transfer(b,a)
    analysis_text("c", aa, bb)
