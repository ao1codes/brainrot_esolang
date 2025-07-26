from flask import Flask, request, render_template, jsonify
import subprocess
import uuid
import os
import re

app = Flask(__name__)

def create_input_modified_interpreter():
    """Create a modified interpreter class that handles spill with preset inputs"""
    
    class InputModifiedInterpreter:
        def __init__(self, debug=False):
            self.acc = 0
            self.pc = 0
            self.lines = []
            self.loop_stack = []
            self.stack = []
            self.vars = {}
            self.funcs = {}
            self.call_stack = []
            self.debug = debug
            self.preset_inputs = []
            self.input_index = 0

        def set_inputs(self, inputs):
            """Set the preset inputs for spill commands"""
            self.preset_inputs = inputs
            self.input_index = 0

        def load(self, filepath):
            if not os.path.isfile(filepath):
                raise Exception(f"File not found: {filepath}")
            raw = open(filepath).readlines()
            self.lines = list(self._parse_lines(raw))
            self._build_function_table()

        def _parse_lines(self, lines):
            for idx, raw in enumerate(lines, 1):
                line = raw.strip()
                if not line or line.startswith('#'):
                    continue
                if '#' in line:
                    line = line.split('#', 1)[0].strip()
                if not line:
                    continue
                tokens = line.split()
                yield idx, tokens

        def _build_function_table(self):
            self.funcs.clear()
            stack = []
            for idx, (_, tokens) in enumerate(self.lines):
                if tokens[0] == 'func':
                    if len(tokens) != 2:
                        raise Exception(f"Malformed func at line {self.lines[idx][0]}")
                    stack.append((tokens[1], idx))
                elif tokens[0] == 'endfunc':
                    if not stack:
                        raise Exception(f"Unmatched endfunc at line {self.lines[idx][0]}")
                    name, start_idx = stack.pop()
                    self.funcs[name] = (start_idx + 1, idx)
            if stack:
                name, line_idx = stack[-1]
                raise Exception(f"Unclosed func '{name}' starting at line {self.lines[line_idx][0]}")

        def run(self):
            while self.pc < len(self.lines):
                line_no, tokens = self.lines[self.pc]
                cmd = tokens[0]
                
                if cmd == 'func':
                    _, (_, end_idx) = next(((n, val) for n, val in self.funcs.items() if val[0]-1 == self.pc), (None, (None, None)))
                    if end_idx is not None:
                        self.pc = end_idx + 1
                    else:
                        self.pc += 1
                    continue
                if cmd == 'endfunc':
                    self.pc += 1
                    continue

                if self.debug:
                    print(f"[DEBUG] Line {line_no}: {tokens} | ACC={self.acc}")

                old_pc = self.pc
                try:
                    self.execute(cmd, tokens[1:])
                except Exception as e:
                    print(f"Error at line {line_no}: {e}")
                    return

                if self.pc == old_pc:
                    self.pc += 1

        def execute(self, cmd, args):
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
            elif cmd == 'flex':
                self.stack.append(self.acc * self.acc)
            elif cmd == 'fam':
                self.stack.append(self.acc)
            elif cmd == 'clapback':
                if not self.stack:
                    raise Exception("Stack is empty")
                self.acc = self.stack.pop()
            elif cmd == 'set':
                if len(args) != 1:
                    raise Exception("Usage: set <varname>")
                self.vars[args[0]] = self.acc
            elif cmd == 'get':
                if len(args) != 1:
                    raise Exception("Usage: get <varname>")
                name = args[0]
                if name not in self.vars:
                    raise Exception(f"Unknown variable '{name}'")
                self.acc = self.vars[name]
            elif cmd == 'spill':
                # use preset input instead of prompting
                if self.input_index < len(self.preset_inputs):
                    self.acc = self.preset_inputs[self.input_index]
                    self.input_index += 1
                else:
                    self.acc = 0  # default if no more inputs
            elif cmd == 'skibidi':
                print(self.acc)
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
                        raise Exception("Unmatched 'vibe'")
            elif cmd == 'unvibe':
                if not self.loop_stack:
                    raise Exception("Unmatched 'unvibe'")
                start = self.loop_stack[-1]
                if self.acc > 0:
                    self.pc = start + 1
                else:
                    self.loop_stack.pop()
            elif cmd == 'call':
                if len(args) != 1:
                    raise Exception("Usage: call <funcname>")
                name = args[0]
                if name not in self.funcs:
                    raise Exception(f"Unknown function '{name}'")
                start, end = self.funcs[name]
                self.call_stack.append(self.pc + 1)
                self.pc = start
            elif cmd == 'return':
                if not self.call_stack:
                    raise Exception("Return without call")
                self.pc = self.call_stack.pop()
            elif cmd == 'mid':
                pass
            else:
                raise Exception(f"Unknown command '{cmd}'")

    return InputModifiedInterpreter

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    code = ""
    inputs = ""
    error_message = ""

    if request.method == "POST":
        code = request.form.get("code", "")
        inputs = request.form.get("inputs", "")
        
        # parse inputs with validation
        input_values = []
        if inputs.strip():
            try:
                input_parts = [x.strip() for x in inputs.split(',') if x.strip()]
                input_values = []
                for part in input_parts:
                    val = int(part)
                    # limit input range to prevent resource exhaustion
                    if abs(val) > 10000:
                        error_message = f"❌ Input value {val} is too large. Maximum allowed is ±10000."
                        break
                    input_values.append(val)
            except ValueError:
                error_message = "❌ Invalid input format. Please enter comma-separated integers."
        
        if not error_message:
            # check if code contains spill commands
            spill_count = code.count('spill')
            if spill_count > len(input_values) and spill_count > 0:
                error_message = f"❌ Code contains {spill_count} 'spill' command(s) but only {len(input_values)} input(s) provided."
        
        if not error_message:
            # use modified interpreter instead of preprocessing
            temp_filename = f"temp_{uuid.uuid4().hex}.brainrot"
            
            try:
                with open(temp_filename, "w") as f:
                    f.write(code)
                
                # create and use modified interpreter
                InterpreterClass = create_input_modified_interpreter()
                
                # capture output
                import io
                import contextlib
                
                output_buffer = io.StringIO()
                
                with contextlib.redirect_stdout(output_buffer):
                    try:
                        interp = InterpreterClass(debug=False)
                        interp.set_inputs(input_values)
                        interp.load(temp_filename)
                        interp.run()
                    except Exception as e:
                        print(f"Error: {e}")
                
                output = output_buffer.getvalue()
                
            except Exception as e:
                output = f"❌ Error: {str(e)}"
            finally:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
        else:
            output = error_message

    return render_template("index.html", code=code, output=output, inputs=inputs)

@app.route("/api/run", methods=["POST"])
def api_run():
    """API endpoint for running code"""
    data = request.get_json()
    code = data.get("code", "")
    inputs = data.get("inputs", [])
    
    if not isinstance(inputs, list):
        return jsonify({"error": "Inputs must be a list of integers"}), 400
    
    try:
        input_values = []
        for x in inputs:
            val = int(x)
            if abs(val) > 10000:
                return jsonify({"error": f"Input value {val} is too large. Maximum allowed is ±10000."}), 400
            input_values.append(val)
    except (ValueError, TypeError):
        return jsonify({"error": "All inputs must be integers"}), 400
    
    spill_count = code.count('spill')
    if spill_count > len(input_values) and spill_count > 0:
        return jsonify({
            "error": f"Code contains {spill_count} 'spill' command(s) but only {len(input_values)} input(s) provided."
        }), 400
    
    temp_filename = f"temp_{uuid.uuid4().hex}.brainrot"
    
    try:
        with open(temp_filename, "w") as f:
            f.write(code)
        
        InterpreterClass = create_input_modified_interpreter()
        
        import io
        import contextlib
        
        output_buffer = io.StringIO()
        
        with contextlib.redirect_stdout(output_buffer):
            try:
                interp = InterpreterClass(debug=False)
                interp.set_inputs(input_values)
                interp.load(temp_filename)
                interp.run()
            except Exception as e:
                print(f"Error: {e}")
        
        output = output_buffer.getvalue()
        return jsonify({"output": output})
    
    except Exception as e:
        return jsonify({"output": f"❌ Error: {str(e)}"})
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=42817)