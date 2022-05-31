from typing import Any, Union

#import numpy
#from names import Names
#from devices import Devices
#from network import Network
#from monitors import Monitors
#from scanner import Scanner
#from parse import Parser


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

"""
path = 'correct_example.txt'
names = Names()
devices = Devices(names)
network = Network(names, devices)
monitors = Monitors(names, devices, network)

scanner = Scanner(path, names)
parser = Parser(names, devices, network, monitors, scanner)

#app = wx.App()
#gui = Gui("Logic Simulator", path, names, devices, network, monitors)
#gui.Show(True)
#app.MainLoop()

parser.parse_network()
graph = Graph(names, devices, network, monitors)
#print(names.names)

#print(graph.create_boolean_from_monitor('G3'))
bool_exp = graph.create_boolean_from_monitor('G3')

bool_exp = '(((A0.A1)+(B1.B0))+(C0+C1))'
print(bool_exp)

#print(graph.expand_xors(bool_exp))
#print('0123456789012345678901234567890123456789012345678901234567890')
bool_exp = graph.distribute_ors(bool_exp)

print(bool_exp)

print(graph.clean_up_to_cnf(bool_exp))

#print('---')

#xor_test = '((A0*A1)+(A1*(A0+B)).(((S+R)*D)+((R+D)*(HFG))))'
#print(xor_test)
#print(graph.expand_xors(xor_test))
"""
