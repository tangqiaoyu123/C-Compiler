from .NFA import *


def epsilon_closure(T):
    stack = [t.id for t in T]
    EC = [t.id for t in T]
    while len(stack) > 0:
        t = NFANode.id2nodes[stack.pop(-1)]
        for q in t.transfer.get(EPSILON, []):
            if q.id not in EC:
                EC.append(q.id)
                stack.append(q.id)
    return EC


class DFA:
    def __init__(self, start, chars, accept_states, transfer_matrix):
        self.start = start
        self.curr_state = self.start
        self.pre_state = self.curr_state
        self.chars = chars
        self.accept_states_dict = accept_states
        self.transfer_matrix = transfer_matrix

    @classmethod
    def NFA2DFA(cls, nfa):
        states = [epsilon_closure([nfa.start])]
        flags = [0]
        Dtran = [{}]
        while len(flags) != 0:
            i = flags.pop(0)
            for c in nfa.chars:
                moves = []
                for j in states[i]:
                    for mm in NFANode.id2nodes[j].transfer.get(c, []):
                        if mm not in moves:
                            moves.append(mm)
                U = epsilon_closure(moves)
                if len(U) != 0:
                    if U not in states:
                        states.append(U)
                        Dtran.append({})
                        flags.append(len(states) - 1)
                        Dtran[i][c] = len(states) - 1
                    else:
                        Dtran[i][c] = states.index(U)
                else:
                    Dtran[i][c] = -1
        acc = {}
        for i in range(len(states)):
            for k, v in nfa.get_accepts().items():
                if k in states[i]:
                    acc[i] = v
                    break
        return cls(0, nfa.chars, acc, Dtran)

    def move(self, char):
        self.pre_state = self.curr_state
        self.curr_state = self.transfer_matrix[self.curr_state][char] if self.curr_state != -1 else -1
        return self.accept_states_dict.get(self.pre_state, -1), self.curr_state

    def reset(self):
        self.curr_state = self.start


if __name__ == "__main__":
    import json
    conf = json.load(open("./config.json"))
    keyword_list = conf["keyword"]
    punctuator = conf["punctuator"]
    a = NFA(keyword_list, punctuator)
    a.buildNFA()
    # for i in NFANode.id2nodes.values():
    #     print(i)
    d = DFA.NFA2DFA(a)
    print("="*30)
    print(a.accept_states)
    print(a.get_accepts())
    print(d.transfer_matrix)
    print(d.accept_states_dict)
    aa = []
    for i in d.accept_states_dict.values():
        if i not in aa:
            aa.append(i)
    print(aa)

    bb = "0; "
    for i in bb:
        print(d.move(i))
