from typing import Any, Union

#import numpy
"""
from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
"""

class Graph():
    """Defining the logsim graph (assuming it's already been parsed)"""
    def __init__(self, names, devices, network, monitors):
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

    def create_boolean_from_monitor(self, monitor_name):
        """Generate boolean expression for monitor

        will return False if any circularity included (including flip-flops)"""
        mon_id = self.names.query(monitor_name)
        mon_dev = self.devices.get_device(mon_id)

        dev_list = self.devices.find_devices()

        # Check no flip flops / other 2-output devices
        for dev in dev_list:
            dev = self.devices.get_device(dev)
            if len(dev.outputs) != 1 or len(dev.inputs) > 2:
                print(dev.outputs)
                print('Flip-Flop/Not etc. present')
                return False

        def dfs(dev):
            """Doesn't yet deal with circular definitions"""
            dev_ins = dev.inputs
            if len(dev_ins) == 0:
                return self.names.get_name_string(dev.device_id)
            if len(dev_ins) == 1:  # not gate
                [out_dev_id] = dev_ins
                next_dev = self.devices.get_device(dev_ins[out_dev_id][0])
                return '¬('+dfs(next_dev)+')'
            i, j = dev_ins
            i_dev = self.devices.get_device(dev_ins[i][0])
            j_dev = self.devices.get_device(dev_ins[j][0])
            middle_char = ['.', '+', '.', '+', '*'][dev.device_kind]
            if dev.device_kind in (2, 3):
                return '¬(' + dfs(i_dev) + middle_char + dfs(j_dev) + ')'
            else:
                return '(' + dfs(i_dev) + middle_char + dfs(j_dev) + ')'

        return dfs(mon_dev)

    def get_sub_exp_end(self, bool_exp, i, left=True):
        if left:
            if bool_exp[i-1] == ')':
                j = 2
                bracket_count = 1
                while bracket_count:
                    if bool_exp[i-j] == ')':
                        bracket_count += 1
                    elif bool_exp[i-j] == '(':
                        bracket_count -= 1
                    j += 1
            else:
                j = 1
                while bool_exp[i-j] not in ('(', '.', '+', '*'):
                    j += 1
            return j - 1
        else:
            if bool_exp[i+1] == '(':
                k = 2
                bracket_count = 1
                while bracket_count:
                    if bool_exp[i+k] == '(':
                        bracket_count += 1
                    elif bool_exp[i+k] == ')':
                        bracket_count -= 1
                    k += 1
            else:
                k = 1
                while bool_exp[i+k] not in (')', '.', '+', '*'):
                    k += 1
            return k - 1

    def expand_xors(self, bool_exp):
        """Expands XORs in a given expression into ANDs/ORs"""
        n_xor = bool_exp.count('*')
        n = len(bool_exp)
        for w in range(n_xor):
            i = bool_exp.index('*')
            j = self.get_sub_exp_end(bool_exp, i, True)
            k = self.get_sub_exp_end(bool_exp, i, False)
            xor_exp = '(' + bool_exp[i-j:i] + '+' + bool_exp[i+1:i+k+1] + ').'
            xor_exp += '(¬' + bool_exp[i-j:i] + '+¬' + bool_exp[i+1:i+k+1] + ')'
            bool_exp = bool_exp[:i-j] + xor_exp + bool_exp[i+k+1:]

        return bool_exp

    def distribute_ors(self, bool_exp):
        """Distribute ORs over ANDs in pursuit of conjunctive normal form"""
        bool_exp0 = 0
        while bool_exp0 != bool_exp:
            bool_exp0 = bool_exp
            i = 0
            for n_or in range(bool_exp.count(')+')):
                i = bool_exp[i+1:].index(')+')+i+2
                j = self.get_sub_exp_end(bool_exp, i-1, True)
                if bool_exp[i-j-2] == '.':
                    jj = self.get_sub_exp_end(bool_exp, i-j-2, True)
                    k = self.get_sub_exp_end(bool_exp, i, False)
                    or_exp = '(' + bool_exp[i-j-2-jj:i-j-2] + bool_exp[i:i+k+1] + ').'
                    or_exp += '(' + bool_exp[i-j-1:i-1] + bool_exp[i:i+k+1] + ')'
                    bool_exp = bool_exp[:i-j-3-jj] + or_exp + bool_exp[i+k+1:]
                    break

            i = 0
            for n_or in range(bool_exp.count('+(')):
                i = bool_exp[i+1:].index('+(') + i+1
                j = self.get_sub_exp_end(bool_exp, i+1, False)
                if bool_exp[(i+1)+j+1] == '.':
                    jj = self.get_sub_exp_end(bool_exp, i+2+j, False)
                    k = self.get_sub_exp_end(bool_exp, i, True)
                    or_exp = '(' + bool_exp[i-k:i+1] + bool_exp[i+2:i+j+2] + ').'
                    or_exp += '(' + bool_exp[i-k:i+1] + bool_exp[i+j+3:i+j+3+jj] + ')'
                    bool_exp = bool_exp[:i-k] + or_exp + bool_exp[i+j+4+jj:]
                    break
        return bool_exp

    def clean_up_to_cnf(self, bool_exp):
        """Removes unnecessary brackets (destroys two-expression bracket syntax)"""
        n = len(bool_exp)
        bool_exp2 = bool_exp[0]
        for i in range(1,n-1):
            if bool_exp[i:i+2] == '((':
                bool_exp2 += ''
            elif bool_exp[i-1:i+1] == '))':
                bool_exp2 += ''
            elif bool_exp[i:i+2] == ')+':
                bool_exp2 += ''
            elif bool_exp[i-1:i+1] == '+(':
                bool_exp2 += ''
            else:
                bool_exp2 += bool_exp[i]
        return bool_exp2 + bool_exp[-1]

    def get_clauses(self, bool_exp):
        clauses = []
        n = len(bool_exp)
        cl = ''
        for i in range(n-1):
            if bool_exp[i] == '(':
                cl = ''
            elif bool_exp[i] == ')':
                clauses.append(cl)
            else:
                cl += bool_exp[i]
        return clauses

    def clause_sets_to_str(self, clauses):
        bool_exp = '('
        for i in clauses:
            exp = ''
            for j in i:
                exp += j+'+'
            bool_exp += '(' + exp[:-1] + ').'
        return bool_exp[:-1] + ')'

    def get_literals_adc(self, clause):
        """Gets literals in a string clause and

        deletes contradictions of form A+A and A+¬A"""
        lits = []
        lits_neg = []
        useless_lits = []
        n = len(clause)
        breaks = [-1]
        n_lits = 1
        for i in range(n):
            if clause[i] == '+':
                breaks.append(i)
                n_lits += 1
        breaks.append(n)
        for i in range(n_lits):
            lit = clause[breaks[i]+1:breaks[i+1]]
            if lit[0] == '¬':
                if lit[1:] in lits:
                    lits_index = lits.index(lit[1:])
                    if not lits_neg[lits_index]:
                        lits_neg.pop(lits_index)
                        lits.pop(lits_index)
                        useless_lits.append(lit[1:])
                elif lit[1:] not in useless_lits:
                    lits.append(lit[1:])
                    lits_neg.append(1)
            else:
                if lit in lits:
                    lits_index = lits.index(lit)
                    if lits_neg[lits_index]:
                        lits_neg.pop(lits_index)
                        lits.pop(lits_index)
                        useless_lits.append(lit)
                elif lit not in useless_lits:
                    lits.append(lit)
                    lits_neg.append(0)
        if len(useless_lits) > 0:
            return ['1'], [0]
        return lits, lits_neg

    def in_clause_clean_up(self, bool_exp):
        bool_exp2 = '('
        clauses = self.get_clauses(bool_exp)
        for clause_exp in clauses:
            lits, lits_neg = self.get_literals_adc(clause_exp)
            exp = ''
            for i in range(len(lits)):
                if lits_neg[i]:
                    exp += '¬'
                exp += lits[i] + '+'
            bool_exp2 += '(' + exp[:-1] + ').'
        return bool_exp2[:-1] + ')'

    def out_clause_clean_up(self, bool_exp):
        bool_exp2 = ''
        clauses = self.get_clauses(bool_exp)
        clause_lit_sets = []
        for clause_exp in clauses:
            lits, lits_neg = self.get_literals_adc(clause_exp)
            if lits != ['1']:
                clause_lit_sets.append(set())
                for i in range(len(lits)):
                    if lits_neg[i]:
                        clause_lit_sets[-1].add('¬'+lits[i])
                    else:
                        clause_lit_sets[-1].add(lits[i])

        for i in range(len(clause_lit_sets)):
            if clause_lit_sets[i] not in clause_lit_sets[:i]:
                exp = ''
                for j in clause_lit_sets[i]:
                    exp += j + '+'
                bool_exp2 += '(' + exp[:-1] + ').'
        return '(' + bool_exp2[:-1] + ')'

"""
path = 'correct_example.txt'
names = Names()
devices = Devices(names)
network = Network(names, devices)
monitors = Monitors(names, devices, network)

scanner = Scanner(path, names)
parser = Parser(names, devices, network, monitors, scanner)


parser.parse_network()
graph = Graph(names, devices, network, monitors)


#clause_exp = 'A0+¬A+B00'
#print(clause_exp)
#print(graph.get_literals_adc(clause_exp))


#bool_exp = graph.create_boolean_from_monitor('G3')

#bool_exp = '(((A0.A1)+(B1.B0))+(C0+C1))'
#print(bool_exp)

#print(graph.expand_xors(bool_exp))
#print('0123456789012345678901234567890123456789012345678901234567890')
#bool_exp = graph.expand_xors(bool_exp)
#bool_exp = graph.distribute_ors(bool_exp)
#bool_exp = graph.clean_up_to_cnf(bool_exp)
#print(bool_exp)
#print(graph.in_clause_clean_up(bool_exp))


#print(bool_exp)

#print(graph.clean_up_to_cnf(bool_exp))

#print('---')

#xor_test = '((A0*A1)+(A1*(A0+B)).(((S+R)*D)+((R+D)*(HFG))))'
#print(xor_test)
#print(graph.expand_xors(xor_test))
"""
