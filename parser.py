from collections import defaultdict, deque
import sys
import random
import string
sys.setrecursionlimit(10000)

class Concat:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Alt:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Group:
    def __init__(self, node, group_index):
        self.stared = False
        self.node = node
        self.group_index = group_index

class BackRef:
    def __init__(self, group_num):
        self.group_num = group_num

class GroupExprRef:
    def __init__(self, group_num):
        self.group_num = group_num

class Letter:
    def __init__(self, char):
        self.char = char

class GroupNumberStub:
    def __init__(self, num):
        self.num = num


def isNT(symbol : str) -> bool:
    return symbol[0] == '['


def getSetOFNTs(rule : list) -> set:
    return set([symbol for symbol in rule if isNT(symbol)])

class Grammar():

    def __init__(self):
        self.NT_To_Rules = defaultdict(list)
        self.rules = []
        self.allNTs = set([])
        self.terminals = set([])
        self.startingNT = None
        self.counter = 1

        self.first = defaultdict(set)
        self.last = defaultdict(set)
        self.follow = defaultdict(set)
        self.precede = defaultdict(set)
        self.followNT = defaultdict(set)
        self.bigramms = defaultdict(set)

        self.NT_To_T_Rules = defaultdict(list)
        self.NT_To_NT_Rules = defaultdict(list)


    def readGrammar(self):
        self.NT_To_Rules['[rg]'] = [['[rg]', '[rg]'], 
                                    ['[rg]', '|', '[rg]'], 
                                    ['(', '[rg]', ')'], 
                                    ['(', '?', ':', '[rg]', ')'],
                                    ['(', '?', '[num]', ')'],
                                    ['[rg]', '*'],
                                    ['[l]'],
                                    ['\\', '[num]']]
        self.NT_To_Rules['[l]'] = [[f'{letter}'] for letter in string.ascii_lowercase]
        self.NT_To_Rules['[num]'] = [[f'{num}'] for num in range(1, 10)]
        self.startingNT = '[rg]'
        self.updateGrammar()
    
    
    def prepareForParsing(self):
        self.HNFTransform()
        self.prepareForCYK()


    def updateGrammar(self):
        self.rules = []
        for NT, rightRules in self.NT_To_Rules.items():
            for rightRule in rightRules:
                self.rules.append((NT, rightRule))
        self.allNTs = set(self.NT_To_Rules.keys())

        self.terminals = set([])
        for _, rightRule in self.rules:
            self.terminals = self.terminals.union(set([symbol for symbol in rightRule if not isNT(symbol)]))


    def parseRule(self, s : str) -> list:
        newList = []
        i = 0
        while i < len(s):
            if s[i] == '[':
                start = i
                while s[i] != ']':
                    i += 1
                newList.append(s[start:i+1])
            else:
                if i < len(s) - 1 and s[i+1].isnumeric():
                    newList.append(s[i:i+2])
                    i += 1
                else:
                    newList.append(s[i])
            i += 1
        
        return newList
    

    def HNFTransform(self):
        self.deleteLongRules()
        self.deleteChainRules()
        self.deleteNonGenerative()
        self.deleteNonReacheble()
        self.deleteAloneTerminals()


    def deleteLongRules(self):
        for NT in self.allNTs:
            self.deleteLongRulesRecursion(NT)
        self.updateGrammar()
    

    def deleteLongRulesRecursion(self, NT : str):
        for i, rightRule in enumerate(self.NT_To_Rules[NT]):
            if len(rightRule) > 2:
                newNT = f"[new_NT_{NT + str(self.counter)}]"
                self.counter += 1
                self.NT_To_Rules[newNT] = [rightRule[1:]]
                newRightRule = [rightRule[0], newNT]
                self.NT_To_Rules[NT][i] = newRightRule
                self.deleteLongRulesRecursion(newNT)


    def deleteChainRules(self):
        visited = set([])
        self.deleteChainRulesRecursion(self.startingNT, visited)
        self.updateGrammar()


    def deleteChainRulesRecursion(self, NT_root : str, visited : set):
        visited.add(NT_root)
        for rightRule in self.NT_To_Rules[NT_root]:
            for NT in getSetOFNTs(rightRule):
                if NT not in visited:
                    self.deleteChainRulesRecursion(NT, visited)
        newRules = []
        for rightRule in self.NT_To_Rules[NT_root]:
            if len(rightRule) == 1 and isNT(rightRule[0]):
                newRules += self.NT_To_Rules[rightRule[0]]
            else:
                newRules.append(rightRule)
        self.NT_To_Rules[NT_root] = newRules.copy()


    def deleteNonGenerative(self):
        isGenerating = defaultdict(bool)
        counter = defaultdict(int)
        concernedRule = defaultdict(list)
        Q = deque()
        allNTs = set([])
        for i, (NT1, rightRule) in enumerate(self.rules):
            count = getSetOFNTs(rightRule)
            allNTs = allNTs.union(count, set([NT1]))
            for NT2 in count:
                concernedRule[NT2] += [i]
            counter[i] += len(count)
            if len(count) == 0:
                isGenerating[NT1] = True
                Q.append(NT1)
        for NT in allNTs:
            if not isGenerating[NT]:
                isGenerating[NT] = False

        visited = set([NT for NT in Q])
        while Q:
            for i in range(len(Q)):
                element = Q.popleft()
                for rule in concernedRule[element]:
                    counter[rule] -= 1
                    if counter[rule] == 0:
                        isGenerating[self.rules[rule][0]] = True
                        if self.rules[rule][0] in visited:
                            continue
                        Q.append(self.rules[rule][0])
                        visited.add(self.rules[rule][0])
        newRules = set([])
        for NT, val in isGenerating.items():
            if not val:
                newRules = set.union(newRules, set(set(concernedRule[NT])))
        self.rules = [rule for i, rule in enumerate(self.rules) if i not in newRules]
        self.NT_To_Rules = defaultdict(list)
        for NT, rightRule in self.rules:
            self.NT_To_Rules[NT] += [rightRule]
        self.updateGrammar()


    def deleteNonReacheble(self):
        rule2rule = defaultdict(list)
        NT_To_RuleNumber = defaultdict(list)
        RuleNumber_To_NTs = defaultdict(set)
        for i, (NT, rightRule) in enumerate(self.rules):
            NT_To_RuleNumber[NT] += [i]
            RuleNumber_To_NTs[i] = getSetOFNTs(rightRule)
        for RuleNumber, NTs in RuleNumber_To_NTs.items():
            for NT in NTs:
                if NT_To_RuleNumber[NT]:
                    rule2rule[RuleNumber] += NT_To_RuleNumber[NT]
        
        visited = set([])
        for ruleNumber, (NT, _) in enumerate(self.rules):
            if NT == self.startingNT:
                self.deleteNonReachebleRecursion(ruleNumber, visited, rule2rule)

        self.rules = [rule for i, rule in enumerate(self.rules) if i in visited]
        self.NT_To_Rules = defaultdict(list)
        for NT, rightRule in self.rules:
            self.NT_To_Rules[NT] += [rightRule]
        self.updateGrammar()


    def deleteNonReachebleRecursion(self, ruleNumber : int, visited : set, rule2rule : defaultdict):
        visited.add(ruleNumber)
        for next in rule2rule[ruleNumber]:
            if next not in visited:
                self.deleteNonReachebleRecursion(next, visited, rule2rule)


    def deleteAloneTerminals(self):
        newRules= {}
        for i, (NT, rightRule) in enumerate(self.rules):
            count = getSetOFNTs(rightRule)
            if len(rightRule) == 2 and len(count) < 2:
                if not isNT(rightRule[0]):
                    if rightRule[0] not in newRules:
                        newRules[rightRule[0]] = f'[NT_{NT}_To_{rightRule[0]}]'
                    self.rules[i][1][0] = newRules[rightRule[0]]
                if not isNT(rightRule[1]):
                    if rightRule[1] not in newRules:
                        newRules[rightRule[1]] = f'[NT_{NT}_To_{rightRule[1]}]'
                    self.rules[i][1][1] = newRules[rightRule[1]]
        for key, val in newRules.items():
            self.rules.append((val, [key]))
        
        self.NT_To_Rules = defaultdict(list)
        for NT, rightRule in self.rules:
            self.NT_To_Rules[NT] += [rightRule]
        self.updateGrammar()

    def printGrammar(self):
        for i, (NT, rightRule) in enumerate(self.rules):
            print(f'{i} ' + NT, '- >', "".join(rightRule))

    def printForCYK(self):
        print('T rules')
        for (NT, rightRules) in self.NT_To_T_Rules.items():
            for i, rule in enumerate(rightRules):
                print(f'{i} {NT} - > {"".join(rule)}')
        print('\nNT rules')
        for (NT, rightRules) in self.NT_To_NT_Rules.items():
            for i, rule in enumerate(rightRules):
                print(f'{i} {NT} - > {"".join(rule)}')
            

    def prepareForCYK(self):
        for NT, rightRule in self.rules:
            if len(rightRule) == 1:
                self.NT_To_T_Rules[NT].append(rightRule[0])
            else:
                self.NT_To_NT_Rules[NT].append(rightRule)

    
    def CYKforAST(self, word):
        d= {NT : [[False for _ in range(len(word))] for _ in range(len(word))] for NT in self.allNTs}
        nodes = {NT : [[None for _ in range(len(word))] for _ in range(len(word))] for NT in self.allNTs}
        for i in range(len(word)):
            for NT, rightRules in self.NT_To_T_Rules.items():
                for rightRule in rightRules:
                    if word[i] == rightRule:
                        d[NT][i][i]= True
                        if NT == '[num]':
                            nodes[NT][i][i] = GroupNumberStub(int(word[i]))
                        elif NT == '[rg]':
                            nodes[NT][i][i] = Letter(word[i])
                        
        for m in range(1, len(word)):
            for i in range(len(word) - m):
                j = i + m
                for NT, rightRules in self.NT_To_NT_Rules.items():
                    for ruleNumber, rightRule in enumerate(rightRules):
                        for k in range(i, j):
                            if d[rightRule[0]][i][k] and d[rightRule[1]][k+1][j]:
                                d[NT][i][j] = True
                                # ПОШЕЛ МЕГАХАРДКОД
                                if NT == '[rg]':
                                    if ruleNumber == 0:
                                        nodes[NT][i][j] = Concat(nodes[rightRule[0]][i][k], nodes[rightRule[1]][k+1][j])
                                    elif ruleNumber == 1:
                                        nodes[NT][i][j] = Alt(nodes[rightRule[0]][i][k], nodes[rightRule[1]][k+1][j])
                                    elif ruleNumber == 2:
                                        nodes[NT][i][j] = Group(nodes[rightRule[1]][k+1][j], 0)
                                    elif ruleNumber == 3:
                                        nodes[NT][i][j] = Group(nodes[rightRule[1]][k+1][j], -1)
                                    elif ruleNumber == 4:
                                        nodes[NT][i][j] = GroupExprRef(nodes[rightRule[1]][k+1][j].num)
                                    elif ruleNumber == 5:
                                        nodes[rightRule[0]][i][k].stared = True
                                        nodes[NT][i][j] = nodes[rightRule[0]][i][k]
                                    else:
                                        nodes[NT][i][j] = BackRef(nodes[rightRule[1]][k+1][j].num)
                                elif NT in ['[new_NT_[rg]1]', '[new_NT_[rg]3]', '[new_NT_[new_NT_[rg]3]4]', '[new_NT_[rg]6]']:
                                    nodes[NT][i][j] = nodes[rightRule[1]][k+1][j]
                                else:
                                    nodes[NT][i][j] = nodes[rightRule[0]][i][k]
        return d[self.startingNT][0][len(word)-1], nodes[self.startingNT][0][len(word)-1]


class CyclicError(Exception):
    pass

class AST:
    def __init__(self, regexp, grammar : Grammar):
        self.root = None
        self.grammar = grammar
        self.regexp = regexp
        self.groups = {}
        self.opened = set([])
        self.CFG = defaultdict(list)
        self.getAST()
        self.reindexGroups()
        self.checkIfValid()
        
        


    def getAST(self):
        valid, root = self.grammar.CYKforAST(self.regexp)
        if not valid:
            raise ValueError(f"{self.regexp} PARSING ERROR")
        else:
            self.root = root
            


    def reindexGroups(self):
        self.count = 1
        self.reindexGroupsRecursion(self.root)


    def reindexGroupsRecursion(self, root):
        if isinstance(root, Group):
            if root.group_index == 0:
                root.group_index = self.count
                self.groups[self.count] = root.node
                self.count += 1
            self.reindexGroupsRecursion(root.node)
        elif isinstance(root, (Concat, Alt)):
            self.reindexGroupsRecursion(root.left)
            self.reindexGroupsRecursion(root.right)
    

    def print_ast(self, node, indent=0):
        pre = "  " * indent
        if isinstance(node, Concat):
            print(pre + "Concat")
            self.print_ast(node.left, indent+1)
            self.print_ast(node.right, indent+1)
        elif isinstance(node, Alt):
            print(pre + "Alt")
            self.print_ast(node.left, indent+1)
            self.print_ast(node.right, indent+1)
        elif isinstance(node, Group):
            if node.stared:
                print(pre + 'Star')
                indent += 1
                pre += '  '
            print(pre + f"Group #{node.group_index}")
            self.print_ast(node.node, indent+1)
        elif isinstance(node, BackRef):
            print(pre + f"BackRef -> group {node.group_num}")
        elif isinstance(node, GroupExprRef):
            print(pre + f"GroupExprRef -> group {node.group_num}")
        elif isinstance(node, Letter):
            if node.char == '':
                print(pre + "ε (empty)")
            else:
                print(pre + f"Letter '{node.char}'")
        elif isinstance(node, GroupNumberStub):
            print(pre + f"GroupNumberStub({node.num})")

    
    def checkIfValid(self):
        try:
            self.valid(self.root, set([]), set([]))
            print(f'{self.regexp} OK')
            self.printCFG()
        except:
            print(f'{self.regexp} ERROR')


    def valid(self, root, opened, closed):
        if isinstance(root, Concat):
            new_closed = self.valid(root.left, opened, closed)
            return self.valid(root.right, opened, new_closed)
        elif isinstance(root, Alt):
            try:
                l_closed = self.valid(root.left, set(opened), set(closed))
            except CyclicError:
                r_closed  = self.valid(root.right, set(opened), set(closed))
                return r_closed
            else:
                try:
                    r_closed = self.valid(root.right, set(opened), set(closed))
                except CyclicError:
                    return l_closed
                else:
                    new_closed = l_closed.intersection(r_closed)
                    return new_closed
        elif isinstance(root, Group):
            new_closed = self.valid(root.node, opened, closed)
            if not root.stared:
                return closed.union(new_closed, set([root.group_index]))
            return closed
        elif isinstance(root, BackRef):
            if root.group_num not in closed:
                raise ValueError
            return closed
        elif isinstance(root, GroupExprRef):
            if root.group_num in opened:
                raise CyclicError
            if root.group_num not in self.groups:
                raise ValueError
            return self.valid(self.groups[root.group_num], opened.union(set([root.group_num])), closed)
        elif isinstance(root, Letter):
            return closed
    

    def makeCFG(self, root):
        if isinstance(root, Group):
            rules = self.makeCFG(root.node)
            if root.stared:
                for i in range(len(rules)):
                    rules.append(rules[i] + [f'G{root.group_index}'])
            self.CFG[f'G{root.group_index}'] =  rules
            return [[f'G{root.group_index}']]
        elif isinstance(root, Concat):
            leftPart = self.makeCFG(root.left)
            rightPart = self.makeCFG(root.right)
            rules = []
            for left in leftPart:
                for right in rightPart:
                    rules.append(left + right)
            return rules
        elif isinstance(root, Alt):
            return self.makeCFG(root.left) + self.makeCFG(root.right)
        elif isinstance(root, (BackRef, GroupExprRef)):
            return [[f'G{root.group_num}']]
        elif isinstance(root, Letter):
            return [[root.char]]
    
    
    def printCFG(self):
        print(f'S -> {'|'.join(map(lambda seq: "".join(seq), self.makeCFG(self.root)))}')
        for NT, rightRules in self.CFG.items():
            print(f'{NT} -> {'|'.join(map(lambda seq: "".join(seq), rightRules))}')
