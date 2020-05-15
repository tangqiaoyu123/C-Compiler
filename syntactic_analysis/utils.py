
EPSILON = "EPSILON"
SSTART = "SSTART"
START = "program"
END = "$"
EXPR = "expr"
REMAINING_WORD = ["id", "decimal", "octal", "hex", "float_num", "character", "string"]

def epsilon_analysis(symbols, symbol2terminal, grammar):
    for i in symbols:
        if symbol2terminal[i] and i != EPSILON:
            return False
        elif not symbol2terminal[i] and [EPSILON] not in grammar[i]:
            return False
    return True


firsts = {}
on_cal = []


def simple_first(symbol, symbol2terminal, grammar):
    if firsts.get(symbol, -1) != -1:
        return firsts[symbol]
    on_cal.append(symbol)
    fi = []
    if symbol2terminal[symbol]:
        fi.append(symbol)
        return fi
    else:
        for i in grammar[symbol]:
            for j in range(len(i)):
                if i[j] in on_cal: continue
                if epsilon_analysis(i[0:j], symbol2terminal, grammar):
                    fi.extend(simple_first(i[j], symbol2terminal, grammar))
                else:
                    break

    firsts[symbol] = list(set(fi))
    on_cal.remove(symbol)
    return firsts[symbol]


def first(symbols, symbol2terminal, grammar):

    fi = []
    extended = []
    for i in symbols:
        if i not in extended:
            sf = simple_first(i, symbol2terminal, grammar)
            fi.extend(sf)
            extended.append(i)
            if EPSILON not in sf:
                break
            else:
                fi.remove(EPSILON)
    if epsilon_analysis(symbols, symbol2terminal, grammar):
        fi.append(EPSILON)
    return list(set(fi))


def expr2grammar(expr):
    gra = {EXPR: []}
    prio = sorted(list(expr.keys()), reverse=True)
    curr = EXPR
    ind = 1
    for i in prio:
        next = EXPR + str(ind)
        gra[curr].append([next])
        combine = expr[i][0]
        tmp = expr[i][1]
        for j in range(len(tmp)):
            if 'A' in tmp[j]:
                if 'B' not in tmp[j]:
                    tmp[j] = [next if _ == "A" else _ for _ in tmp[j]]
                else:
                    if combine == 0:
                        tmp[j] = [curr if _ == "A" else _ for _ in tmp[j]]
                        tmp[j] = [next if _ == "B" else _ for _ in tmp[j]]
                    else:
                        tmp[j] = [curr if _ == "B" else _ for _ in tmp[j]]
                        tmp[j] = [next if _ == "A" else _ for _ in tmp[j]]
            gra[curr].append(tmp[j])

        if i != prio[-1]:
            gra[next] = []
        else:
            gra[curr] = [[EXPR if j == next else j for j in i] for i in gra[curr]]
            gra[curr].remove([EXPR])
        ind += 1
        curr = next
    return gra


def read_grammar(gfile='./simple_grammar.txt', efile='./simple_expr.txt'):
    gra = {}
    with open(gfile) as f:
        for line in f.readlines():
            if line == "\n": continue
            line = line.replace('\n', '')
            line = line.replace('\\n', '\n')
            ll = line.split(" ")
            gra[ll[0]] = gra.get(ll[0], [])
            gra[ll[0]].append(ll[1:])

    expr = {}
    with open(efile) as f:
        tmp = []
        prio = -1
        for line in f.readlines():
            if prio == -1:
                if line == "\n": continue
                else:
                    line = line.replace('\n', '')
                    ll = line.split(" ")
                    prio = int(ll[0])
                    tmp.append(int(ll[1]))
            elif line == "\n":
                expr[prio] = tmp
                tmp = []
                prio = -1
            else:
                line = line.replace('\n', '')
                if len(tmp) == 0:
                    print(line)
                    raise Exception("error!")
                if len(tmp) == 1:
                    tmp.append([])
                tmp[1].append(line.split(" "))
        if prio != -1 and tmp != []:
            expr[prio] = tmp
    gra2 = expr2grammar(expr)
    gra.update(gra2)
    return gra


if __name__ == "__main__":
    print(read_grammar())
