import sys
import json


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

    def cast_value(self, value, from_type, to_type, explicit=False):
        if from_type == to_type:
            return value
        
       
        # 2. To YARN
        if to_type == Types.YARN:
            if from_type == Types.NUMBAR:
                return str(value)
            if from_type == Types.TROOF:
                return "WIN" if value else "FAIL"
            # NUMBR to YARN just converts to string 
            return str(value) 
            
        # 3. To NUMBR
        if to_type == Types.NUMBR:
            if from_type == Types.NUMBAR: 
                # Truncates the decimal portion 
                return int(value) 
            if from_type == Types.YARN:
                if value.strip() == "":  # empty string counts as zero
                    return 0
                try:
                    if '.' in value:
                        return int(float(value))
                    return int(value)
                except ValueError:
                    if explicit:
                        return 0
                    # allow implicit cast of empty YARN to 0 for arithmetic
                    return 0
            if from_type == Types.TROOF: 
                return 1 if value else 0 # WIN -> 1, FAIL -> 0 

        # 4. To NUMBAR
        if to_type == Types.NUMBAR:
            if from_type == Types.NUMBR: 
                return float(value)
            if from_type == Types.YARN: 
                try:
                    return float(value)
                except ValueError:
                    if explicit: return 0.0 # Explicit cast to zero on failure
                    raise Exception(f"Cannot implicitly cast YARN '{value}' to NUMBAR.")
            if from_type == Types.TROOF: 
                return 1.0 if value else 0.0 # WIN -> 1.0, FAIL -> 0.0 

        # 5. To TROOF
        if to_type == Types.TROOF:
            if from_type == Types.NUMBR or from_type == Types.NUMBAR: 
                # Numerical zero values are cast to FAIL. All others are WIN. 
                return value != 0 and value != 0.0
            if from_type == Types.YARN: 
                # Empty string ("") is cast to FAIL. All others are WIN. 
                return value != ""
            # The NOOB case is handled at the start.
            
        return value # Should not be reached for defined types

    # main function na magpprocess sa Abstract syntax tree (ast)
    def execute(self, ast):
        try:
            self.execute_node(ast)
            # return "\n".join(self.output_buffer) # No longer returning buffer
        except Exception as e:
            print(f"Runtime Error: {str(e)}")

    # recursive func that interpret each block/statemt
    def execute_node(self, node):
        if not node: return
        if self.should_return: return

        ntype = node.get('node_type')
        # print(f"EXECUTE NODE: {ntype}")

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
                try:
                    val, t = self.evaluate(arg)
                    out_parts.append(str(self.cast_value(val, t, Types.YARN)))
                except Exception as e:
                    out_parts.append(f"[Error: {str(e)}]")
            
            output = "".join(out_parts)
            self.output_buffer.append(output)
            print(output)
            sys.stdout.flush()

        elif ntype == 'if_stmt':

            # ORLY uses the current value in IT register
            # Cast IT to TROOF
            condition_val = self.cast_value(self.it_register['value'], self.it_register['type'], Types.TROOF)

            branch_executed = False

            # YA RLY block
            if condition_val:
                for stmt in node.get('true_block', []):
                    self.execute_node(stmt)
                    if self.should_return: return
                branch_executed = True

            # MEBBE blocks
            if not branch_executed:
                for elif_block in node.get('else_if_blocks', []):
                    # Evaluate MEBBE condition
                    # Note: In LOLCODE, expressions in flow control usually update IT.
                    # We evaluate, update IT, then check TROOFness.
                    val, t = self.evaluate(elif_block['condition'])
                    self.it_register = {'value': val, 'type': t}
                    
                    cond_val = self.cast_value(val, t, Types.TROOF)
                    
                    if cond_val:
                        for stmt in elif_block['body']:
                            self.execute_node(stmt)
                            if self.should_return: return
                        branch_executed = True
                        break  # Stop after first true MEBBE

            # NO WAI block
            if not branch_executed:
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

        # GIMMEH input
        elif ntype == 'input':
            var_name = node.get('variable')
            try:
                # Read from stdin
                user_input = input()
                # Store as YARN (string)
                self.set_variable(var_name, user_input, Types.YARN)
            except EOFError:
                # Handle end of input gracefully if needed
                self.set_variable(var_name, "", Types.YARN)

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
                    # Typecast to NUMBR/NUMBAR for UPPIN/NERFIN
                    # Assume casting to NUMBAR for safety if needed, or NUMBR if it's the current type
                    # For simplicity, cast to the current numerical type or NUMBR if NOOB/TROOF
                    current_type = var_info['type']
                    
                    if current_type not in [Types.NUMBR, Types.NUMBAR]:
                        # Attempt to implicitly cast to NUMBR/NUMBAR
                        # Since this is an operation, the casting rules from arithmetic should apply
                        try:
                            val = self.cast_value(val, current_type, Types.NUMBR)
                            current_type = Types.NUMBR
                        except:
                            try:
                                val = self.cast_value(val, current_type, Types.NUMBAR)
                                current_type = Types.NUMBAR
                            except:
                                raise Exception(f"Loop variable '{var_name}' value cannot be cast to numerical type for UPPIN/NERFIN.")

                    if op['type'] == 'UPPIN': # increment
                        val += 1
                    elif op['type'] == 'NERFIN': # decrement
                        val -= 1
                        
                    # Ensure value remains int if original type was NUMBR, and float if NUMBAR
                    if current_type == Types.NUMBR:
                        val = int(val)
                    elif current_type == Types.NUMBAR:
                        val = float(val)

                    self.set_variable(var_name, val, current_type)

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

    def get_numeric_operands(self, left_node, right_node, operation_name):
        left_val, left_type = self.evaluate(left_node)
        right_val, right_type = self.evaluate(right_node)
        
        # Determine the target type for casting and the final result type
        # If at least one is NUMBAR, the target is NUMBAR and result is NUMBAR.
        # If both are NUMBR, the target is NUMBR and result is NUMBR.
        # Division always yields NUMBAR
        if operation_name == 'QUOSHUNT_OF':
            target_type = Types.NUMBAR
        else:
            target_type = Types.NUMBAR if left_type == Types.NUMBAR or right_type == Types.NUMBAR else Types.NUMBR
        result_type = target_type

        try:
            left_num = self.cast_value(left_val, left_type, target_type)
            right_num = self.cast_value(right_val, right_type, target_type)
        except Exception as e:
            # If a value cannot be typecast, the operation must fail with an error [cite: 161]
            raise Exception(f"Arithmetic Error in {operation_name}: {str(e)}")
            
        # If target was NUMBR, but we got floats from casting YARN/NUMBAR, convert them to int for NUMBR result
        if result_type == Types.NUMBR:
            left_num = int(left_num)
            right_num = int(right_num)

        return left_num, right_num, result_type

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

            # --- Arithmetic Operations (Require implicit casting) ---
            if op in ['SUM_OF', 'DIFF_OF', 'PRODUKT_OF', 'QUOSHUNT_OF', 'MOD_OF', 'BIGGR_OF', 'SMALLR_OF']:
                
                left_num, right_num, result_type = self.get_numeric_operands(node.get('left'), node.get('right'), op)
                
                # Check for division by zero
                if op in ['QUOSHUNT_OF', 'MOD_OF'] and right_num == 0:
                    raise Exception(f"Division or Modulo by zero error in {op}.")

                # Arithmetic calculations
                if op == 'SUM_OF':
                    result = left_num + right_num
                elif op == 'DIFF_OF':
                    result = left_num - right_num
                elif op == 'PRODUKT_OF':
                    result = left_num * right_num
                elif op == 'QUOSHUNT_OF':
                    # If both operands evaluated to NUMBR, the result is truncated (integer division)
                    if result_type == Types.NUMBR:
                        result = left_num // right_num
                    else:
                        result = left_num / right_num
                elif op == 'MOD_OF':
                    result = left_num % right_num
                elif op == 'BIGGR_OF': # Max operation
                    result = max(left_num, right_num)
                elif op == 'SMALLR_OF': # Min operation
                    result = min(left_num, right_num)

                # Ensure result type matches: NUMBR (int) or NUMBAR (float)
                if result_type == Types.NUMBR:
                    result = int(result)
                elif result_type == Types.NUMBAR:
                    result = float(result)

                return result, result_type

            # --- Boolean Operations (Require implicit TROOF casting) ---
            
            # Implicitly cast operands to TROOF
            left_troof = self.cast_value(left_val, left_type, Types.TROOF)
            right_troof = self.cast_value(right_val, right_type, Types.TROOF)
            
            if op == 'BOTH_OF':
                return (left_troof and right_troof), Types.TROOF
            elif op == 'EITHER_OF':
                return (left_troof or right_troof), Types.TROOF
            elif op == 'WON_OF':
                return (left_troof != right_troof), Types.TROOF
            
            # --- Comparison Operations (NO implicit casting) ---
            # Comparisons are done using the raw values/types.
            elif op == 'BOTH_SAEM':
                # Relaxed comparison: allow implicit casting
                if left_type == right_type:
                    return (left_val == right_val), Types.TROOF
                
                # NUMBR vs NUMBAR
                if left_type in (Types.NUMBR, Types.NUMBAR) and right_type in (Types.NUMBR, Types.NUMBAR):
                    return (float(left_val) == float(right_val)), Types.TROOF
                
                # YARN vs NUMBR/NUMBAR
                try:
                    if left_type == Types.YARN and right_type in (Types.NUMBR, Types.NUMBAR):
                        return (float(left_val) == float(right_val)), Types.TROOF
                    if right_type == Types.YARN and left_type in (Types.NUMBR, Types.NUMBAR):
                        return (float(left_val) == float(right_val)), Types.TROOF
                except ValueError:
                    pass # Casting failed, so they are different
                
                return False, Types.TROOF

            elif op == 'DIFFRINT':
                # DIFFRINT is NOT BOTH_SAEM
                # We can reuse the logic by inverting the result of BOTH_SAEM logic
                # But for clarity/performance, we can just copy-paste and invert or call a helper.
                # Let's just duplicate logic but inverted.
                
                if left_type == right_type:
                    return (left_val != right_val), Types.TROOF
                
                if left_type in (Types.NUMBR, Types.NUMBAR) and right_type in (Types.NUMBR, Types.NUMBAR):
                    return (float(left_val) != float(right_val)), Types.TROOF
                
                try:
                    if left_type == Types.YARN and right_type in (Types.NUMBR, Types.NUMBAR):
                        return (float(left_val) != float(right_val)), Types.TROOF
                    if right_type == Types.YARN and left_type in (Types.NUMBR, Types.NUMBAR):
                        return (float(left_val) != float(right_val)), Types.TROOF
                except ValueError:
                    pass 
                
                return True, Types.TROOF
                
            raise Exception(f"Unknown binary operation: {op}")
                
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
                result = "".join(str(self.evaluate(x)[0]) for x in node.get('operands'))
                return result, Types.YARN
        # evaluate expression tas typecast
        elif ntype == 'type_cast':
            # MAEK
            val, t = self.evaluate(node.get('expr'))
            target_type = node.get('type')
            return self.cast_value(val, t, target_type), target_type

        return None, Types.NOOB

    def dump_symbol_table(self):
        # Helper to format value for display
        def format_val(val, type_):
            if type_ == Types.NOOB:
                return "NOOB"
            if type_ == Types.TROOF:
                return "WIN" if val else "FAIL"
            return val

        # Merge scopes from bottom to top to get current visible variables
        symbols = {}
        for scope in self.scopes:
            for name, info in scope.items():
                symbols[name] = {
                    'value': format_val(info['value'], info['type']),
                    'type': info['type']
                }
        
        # Also include IT variable
        symbols['IT'] = {
            'value': format_val(self.it_register['value'], self.it_register['type']),
            'type': self.it_register['type']
        }
        
        import json
        return json.dumps(symbols, default=str)

if __name__ == "__main__":
    # For quick testing, we can import parser if running directly
    if len(sys.argv) > 1:
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
        interpreter.execute(ast)
        
        # Dump tokens
        token_list = []
        for t in tokens:
            token_list.append({
                'lexeme': t.value,
                'classification': t.label,
                'line': t.line
            })
        print(f"\n<<TOKENS>>{json.dumps(token_list)}")

        # Dump symbol table at the end
        print(f"\n<<SYMBOL_TABLE>>{interpreter.dump_symbol_table()}")
