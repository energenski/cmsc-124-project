class Types:
    NOOB = 'NOOB'       # uninitialized
    NUMBR = 'NUMBR'     # int
    NUMBAR = 'NUMBAR'   # float
    YARN = 'YARN'       # string
    TROOF = 'TROOF'     # boolean
    ANY = 'ANY'         # unknown/flexible
    WTF = 'WTF'         # error placeholder

# util function: infer literal token/value type
def infer_literal_type(val):
    if isinstance(val, int):
        return Types.NUMBR
    if isinstance(val, float):
        return Types.NUMBAR
    if isinstance(val, str):
        if val.startswith('"') and val.endswith('"'):
            return Types.YARN
        if val in ('WIN', 'FAIL'):
            return Types.TROOF
    return Types.ANY

class SemanticAnalyzer:
    def __init__(self):
        # stack of scopes, each scope is a dict var_name -> value/type
        self.scopes = [{}]
        # functions table: function_name -> node
        self.functions = {}
        # collected semantic errors
        self.errors = []
        # track if we are inside a function
        self.in_function = False
        # track if we are inside a loop
        self.in_loop = 0
        # track if we are inside a switch
        self.in_switch = 0
        # track if we are inside wazzup
        self.in_wazzup = False
        # func_name -> set of types seen
        self.function_returns = {}
        # track current function name
        self.current_func = None
        # Track IT's current type
        self.it_type = Types.NOOB  
        # Track if we are analyzing VISIBLE args
        self.in_visible_context = False

    # push a new scope
    def push_scope(self):
        self.scopes.append({})

    # pop the current scope
    def pop_scope(self):
        self.scopes.pop()

    def _declare_param(self, pname, ptype=None, line=None):
        info = {
            'declared_type': ptype or Types.ANY,
            'current_type': ptype or Types.ANY,
            'initialized': True,    # parameters are initialized
            'value': None,
            'line': line
        }
        self.scopes[-1][pname] = info

    # declare a variable in current scope
    def declare_variable(self, name, init_node=None, explicit_type=None, line=None):
        if name in self.scopes[-1]:
            self.errors.append(f"variable '{name}' already declared in current scope")
            return
        info = {
            'declared_type': explicit_type or Types.NOOB,
            'current_type': explicit_type or Types.NOOB,
            'initialized': False,
            'value': None,
            'line': line
        }
        if init_node:
            t = self.infer_expr_type(init_node)
            info['current_type'] = t
            if info['declared_type'] in [Types.NOOB, Types.ANY]:
                info['declared_type'] = t
            info['initialized'] = True
            info['value'] = init_node
        self.scopes[-1][name] = info

    # lookup variable in all scopes
    def lookup_var_info(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    # context-aware variable checking
    def check_variable_usage(self, var_name, line, node):
        """Check variable usage with context awareness"""
        info = self.lookup_var_info(var_name)
        if not info:
            self.errors.append(f"line {line}: undeclared variable '{var_name}'")
            return Types.WTF
        
        # Allow uninitialized variables in VISIBLE context
        if not info['initialized'] and not self.in_visible_context:
            self.errors.append(f"line {line}: use of uninitialized variable '{var_name}'")
            return Types.WTF
            
        return info['current_type']
    
    # helper: type cast validation
    def _is_valid_cast(self, from_type, to_type):
        """Check if a type cast is valid"""
        # Can't cast from WTF (error type)
        if from_type == Types.WTF:
            return False
        
        # Can't cast to WTF
        if to_type == Types.WTF:
            return False
        
        # Most types can be cast to YARN (string conversion)
        if to_type == Types.YARN:
            return True
        
        # YARN can be cast to TROOF (empty string is FAIL, non-empty is WIN)
        if from_type == Types.YARN and to_type == Types.TROOF:
            return True
        
        # Numeric conversions
        if from_type in [Types.NUMBR, Types.NUMBAR] and to_type in [Types.NUMBR, Types.NUMBAR]:
            return True
        
        # TROOF to numeric (WIN=1, FAIL=0)
        if from_type == Types.TROOF and to_type in [Types.NUMBR, Types.NUMBAR]:
            return True
        
        # Numeric to TROOF (0 is FAIL, non-zero is WIN)
        if from_type in [Types.NUMBR, Types.NUMBAR] and to_type == Types.TROOF:
            return True
        
        # NOOB can be cast to any type
        if from_type == Types.NOOB:
            return True
        
        # Same type is always valid
        if from_type == to_type:
            return True
        
        # ANY type is flexible
        if from_type == Types.ANY or to_type == Types.ANY:
            return True
        
        return False

    # main function to analyze any node
    def analyze_node(self, node):
        # ignore invalid nodes
        if not node or not isinstance(node, dict):
            return

        node_type = node.get("node_type")

        # handle var_block (wazzup)
        if node_type == "var_block":
            self.in_wazzup = True
            for decl in node.get("body", []):
                self.analyze_node(decl)
            self.in_wazzup = False

        # handle variable declaration
        elif node_type == "var_decl":
            # check if inside wazzup
            # print(self.scopes)
            if not self.in_wazzup:
                self.errors.append(f"line {node['line']}: variable '{node['name']}' declared outside wazzup")
                return         

            #     self.analyze_node(node["value"])
            init_node = node.get('value') or node.get('init')
            explicit_type = node.get('type') # if parser provided explicit declared type
            self.declare_variable(
                node.get('name'),
                init_node=init_node if isinstance(init_node, dict) else None,
                explicit_type=explicit_type,
                line=node.get('line')
            )
            if isinstance(init_node, dict):
                self.analyze_node(init_node)

        # handle operands
        elif node_type == "operand":
            # Handle standalone operands (like variable references)
            val = node.get("value")
            if isinstance(val, str) and not (val.startswith('"') and val.endswith('"')) and val not in ('WIN', 'FAIL'):
                # Use context-aware checking
                var_type = self.check_variable_usage(val, node['line'], node)
                if var_type != Types.WTF:
                    self.it_type = var_type
            else:
                # Literal value - update IT type
                self.it_type = self.infer_expr_type(node)

        # handle unary operations
        elif node_type == "unary_op":
            self.analyze_node(node.get('operand'))

            # update IT with result type of this expr
            expr_type = self.infer_expr_type(node)
            self.it_type = expr_type

        # handle binary operations
        elif node_type == "binary_op":
            self.analyze_node(node.get("left"))
            self.analyze_node(node.get("right"))

            # update IT with result type of this expr
            expr_type = self.infer_expr_type(node)
            self.it_type = expr_type

        # handle assignment
        elif node_type == "assignment":
            # analyze expression first
            self.analyze_node(node.get("expr"))
            target = node.get("target")
            info = self.lookup_var_info(target)
            if info is None:
                self.errors.append(f"line {node['line']}: assignment to undeclared variable '{target}'")
            else:
                # # update value in current scope
                # self.scopes[-1][target] = node.get("expr")

                expr_type = self.infer_expr_type(node.get("expr"))
                decl_type = info['declared_type']
                if decl_type not in [Types.NOOB, Types.ANY] and expr_type not in [decl_type, Types.WTF]:
                    self.errors.append(f"line {node['line']}: type mismatch assigning {expr_type} to {decl_type} ('{target}')")
                else:
                    if decl_type in [Types.NOOB, Types.ANY]:
                        info['declared_type'] = expr_type
                    info['current_type'] = expr_type
                info['initialized'] = True
                info['value'] = node.get("expr")

            # Update IT type
            expr_type = self.infer_expr_type(node.get("expr"))
            self.it_type = expr_type

        elif node_type == "visible":
            # analyze args
            self.in_visible_context = True  # Enter VISIBLE context
            for arg in node.get("args", []):
                self.analyze_node(arg)  # Just analyze the node, don't expect return type
                
                # Get the type after analysis (unused)
                arg_type = self.infer_expr_type(arg)
                
                # note: All types can be printed in LOLCODE (implicit conversion to YARN)
                # So no type checking needed here - VISIBLE can handle any type
            
            self.in_visible_context = False  # Exit VISIBLE context

            # return type is irrelevant
            return None

        # handle function definitions
        elif node_type == "func_def":
            func_name = node.get("name")
            self.current_func = func_name
            if func_name in self.functions:
                self.errors.append(f"line {node['line']}: function '{func_name}' already defined")
            # self.functions[func_name] = node
            else:
                self.functions[func_name] = {
                    'node': node,
                    'params': node.get("params", []),
                    'return_types': set()
                }

            # create new scope for function
            self.push_scope()
            self.in_function = True
            # declare parameters (now support dict or raw string)
            for param in node.get("params", []):
                # self.declare_variable(param)
                if isinstance(param, dict):
                    self._declare_param(param.get('name'), param.get('type'), line=node.get('line'))
                else:
                    self._declare_param(param, None, line=node.get('line'))

            # analyze function body
            for stmt in node.get("body", []):
                self.analyze_node(stmt)

            rtypes = self.function_returns.get(func_name, set())
            if len(rtypes) > 1:
                self.errors.append(
                    f"line {node['line']}: inconsistent return types in function '{func_name}': {sorted(rtypes)}"
                )

            # Store final resolved return type
            if func_name in self.functions:
                final_type = None
                if len(rtypes) == 1:
                    final_type = list(rtypes)[0]
                elif len(rtypes) == 0:
                    final_type = Types.NOOB   # treat as void
                else:
                    final_type = Types.ANY
                self.functions[func_name]['final_return_type'] = final_type
                self.functions[func_name]['return_types'] = rtypes

            self.in_function = False
            self.current_func = None
            self.pop_scope()