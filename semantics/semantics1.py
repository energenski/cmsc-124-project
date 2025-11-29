import sys

# data types
class Types:
    NOOB = 'NOOB'       # uninitialized
    NUMBR = 'NUMBR'     # int
    NUMBAR = 'NUMBAR'   # float
    YARN = 'YARN'       # string
    TROOF = 'TROOF'     # boolean
    TYPE = 'TYPE'       # type literal

# main class for lolcode
class Interpreter:
    def __init__(self):
        # store var
        self.scopes = [{}]  # Stack of scopes: {var_name: {'value': val, 'type': type}}
        self.functions = {} # func_name -> {params, body}
        # here sin-save ng interpreter yung text
        self.output_buffer = []
        self.it_register = {'value': None, 'type': Types.NOOB}
        self.return_value = None # For function returns
        self.should_return = False

    # adds new dict
    def push_scope(self):
        self.scopes.append({})

    # tanggal
    def pop_scope(self):
        self.scopes.pop()

    def current_scope(self):
        return self.scopes[-1]

    # creates a variable in the current (topmost) scope
    def declare_variable(self, name, value=None, type_=Types.NOOB):
        if name in self.current_scope():
            raise Exception(f"Variable '{name}' already declared in current scope")
        self.current_scope()[name] = {'value': value, 'type': type_}

    # looks at the current scope first and if not found, it checks the outer scope hanngang sa global
    def get_variable(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise Exception(f"Undeclared variable '{name}'")

    def set_variable(self, name, value, type_):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = {'value': value, 'type': type_}
                return
        raise Exception(f"Undeclared variable '{name}'")

    # Converts data from one type to another
    def cast_value(self, value, from_type, to_type):
        if from_type == to_type:
            return value
        # yung troof to yarn nagiging win (true) and fail (false)
        if to_type == Types.YARN:
            if from_type == Types.NOOB: return ""
            if from_type == Types.TROOF: return "WIN" if value else "FAIL"
            return str(value)
            
        # truncates decimal
        if to_type == Types.NUMBR:
            try:
                if from_type == Types.NUMBAR: return int(value)
                if from_type == Types.YARN: return int(value) 
                if from_type == Types.TROOF: return 1 if value else 0
            except:
                return 0
        
        # Adds decimal pts
        if to_type == Types.NUMBAR:
            try:
                if from_type == Types.NUMBR: return float(value)
                if from_type == Types.YARN: return float(value)
                if from_type == Types.TROOF: return 1.0 if value else 0.0
            except:
                return 0.0
            
        if to_type == Types.TROOF:
            if from_type == Types.NOOB: return False
            if from_type == Types.NUMBR: return value != 0
            if from_type == Types.NUMBAR: return value != 0.0
            if from_type == Types.YARN: return len(value) > 0
            
        return value # Fallback

    # main function na magpprocess sa Abstract syntax tree (ast)
    def execute(self, ast):
        try:
            self.execute_node(ast)
            return "\n".join(self.output_buffer)
        except Exception as e:
            return f"Runtime Error: {str(e)}"

    # recursive func that interpret each block/statemt
    def execute_node(self, node):
        if not node: return
        if self.should_return: return

        ntype = node.get('node_type')

        # Loops through a list of statements and executes them one by one
        if ntype == 'program':
            for stmt in node.get('body', []):
                self.execute_node(stmt)
        
        elif ntype == 'var_block':
            for stmt in node.get('body', []):
                self.execute_node(stmt)

        # calculates the initial value
        elif ntype == 'var_decl':
            val = None
            t = Types.NOOB
            if node.get('value'):
                val, t = self.evaluate(node.get('value'))
            self.declare_variable(node.get('name'), val, t)

        # update lag variable depende sa expression
        elif ntype == 'assignment':
            val, t = self.evaluate(node.get('expr'))
            target = node.get('target')
            if target == 'IT':
                self.it_register = {'value': val, 'type': t}
            else:
                self.set_variable(target, val, t)

        # Evaluates arguments, casts them to strings, and adds them sa output_buffer
        elif ntype == 'visible':
            out_parts = []
            for arg in node.get('args', []):
                val, t = self.evaluate(arg)
                out_parts.append(str(self.cast_value(val, t, Types.YARN)))
            self.output_buffer.append("".join(out_parts))

        elif ntype == 'if_stmt':
            # Check IT register
            condition_val = self.cast_value(self.it_register['value'], self.it_register['type'], Types.TROOF)
            
            executed = False
            if condition_val:
                for stmt in node.get('true_block', []):
                    self.execute_node(stmt)
                    if self.should_return: return
                executed = True
            else:
                # Check else ifs
                for elif_block in node.get('else_if_blocks', []):
                    cond, _ = self.evaluate(elif_block['condition'])
                    if cond: # Implicitly cast to TROOF in python
                        for stmt in elif_block['body']:
                            self.execute_node(stmt)
                            if self.should_return: return
                        executed = True
                        break
                
                if not executed:
                    for stmt in node.get('else_block', []):
                        self.execute_node(stmt)
                        if self.should_return: return

        # check yung value ng IT reg and compare sa literal values ng bawta case
        elif ntype == 'switch_stmt':
            it_val = self.it_register['value']
            matched = False
            for case in node.get('cases', []):
                case_val = case['value'] # Literal value
                # Simple equality check
                if it_val == case_val:
                    matched = True
                    for stmt in case['body']:
                        self.execute_node(stmt)
                        if self.should_return: return
                    break 
            
            if not matched:
                for stmt in node.get('default', []):
                    self.execute_node(stmt)
                    if self.should_return: return

        # check yung TIL or WILE cond para mag break
        elif ntype == 'loop':
            op = node.get('operation')
            cond = node.get('condition')
            
            while True:
                # Check condition
                if cond:
                    val, t = self.evaluate(cond['expr'])
                    bool_val = self.cast_value(val, t, Types.TROOF)
                    if cond['type'] == 'TIL' and bool_val: break
                    if cond['type'] == 'WILE' and not bool_val: break
                
                # Execute body
                for stmt in node.get('body', []):
                    self.execute_node(stmt)
                    if self.should_return: return
                    if isinstance(stmt, dict) and stmt.get('node_type') == 'break':
                        return # Break loop
                
                # Operation
                if op:
                    var_name = op['variable']
                    var_info = self.get_variable(var_name)
                    val = var_info['value']
                    if op['type'] == 'UPPIN': # incre,ent
                        val += 1
                    elif op['type'] == 'NERFIN': #decrement
                        val -= 1
                    self.set_variable(var_name, val, var_info['type'])

        elif ntype == 'break':
            pass 

        #save lang buong  function node
        elif ntype == 'func_def':
            self.functions[node.get('name')] = node

        # check if same count ng args and params
        elif ntype == 'func_call':
            func_name = node.get('name')
            if func_name not in self.functions:
                raise Exception(f"Function '{func_name}' not defined")
            
            func_node = self.functions[func_name]
            params = func_node.get('params', [])
            args = node.get('args', [])
            
            if len(params) != len(args):
                raise Exception(f"Function '{func_name}' expects {len(params)} arguments, got {len(args)}")
            
            # Create new scope
            self.push_scope()
            
            # Bind args to params
            for param, arg_expr in zip(params, args):
                val, t = self.evaluate(arg_expr)
                self.declare_variable(param, val, t)
                
            # Execute body
            for stmt in func_node.get('body', []):
                self.execute_node(stmt)
                if self.should_return: break
            
            # Capture return
            ret_val = self.return_value
            self.return_value = None
            self.should_return = False
            self.pop_scope()
            
            if ret_val:
                self.it_register = ret_val
            else:
                self.it_register = {'value': None, 'type': Types.NOOB}

        # reutrn para mag stop yung pag run
        elif ntype == 'return':
            val, t = self.evaluate(node.get('value'))
            self.return_value = {'value': val, 'type': t}
            self.should_return = True

        elif ntype == 'type_cast':
            # IS NOW A (modifies variable)
            if 'target' in node:
                target = node.get('target')
                target_type_str = node.get('type')
                var_info = self.get_variable(target)
                new_val = self.cast_value(var_info['value'], var_info['type'], target_type_str)
                self.set_variable(target, new_val, target_type_str)

    # compute and turn back the value and type sa expression
    def evaluate(self, node):
        ntype = node.get('node_type')
        
        if ntype == 'operand':
            val = node.get('value')
            kind = node.get('kind')
            
            if kind == 'IT':
                return self.it_register['value'], self.it_register['type']
            
            if kind == 'IDENTIFIER':
                # Try to look up variable
                try:
                    info = self.get_variable(val)
                    return info['value'], info['type']
                except:
                    raise Exception(f"Undeclared variable '{val}'")
            
            # Literals
            if kind == 'INTEGER_LITERAL': return val, Types.NUMBR
            if kind == 'FLOAT_LITERAL': return val, Types.NUMBAR
            if kind == 'STRING': return val, Types.YARN 
            if kind == 'TROOF_LITERAL':
                if val == 'WIN' or val == 'true': return True, Types.TROOF
                if val == 'FAIL' or val == 'false': return False, Types.TROOF
                return val, Types.TROOF # Fallback
            
            return val, Types.ANY

        # compute the result of two args operation 
        elif ntype == 'binary_op':
            left_val, left_type = self.evaluate(node.get('left'))
            right_val, right_type = self.evaluate(node.get('right'))
            op = node.get('op')
            
            if op == 'SUM_OF':
                return left_val + right_val, Types.NUMBR if isinstance(left_val, int) and isinstance(right_val, int) else Types.NUMBAR
            elif op == 'DIFF_OF':
                return left_val - right_val, Types.NUMBR 
            elif op == 'PRODUKT_OF':
                return left_val * right_val, Types.NUMBR
            elif op == 'QUOSHUNT_OF':
                return left_val / right_val, Types.NUMBAR
            elif op == 'MOD_OF':
                return left_val % right_val, Types.NUMBR
            elif op == 'BIGGR_OF':
                return max(left_val, right_val), left_type
            elif op == 'SMALLR_OF':
                return min(left_val, right_val), left_type
            elif op == 'BOTH_OF':
                return (bool(left_val) and bool(right_val)), Types.TROOF
            elif op == 'EITHER_OF':
                return (bool(left_val) or bool(right_val)), Types.TROOF
            elif op == 'WON_OF':
                return (bool(left_val) != bool(right_val)), Types.TROOF
            elif op == 'BOTH_SAEM':
                return (left_val == right_val), Types.TROOF
            elif op == 'DIFFRINT':
                return (left_val != right_val), Types.TROOF
                
        # compute the result of single arg operation
        elif ntype == 'unary_op':
            val, t = self.evaluate(node.get('operand'))
            if node.get('op') == 'NOT':
                return not bool(val), Types.TROOF

        # multi-arg
        elif ntype == 'n_ary_op':
            op = node.get('op')
            operands = [self.evaluate(x)[0] for x in node.get('operands')]
            
            if op == 'ALL_OF':
                return all(operands), Types.TROOF
            elif op == 'ANY_OF':
                return any(operands), Types.TROOF
            elif op == 'SMOOSH':
                return "".join(map(str, operands)), Types.YARN
        # evaluate expression tas typecast
        elif ntype == 'type_cast':
            # MAEK
            val, t = self.evaluate(node.get('expr'))
            target_type = node.get('type')
            return self.cast_value(val, t, target_type), target_type

        return None, Types.NOOB

if __name__ == "__main__":
    # For quick testing, we can import parser if running directly
    if len(sys.argv) > 1:
        # Assume it's called from server.py with AST or something, 
        # but actually server.py calls this script.
        # Wait, server.py calls this script with a FILE PATH.
        # So we need to:
        # 1. Read file
        # 2. Parse (using syntax2)
        # 3. Execute
        
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from syntax.syntax2 import Parser
        from lexer1 import get_tokens
        
        filepath = sys.argv[1]
        with open(filepath, 'r') as f:
            code = f.read()
            
        tokens = get_tokens(code)
        parser = Parser(tokens)
        ast = parser.parse()
        
        if parser.errors:
            print("Syntax Errors:")
            for err in parser.errors:
                print(err)
            sys.exit(1)
            
        interpreter = Interpreter()
        result = interpreter.execute(ast)
        print(result)
