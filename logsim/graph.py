"""Define Graph class to help with CNF capability."""


class Graph:
    """Define the logsim graph and make convert to
    conjunctive-normal-form.

    This class contains the methods for taking the parsed network and
    converting to conjunctive-normal-form in anticipation of adding a
     SAT-solver if relevant.

    Parameters:
    -----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.

    Public Methods:
    ---------------
    create_boolean_from_monitor(self, monitor_name): Produces a boolean
                            expression string from the network in-use
                            at the indicated monitor.

    get_sub_exp_end(self, bool_exp, i, left=True): Gets the endpoint
                            of the current subexpression, in the
                            direction indicated and at the bracket-
                            level of the start point.

    expand_xors(self, bool_exp): Converts all the XOR gates in the given
                            boolean expression string to ANDs, ORs and
                            NOTs.

    distribute_ors(self, bool_exp): Distributes all the ORs over the
                            ANDs in the boolean expression string to
                            give an expression in conjunctive normal
                            form.

    clean_up_to_cnf(self, bool_exp): Removes all the unnecessary brackets
                            and returns the boolean expression string in
                            conjunctive normal form.

    get_clauses(self, bool_exp): Gets all the clauses from a given
                            boolean expression string and returns them
                            as a list of strings.

    get_literals_adc(self, clause): Gets the literals within a given
                            clause string 'and destroys contradictions'
                            meaning setting literals containing both a
                            literal and its negation to '1' and removing
                            duplicate literals within a clause.

    in_clause_clean_up(self, bool_exp): Ties together the above methods
                            to remove unnecessary brackets and
                            redundancies on the literal level within
                            clauses and returns the expression in
                            string form.

    out_clause_clean_up(self, bool_exp): Ties together the above methods
                            to remove unnecessary brackets and
                            redundancies on the clause level and returns
                            the expression in string form.
    """

    def __init__(self, names, devices, network, monitors):
        """Initialise the graph and graph dependencies."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

    def create_boolean_from_monitor(self, monitor_name):
        """Generate boolean expression for monitor.

        Will return False if any circularity included (including
        flip-flops).
        """
        mon_id = self.names.query(monitor_name)
        mon_dev = self.devices.get_device(mon_id)

        dev_list = self.devices.find_devices()

        # Check no flip flops / other 2-output devices
        for dev in dev_list:
            dev = self.devices.get_device(dev)
            if len(dev.outputs) != 1 or len(dev.inputs) > 2:
                return False

        def dfs(dev, dfs_calls):
            """Recursively build boolean expression from monitor position."""

            # Make sure it doesn't get caught in a loop (circular
            # definition)
            dfs_calls += 1
            if dfs_calls > 500:
                return '@'

            # Otherwise recursively build boolean expression string from
            # device inputs
            dev_ins = dev.inputs

            # Check if device is a switch
            if len(dev_ins) == 0:
                return self.names.get_name_string(dev.device_id)

            # Check if device is a not gate
            if len(dev_ins) == 1:
                [out_dev_id] = dev_ins
                next_dev = self.devices.get_device(dev_ins[out_dev_id][0])
                return '¬(' + dfs(next_dev, dfs_calls) + ')'

            # Assume gate is one of AND, OR, NAND, NOR, XOR.
            # Get input device IDs
            i, j = dev_ins

            # Get device objects
            i_dev = self.devices.get_device(dev_ins[i][0])
            j_dev = self.devices.get_device(dev_ins[j][0])

            # Produce string boolean expression calling dfs to build
            # the expression below.
            middle_char = ['.', '+', '.', '+', '*'][dev.device_kind]
            if dev.device_kind in (2, 3):
                return '¬(' + dfs(i_dev, dfs_calls) + middle_char + \
                       dfs(j_dev, dfs_calls) + ')'
            else:
                return '(' + dfs(i_dev, dfs_calls) + middle_char + \
                       dfs(j_dev, dfs_calls) + ')'

        bool_exp = dfs(mon_dev, 0)
        if '@' in bool_exp:
            return False
        return bool_exp

    def get_sub_exp_end(self, bool_exp, i, left=True):
        """Get the end of the sub-expression."""
        if left:
            if bool_exp[i - 1] == ')':
                j = 2
                bracket_count = 1
                while bracket_count:
                    if bool_exp[i - j] == ')':
                        bracket_count += 1
                    elif bool_exp[i - j] == '(':
                        bracket_count -= 1
                    j += 1
            else:
                j = 1
                while bool_exp[i - j] not in ('(', '.', '+', '*'):
                    j += 1
            return j - 1
        else:
            if bool_exp[i + 1] == '(':
                k = 2
                bracket_count = 1
                while bracket_count:
                    if bool_exp[i + k] == '(':
                        bracket_count += 1
                    elif bool_exp[i + k] == ')':
                        bracket_count -= 1
                    k += 1
            else:
                k = 1
                while bool_exp[i + k] not in (')', '.', '+', '*'):
                    k += 1
            return k - 1

    def expand_xors(self, bool_exp):
        """Expand XORs in a given expression into ANDs/ORs."""
        while '*' in bool_exp:
            i = bool_exp.index('*')
            j = self.get_sub_exp_end(bool_exp, i, True)
            k = self.get_sub_exp_end(bool_exp, i, False)
            xor_exp = '(' + bool_exp[i - j:i] + '+' + \
                      bool_exp[i + 1:i + k + 1] + ').'
            xor_exp += '(¬' + bool_exp[i - j:i] + '+¬' + \
                       bool_exp[i + 1:i + k + 1] + ')'
            bool_exp = bool_exp[:i - j] + xor_exp + bool_exp[i + k + 1:]

        return bool_exp

    def distribute_ors(self, bool_exp):
        """Distribute ORs over ANDs in pursuit of conjunctive normal form."""
        bool_exp0 = 0
        while bool_exp0 != bool_exp:
            bool_exp0 = bool_exp
            i = 0
            for n_or in range(bool_exp.count(')+')):
                i = bool_exp[i + 1:].index(')+') + i + 2
                j = self.get_sub_exp_end(bool_exp, i - 1, True)
                if bool_exp[i - j - 2] == '.':
                    jj = self.get_sub_exp_end(bool_exp, i - j - 2, True)
                    k = self.get_sub_exp_end(bool_exp, i, False)
                    or_exp = '(' + bool_exp[i - j - 2 - jj:i - j - 2] + \
                             bool_exp[i:i + k + 1] + ').'
                    or_exp += '(' + bool_exp[i - j - 1:i - 1] + \
                              bool_exp[i:i + k + 1] + ')'
                    bool_exp = bool_exp[:i - j - 3 - jj] + or_exp + bool_exp[
                                                                    i + k + 1:]
                    break

            i = 0
            for n_or in range(bool_exp.count('+(')):
                i = bool_exp[i + 1:].index('+(') + i + 1
                j = self.get_sub_exp_end(bool_exp, i + 1, False)
                if bool_exp[(i + 1) + j + 1] == '.':
                    jj = self.get_sub_exp_end(bool_exp, i + 2 + j, False)
                    k = self.get_sub_exp_end(bool_exp, i, True)
                    or_exp = '(' + bool_exp[i - k:i + 1] + \
                             bool_exp[i + 2:i + j + 2] + ').'
                    or_exp += '(' + bool_exp[i - k:i + 1] + \
                              bool_exp[i + j + 3:i + j + 3 + jj] + ')'
                    bool_exp = bool_exp[:i - k] + or_exp + bool_exp[
                                                           i + j + 4 + jj:]
                    break
        return bool_exp

    def clean_up_to_cnf(self, bool_exp):
        """Remove unnecessary brackets.

        Note that it destroys two-expression bracket syntax).
        """
        n = len(bool_exp)
        bool_exp2 = bool_exp[0]
        for i in range(1, n - 1):
            if bool_exp[i:i + 2] == '((':
                bool_exp2 += ''
            elif bool_exp[i - 1:i + 1] == '))':
                bool_exp2 += ''
            elif bool_exp[i:i + 2] == ')+':
                bool_exp2 += ''
            elif bool_exp[i - 1:i + 1] == '+(':
                bool_exp2 += ''
            else:
                bool_exp2 += bool_exp[i]
        return bool_exp2 + bool_exp[-1]

    def get_clauses(self, bool_exp):
        """Get clauses from boolean expression string."""
        clauses = []
        n = len(bool_exp)
        cl = ''
        for i in range(n - 1):
            if bool_exp[i] == '(':
                cl = ''
            elif bool_exp[i] == ')':
                clauses.append(cl)
            else:
                cl += bool_exp[i]
        return clauses

    def get_literals_adc(self, clause):
        """Get clause literals and remove contradictions/redundancies.

        Deletes contradictions of form A+A and A+¬A.
        """
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
            lit = clause[breaks[i] + 1:breaks[i + 1]]
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
        """Clean up the expression within clauses.

        Removes unnecessary brackets and contradictions/redundancy.
        """
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
        """Clean up the expression on the clause-to-clause level.

        Removes unnecessary brackets and contradictions/redundancy.
        """
        bool_exp2 = ''
        clauses = self.get_clauses(bool_exp)
        clause_lit_sets = []
        for clause_exp in clauses:
            lits, lits_neg = self.get_literals_adc(clause_exp)
            if lits != ['1']:
                clause_lit_sets.append(set())
                for i in range(len(lits)):
                    if lits_neg[i]:
                        clause_lit_sets[-1].add('¬' + lits[i])
                    else:
                        clause_lit_sets[-1].add(lits[i])

        for i in range(len(clause_lit_sets)):
            if clause_lit_sets[i] not in clause_lit_sets[:i]:
                exp = ''
                for j in clause_lit_sets[i]:
                    exp += j + '+'
                bool_exp2 += '(' + exp[:-1] + ').'
        return '(' + bool_exp2[:-1] + ')'

    def add_new_line_breaks(self, bool_exp):
        """Add line-breaks in boolean expression."""
        if len(bool_exp) < 80:
            return bool_exp, 0
        c = 0
        breaks = []
        for i in range(len(bool_exp)):
            c += 1
            if c > 70:
                if bool_exp[i] == '(':
                    if bool_exp[i-1] == '¬':
                        breaks.append(i-1)
                        c = 0
                    else:
                        breaks.append(i)
                        c = 0
        breaks.reverse()
        for i in breaks:
            bool_exp = bool_exp[:i] + '\n\t' + bool_exp[i:]
        return bool_exp, len(breaks)
