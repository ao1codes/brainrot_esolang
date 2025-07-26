#!/usr/bin/env python3
import sys
import os

VERSION = "1.0.0"

class BrainrotError(Exception):
    pass

def parse_lines(lines):
    """
    Yield meaningful tokens from the source:
     - ignore blank lines
     - ignore comments (# at line start)
     - strip inline comments
     - split into tokens by whitespace
    """
    for idx, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        # remove inline comments
        if '#' in line:
            line = line.split('#', 1)[0].strip()
        if not line:
            continue
        tokens = line.split()
        yield idx, tokens

class Interpreter:
    def __init__(self, debug=False):
        self.acc = 0
        self.pc = 0
        self.lines = []             # list of (line_no, tokens)
        self.loop_stack = []        # for vibe/unvibe loops
        self.stack = []             # generic stack
        self.vars = {}              # named variables
        self.funcs = {}             # function table: name -> (start_idx, end_idx)
        self.call_stack = []        # return addresses
        self.debug = debug

    def load(self, filepath):
        if not os.path.isfile(filepath):
            raise BrainrotError(f"File not found: {filepath}")
        raw = open(filepath).readlines()
        self.lines = list(parse_lines(raw))
        self._build_function_table()

    def _build_function_table(self):
        """Scan for func/endfunc pairs and record their indices."""
        self.funcs.clear()
        stack = []
        for idx, (_, tokens) in enumerate(self.lines):
            if tokens[0] == 'func':
                if len(tokens) != 2:
                    raise BrainrotError(f"Malformed func at line {self.lines[idx][0]}")
                stack.append((tokens[1], idx))
            elif tokens[0] == 'endfunc':
                if not stack:
                    raise BrainrotError(f"Unmatched endfunc at line {self.lines[idx][0]}")
                name, start_idx = stack.pop()
                self.funcs[name] = (start_idx + 1, idx)  # body is between func and endfunc
        if stack:
            name, line_idx = stack[-1]
            raise BrainrotError(f"Unclosed func '{name}' starting at line {self.lines[line_idx][0]}")

    def run(self):
        while self.pc < len(self.lines):
            line_no, tokens = self.lines[self.pc]
            cmd = tokens[0]
            # skip function bodies unless called
            if cmd == 'func':
                # jump to matching endfunc
                _, (_, end_idx) = next(((n, val) for n, val in self.funcs.items() if val[0]-1 == self.pc), (None, None))
                self.pc = end_idx + 1
                continue
            if cmd == 'endfunc':
                # if we're inside a function body but not via call, skip
                self.pc += 1
                continue

            if self.debug:
                print(f"[DEBUG] Line {line_no}: {tokens} | ACC={self.acc} STACK={self.stack} VARS={self.vars} CALLS={self.call_stack}")

            old_pc = self.pc
            try:
                self.execute(cmd, tokens[1:])
            except BrainrotError as e:
                print(f"Error at line {line_no}: {e}", file=sys.stderr)
                sys.exit(1)

            if self.pc == old_pc:
                self.pc += 1

    def execute(self, cmd, args):
        # Arithmetic and accumulator
        if cmd == 'rizz':
            self.acc += 1
        elif cmd == 'gyatt':
            self.acc -= 1
        elif cmd == 'drip':
            self.acc += 5
        elif cmd == 'npc':
            self.acc -= 5
        elif cmd == 'lit':
            self.acc += 10
        elif cmd == 'slaps':
            self.acc -= 10
        elif cmd == 'yeet':
            self.acc *= 2
        elif cmd == 'cringe':
            if self.acc != 0:
                self.acc //= 2

        # Stack
        elif cmd == 'flex':
            self.stack.append(self.acc * self.acc)
        elif cmd == 'fam':
            self.stack.append(self.acc)
        elif cmd == 'peekback':
            if not self.stack:
                raise BrainrotError("Stack is empty")
            self.acc = self.stack[-1]
        elif cmd == 'clapback':
            if not self.stack:
                raise BrainrotError("Stack is empty")
            self.acc = self.stack.pop()

        # Variables
        elif cmd == 'set':
            if len(args) != 1:
                raise BrainrotError("Usage: set <varname>")
            self.vars[args[0]] = self.acc
        elif cmd == 'get':
            if len(args) != 1:
                raise BrainrotError("Usage: get <varname>")
            name = args[0]
            if name not in self.vars:
                raise BrainrotError(f"Unknown variable '{name}'")
            self.acc = self.vars[name]

        # I/O
        elif cmd == 'spill':
            val = input("spill> ")
            try:
                self.acc = int(val)
            except ValueError:
                raise BrainrotError("Invalid integer input")
        elif cmd == 'skibidi':
            print(self.acc)

        # Control flow
        elif cmd == 'no' and args == ['cap']:
            self.acc = 0
        elif cmd == 'sus':
            if self.acc == 0:
                self.pc += 2
        elif cmd == 'suspect':
            if self.acc > 0:
                self.pc += 2

        elif cmd == 'vibe':
            if self.acc > 0:
                self.loop_stack.append(self.pc)
            else:
                depth = 1
                while depth and self.pc < len(self.lines) - 1:
                    self.pc += 1
                    _, toks = self.lines[self.pc]
                    if toks[0] == 'vibe':
                        depth += 1
                    elif toks[0] == 'unvibe':
                        depth -= 1
                if depth:
                    raise BrainrotError("Unmatched 'vibe'")
        elif cmd == 'unvibe':
            if not self.loop_stack:
                raise BrainrotError("Unmatched 'unvibe'")
            start = self.loop_stack[-1]
            if self.acc > 0:
                self.pc = start + 1
            else:
                self.loop_stack.pop()

        # Functions
        elif cmd == 'call':
            if len(args) != 1:
                raise BrainrotError("Usage: call <funcname>")
            name = args[0]
            if name not in self.funcs:
                raise BrainrotError(f"Unknown function '{name}'")
            start, end = self.funcs[name]
            self.call_stack.append(self.pc + 1)
            self.pc = start
        elif cmd == 'return':
            if not self.call_stack:
                raise BrainrotError("Return without call")
            self.pc = self.call_stack.pop()
        # endfunc is handled by skipping over in run()

        # File include
        elif cmd == 'load':
            if len(args) != 1:
                raise BrainrotError("Usage: load <filename>")
            filename = args[0]
            prev_lines, prev_pc = self.lines, self.pc
            self.load(filename)
            self.lines, self.pc = prev_lines, prev_pc

        # Meta
        elif cmd == 'help':
            self.print_help()
        elif cmd == 'version':
            print(f"Brainrot version {VERSION}")

        # No-op
        elif cmd == 'mid':
            pass

        else:
            raise BrainrotError(f"Unknown command '{cmd}'")

    def print_help(self):
        print("Brainrot commands:")
        print("- rizz       : +1")
        print("- gyatt      : -1")
        print("- drip       : +5")
        print("- npc        : -5")
        print("- lit        : +10")
        print("- slaps      : -10")
        print("- yeet       : *2")
        print("- cringe     : //2")
        print("- flex       : push acc² to stack")
        print("- fam        : push acc")
        print("- peekback   : read top of stack")
        print("- clapback   : pop to acc")
        print("- set <v>    : var=v")
        print("- get <v>    : load var")
        print("- spill      : input number")
        print("- skibidi    : print acc")
        print("- no cap     : acc=0")
        print("- sus        : skip if acc==0")
        print("- suspect    : skip if acc>0")
        print("- vibe ...   : loop while acc>0")
        print("- unvibe     : end loop")
        print("- func <n>   : define function")
        print("- endfunc    : end function")
        print("- call <n>   : call function")
        print("- return     : return from function")
        print("- load <f>   : include file")
        print("- help       : this list")
        print("- version    : show version")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Brainrot esolang interpreter')
    parser.add_argument('file', nargs='?', help='Path to .brainrot source')
    parser.add_argument('--debug', action='store_true', help='Trace execution')
    args = parser.parse_args()

    interp = Interpreter(debug=args.debug)

    # REPL if no file given
    if not args.file:
        print(f"Brainrot v{VERSION} REPL. Type 'help'. Ctrl-C to exit.")
        try:
            while True:
                line = input(">>> ")
                if not line.strip():
                    continue
                toks = line.split()
                interp.lines = [(0, toks)]
                interp.pc = 0
                interp.execute(toks[0], toks[1:])
        except KeyboardInterrupt:
            print("\nGoodbye.")
        sys.exit(0)

    # run file
    try:
        interp.load(args.file)
        interp.run()
    except BrainrotError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    