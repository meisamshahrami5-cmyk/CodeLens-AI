import ast
from pathlib import Path

from app.core.parser import PythonParser


class CodeAnalyzer(ast.NodeVisitor):
    """Analyze Python source code using AST."""

    def __init__(self, file_path):
        self.file_path = Path(file_path)

        self.functions = []
        self.classes = []
        self.imports = []
        self.issues = []
        self.todos = []
        self.print_statements = []

        self.current_function = None
        self.current_class = None

        self.source_lines = []

    def analyze(self):
        parser = PythonParser(self.file_path)
        result = parser.parse()

        self.source_lines = result["source"].splitlines()

        if result["error"]:
            self.issues.append({
                "type": "Syntax Error",
                "severity": "Critical",
                "line": result["error"]["line"],
                "message": result["error"]["message"],
            })

            return self.get_result()

        tree = result["tree"]

        self.visit(tree)

        self._find_todos()
        self._check_long_functions()
        self._check_large_classes()
        self._check_unreachable_code()

        return self.get_result()

    # ---------------------------------------------------------
    # Functions
    # ---------------------------------------------------------

    def visit_FunctionDef(self, node):

        function_info = {
            "name": node.name,
            "line": node.lineno,
            "end_line": getattr(node, "end_lineno", node.lineno),
            "arguments": len(node.args.args),
            "is_async": False,
            "class": self.current_class,
        }

        self.functions.append(function_info)

        previous_function = self.current_function
        self.current_function = node.name

        self.generic_visit(node)

        self.current_function = previous_function

    # ---------------------------------------------------------
    # Async Functions
    # ---------------------------------------------------------

    def visit_AsyncFunctionDef(self, node):

        function_info = {
            "name": node.name,
            "line": node.lineno,
            "end_line": getattr(node, "end_lineno", node.lineno),
            "arguments": len(node.args.args),
            "is_async": True,
            "class": self.current_class,
        }

        self.functions.append(function_info)

        previous_function = self.current_function
        self.current_function = node.name

        self.generic_visit(node)

        self.current_function = previous_function

    # ---------------------------------------------------------
    # Classes
    # ---------------------------------------------------------

    def visit_ClassDef(self, node):

        class_info = {
            "name": node.name,
            "line": node.lineno,
            "end_line": getattr(node, "end_lineno", node.lineno),
            "methods": 0,
        }

        self.classes.append(class_info)

        previous_class = self.current_class
        self.current_class = node.name

        self.generic_visit(node)

        self.current_class = previous_class

    # ---------------------------------------------------------
    # Imports
    # ---------------------------------------------------------

    def visit_Import(self, node):

        for alias in node.names:

            self.imports.append({
                "type": "import",
                "name": alias.name,
                "line": node.lineno,
            })

        self.generic_visit(node)

    # ---------------------------------------------------------

    def visit_ImportFrom(self, node):

        module = node.module or ""

        for alias in node.names:

            self.imports.append({
                "type": "from",
                "module": module,
                "name": alias.name,
                "line": node.lineno,
            })

        self.generic_visit(node)

    # ---------------------------------------------------------
    # print()
    # ---------------------------------------------------------

    def visit_Call(self, node):

        if isinstance(node.func, ast.Name):

            if node.func.id == "print":

                self.print_statements.append({
                    "line": node.lineno,
                })

                self.issues.append({
                    "type": "Debug Print",
                    "severity": "Low",
                    "line": node.lineno,
                    "message": (
                        "print() found in source code. "
                        "Consider using logging instead."
                    ),
                })

        self.generic_visit(node)

    # ---------------------------------------------------------
    # TODO / FIXME
    # ---------------------------------------------------------

    def _find_todos(self):

        for index, line in enumerate(self.source_lines, start=1):

            upper_line = line.upper()

            if "TODO" in upper_line:

                self.todos.append({
                    "type": "TODO",
                    "line": index,
                    "text": line.strip(),
                })

                self.issues.append({
                    "type": "TODO",
                    "severity": "Info",
                    "line": index,
                    "message": line.strip(),
                })

            if "FIXME" in upper_line:

                self.todos.append({
                    "type": "FIXME",
                    "line": index,
                    "text": line.strip(),
                })

                self.issues.append({
                    "type": "FIXME",
                    "severity": "Medium",
                    "line": index,
                    "message": line.strip(),
                })

    # ---------------------------------------------------------
    # Long functions
    # ---------------------------------------------------------

    def _check_long_functions(self):

        max_lines = 50

        for function in self.functions:

            length = (
                function["end_line"]
                - function["line"]
                + 1
            )

            if length > max_lines:

                self.issues.append({
                    "type": "Long Function",
                    "severity": "Medium",
                    "line": function["line"],
                    "message": (
                        f"Function '{function['name']}' "
                        f"is {length} lines long."
                    ),
                })

    # ---------------------------------------------------------
    # Large classes
    # ---------------------------------------------------------

    def _check_large_classes(self):

        max_lines = 300

        for class_info in self.classes:

            length = (
                class_info["end_line"]
                - class_info["line"]
                + 1
            )

            if length > max_lines:

                self.issues.append({
                    "type": "Large Class",
                    "severity": "Medium",
                    "line": class_info["line"],
                    "message": (
                        f"Class '{class_info['name']}' "
                        f"is {length} lines long."
                    ),
                })

    # ---------------------------------------------------------
    # Unreachable code
    # ---------------------------------------------------------

    def _check_unreachable_code(self):

        class UnreachableVisitor(ast.NodeVisitor):

            def __init__(self, analyzer):
                self.analyzer = analyzer

            def check_body(self, body):

                terminated = False

                for node in body:

                    if terminated:

                        self.analyzer.issues.append({
                            "type": "Unreachable Code",
                            "severity": "Medium",
                            "line": node.lineno,
                            "message": (
                                "Code appears after a "
                                "return/break/continue/raise."
                            ),
                        })

                    if isinstance(
                        node,
                        (
                            ast.Return,
                            ast.Raise,
                            ast.Break,
                            ast.Continue,
                        ),
                    ):
                        terminated = True

                    self.visit(node)

            def visit_FunctionDef(self, node):
                self.check_body(node.body)

            def visit_AsyncFunctionDef(self, node):
                self.check_body(node.body)

            def visit_If(self, node):
                self.check_body(node.body)

                if node.orelse:
                    self.check_body(node.orelse)

        visitor = UnreachableVisitor(self)
        visitor.visit(ast.parse("\n".join(self.source_lines)))

    # ---------------------------------------------------------
    # Result
    # ---------------------------------------------------------

    def get_result(self):

        return {
            "file": str(self.file_path),
            "functions": self.functions,
            "classes": self.classes,
            "imports": self.imports,
            "todos": self.todos,
            "print_statements": self.print_statements,
            "issues": self.issues,
        }