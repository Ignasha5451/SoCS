from binarytree import Node

import re

from lab1 import ExpressionValidator


class ExpressionOptimizer:
    def __init__(self, expression):
        self.expression = expression
        self.tokens = self._tokenizer()
        self._expression_status = True
        self._division_by_zero_indicators = ""
        self._need_optimize = True

    def _tokenizer(self):
        tokens = re.findall(r"\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[+\-*/()]", self.expression)
        return tokens

    def _division_by_zero_check(self):
        for token_i, token in enumerate(self.tokens):
            if re.match(r"0+\.?0+|0", token) and self.tokens[token_i - 1] == "/":
                self._division_by_zero_indicators = self._division_by_zero_indicators[:-1] + "^" * (len(token) + 1)
                self._expression_status = False
            else:
                self._division_by_zero_indicators += " " * len(token)

    def _addition_and_subtraction_optimizer(self):
        new_tokens = []
        token_i = 0
        while token_i < len(self.tokens):
            new_tokens.append(self.tokens[token_i])
            if token_i != 0:
                if self.tokens[token_i] == "-" and new_tokens[-2] == "(" and re.match(r"-?\d+\.\d+|-?\d+",
                                                                                      self.tokens[token_i + 1]):
                    new_tokens[-1] += self.tokens[token_i + 1]
                    token_i += 1
                elif (self.tokens[token_i] in "+-" and
                      re.match(r"-?\d+\.\d+|-?\d+", new_tokens[-2]) and
                      re.match(r"-?\d+\.\d+|-?\d+", self.tokens[token_i + 1])):
                    try:
                        if new_tokens[-3] not in "/*" and self.tokens[token_i + 2] not in "/*":
                            self._need_optimize = True
                            if new_tokens[-3] == "-":
                                val = eval(f"-{new_tokens.pop(-2)}{new_tokens.pop(-1)}{self.tokens[token_i + 1]}")
                                if val <= 0:
                                    new_tokens.append(str(val)[1:])
                                elif val > 0:
                                    new_tokens.pop()
                                    new_tokens.append("+")
                                    new_tokens.append(str(val))
                            elif new_tokens[-3] == "+":
                                val = eval(f"{new_tokens.pop(-2)}{new_tokens.pop(-1)}{self.tokens[token_i + 1]}")
                                if val < 0:
                                    new_tokens.pop()
                                    new_tokens.append("-")
                                    new_tokens.append(str(val)[1:])
                                elif val >= 0:
                                    new_tokens.append(str(val))
                            else:
                                new_tokens.append(
                                    str(eval(f"{new_tokens.pop(-2)}{new_tokens.pop(-1)}{self.tokens[token_i + 1]}")))
                            token_i += 1
                    except IndexError:
                        self._need_optimize = True
                        new_tokens.append(
                            str(eval(f"{new_tokens.pop(-2)}{new_tokens.pop(-1)}{self.tokens[token_i + 1]}")))
                        token_i += 1
                elif self.tokens[token_i] == "+" and new_tokens[-2] == "0":
                    self._need_optimize = True
                    new_tokens.pop()
                    new_tokens.pop()
                elif self.tokens[token_i] == "-" and new_tokens[-2] == "0":
                    self._need_optimize = True
                    new_tokens.pop(-2)
                elif self.tokens[token_i] in "+-" and self.tokens[token_i + 1] == "0":
                    self._need_optimize = True
                    new_tokens.pop()
                    token_i += 1
            else:
                if self.tokens[token_i] == "-" and re.match(r"-?\d+\.\d+|-?\d+", self.tokens[token_i + 1]):
                    new_tokens[-1] += self.tokens[token_i + 1]
                    token_i += 1
                elif self.tokens[token_i] == "+":
                    new_tokens.pop()
            token_i += 1
        self.tokens = new_tokens

    def _multiplication_and_division_optimizer(self):
        new_tokens = []
        token_i = 0
        while token_i < len(self.tokens):
            new_tokens.append(self.tokens[token_i])
            if (self.tokens[token_i] in "*/" and
                    re.match(r"-?\d+\.\d+|-?\d+", new_tokens[-2]) and
                    re.match(r"-?\d+\.\d+|-?\d+", self.tokens[token_i + 1])):
                self._need_optimize = True
                new_tokens.append(str(eval(f"{new_tokens.pop(-2)}{new_tokens.pop(-1)}{self.tokens[token_i + 1]}")))
                token_i += 1
            elif self.tokens[token_i] in "*/" and self.tokens[token_i + 1] == "1":
                self._need_optimize = True
                new_tokens.pop()
                token_i += 1
            elif self.tokens[token_i] == "*" and new_tokens[-2] == "1":
                self._need_optimize = True
                new_tokens.pop()
                new_tokens.pop()
            elif self.tokens[token_i] in "*/" and re.match(r"0+\.?0+|0", new_tokens[-2]):
                self._need_optimize = True
                new_tokens.pop()
                if self.tokens[token_i + 1] != "(":
                    token_i += 1
                    if self.tokens[token_i + 1] == "(":
                        bracket_deep = 1
                        token_i += 1
                        while bracket_deep:
                            token_i += 1
                            if self.tokens[token_i] == "(":
                                bracket_deep += 1
                            elif self.tokens[token_i] == ")":
                                bracket_deep -= 1
                else:
                    bracket_deep = 1
                    token_i += 1
                    while bracket_deep:
                        token_i += 1
                        if self.tokens[token_i] == "(":
                            bracket_deep += 1
                        elif self.tokens[token_i] == ")":
                            bracket_deep -= 1
            elif self.tokens[token_i] == "*" and re.match(r"0+\.?0+|0", self.tokens[token_i + 1]):
                self._need_optimize = True
                new_tokens.pop()
                if new_tokens[-1] != ")":
                    new_tokens.pop()
                else:
                    bracket_deep = 1
                    new_tokens.pop()
                    while bracket_deep:
                        if new_tokens[-1] == ")":
                            bracket_deep += 1
                        elif new_tokens[-1] == "(":
                            bracket_deep -= 1
                        new_tokens.pop()
                    else:
                        if new_tokens[-1] not in "+-*/":
                            new_tokens.pop()
            token_i += 1
        self.tokens = new_tokens

    def _brackets_optimizer(self):
        new_tokens = []
        token_i = 0
        while token_i < len(self.tokens):
            new_tokens.append(self.tokens[token_i])
            if self.tokens[token_i] == ")" and new_tokens[-3] == "(":
                if token_i == 2:
                    self._need_optimize = True
                    new_tokens.pop(-3)
                    new_tokens.pop()
                else:
                    if new_tokens[-4] in "*/":
                        self._need_optimize = True
                        new_tokens.pop(-3)
                        new_tokens.pop()
                    elif new_tokens[-4] == "+":
                        self._need_optimize = True
                        if new_tokens[-2].startswith("-"):
                            new_tokens[-4] = "-"
                            new_tokens[-2] = new_tokens[-2][1:]
                        new_tokens.pop(-3)
                        new_tokens.pop()
                    elif new_tokens[-4] == "-":
                        self._need_optimize = True
                        if new_tokens[-2].startswith("-"):
                            new_tokens[-4] = "+"
                            new_tokens[-2] = new_tokens[-2][1:]
                        new_tokens.pop(-3)
                        new_tokens.pop()
            token_i += 1

        self.tokens = new_tokens

    def optimizer(self):
        expression_validator = ExpressionValidator()
        if expression_validator.validation(expression):
            self._division_by_zero_check()
            if not self._expression_status:
                print("Division by zero at positions:", self.expression, self._division_by_zero_indicators, sep="\n")
                print("Expression is incorrect")
            else:
                print("Expression is correct")
                while self._need_optimize:
                    self._need_optimize = False
                    self._multiplication_and_division_optimizer()
                    self._addition_and_subtraction_optimizer()
                    self._brackets_optimizer()
                print()
                new_expression = "".join(self.tokens)
                if new_expression == self.expression:
                    print(f"Can't provide optimizations to this expression:\n{self.expression}")
                else:
                    print(f"Optimized expression:\n{new_expression}")
        else:
            print("Expression is incorrect")

    def _building_tree_list(self):
        self.optimizer()
        tokens_for_tree = self.tokens[:]
        while len(tokens_for_tree) > 3:
            token_i = 0
            while token_i < len(tokens_for_tree):
                if token_i < 2:
                    if (tokens_for_tree[token_i] == "/" and
                            tokens_for_tree[token_i + 1] != "("):
                        tokens_for_tree = ([[tokens_for_tree[token_i - 1], "/", tokens_for_tree[token_i + 1]]] +
                                           tokens_for_tree[token_i + 2:])
                        token_i += 1
                    elif (tokens_for_tree[token_i] == "*" and
                          tokens_for_tree[token_i + 1] != "("):
                        tokens_for_tree = ([[tokens_for_tree[token_i - 1], "*", tokens_for_tree[token_i + 1]]] +
                                           tokens_for_tree[token_i + 2:])
                        token_i += 1
                    elif (tokens_for_tree[token_i] == "-" and
                          tokens_for_tree[token_i + 1] != "(" and
                          tokens_for_tree[token_i + 2] not in ["*", "/"]):
                        tokens_for_tree = ([[tokens_for_tree[token_i - 1], "-", tokens_for_tree[token_i + 1]]] +
                                           tokens_for_tree[token_i + 2:])
                        token_i += 1
                    elif (tokens_for_tree[token_i] == "+" and
                          tokens_for_tree[token_i + 1] != "(" and
                          tokens_for_tree[token_i + 2] not in ["*", "/"]):
                        tokens_for_tree = ([[tokens_for_tree[token_i - 1], "+", tokens_for_tree[token_i + 1]]] +
                                           tokens_for_tree[token_i + 2:])
                        token_i += 1
                elif token_i > len(tokens_for_tree) - 3:
                    if (tokens_for_tree[token_i] == "/" and
                            tokens_for_tree[token_i - 1] != ")" and
                            tokens_for_tree[token_i - 2] != "/"):
                        tokens_for_tree = (tokens_for_tree[:token_i - 1] +
                                           [[tokens_for_tree[token_i - 1], "/", tokens_for_tree[token_i + 1]]])
                        token_i += 1
                    elif (tokens_for_tree[token_i] == "*" and
                          tokens_for_tree[token_i - 1] != ")" and
                          tokens_for_tree[token_i - 2] != "/"):
                        tokens_for_tree = (tokens_for_tree[:token_i - 1] +
                                           [[tokens_for_tree[token_i - 1], "*", tokens_for_tree[token_i + 1]]])
                        token_i += 1
                    elif (tokens_for_tree[token_i] == "-" and
                          tokens_for_tree[token_i - 1] != ")" and
                          tokens_for_tree[token_i - 2] not in ["-", "*", "/"]):
                        tokens_for_tree = (tokens_for_tree[:token_i - 1] +
                                           [[tokens_for_tree[token_i - 1], "-", tokens_for_tree[token_i + 1]]])
                        token_i += 1
                    elif (tokens_for_tree[token_i] == "+" and
                          tokens_for_tree[token_i - 1] != ")" and
                          tokens_for_tree[token_i - 2] not in ["-", "*", "/"]):
                        tokens_for_tree = (tokens_for_tree[:token_i - 1] +
                                           [[tokens_for_tree[token_i - 1], "+", tokens_for_tree[token_i + 1]]])
                        token_i += 1
                else:
                    if (tokens_for_tree[token_i] == "/" and
                            tokens_for_tree[token_i - 1] != ")" and
                            tokens_for_tree[token_i + 1] != "(" and
                            tokens_for_tree[token_i - 2] != "/"):
                        if tokens_for_tree[token_i + 2] == ")" and tokens_for_tree[token_i - 2] == "(":
                            tokens_for_tree = (tokens_for_tree[:token_i - 2] +
                                               [[tokens_for_tree[token_i - 1], "/", tokens_for_tree[token_i + 1]]] +
                                               tokens_for_tree[token_i + 3:])
                        else:
                            tokens_for_tree = (tokens_for_tree[:token_i - 1] +
                                               [[tokens_for_tree[token_i - 1], "/", tokens_for_tree[token_i + 1]]] +
                                               tokens_for_tree[token_i + 2:])
                            token_i += 1
                    elif (tokens_for_tree[token_i] == "*" and
                          tokens_for_tree[token_i - 1] != ")" and
                          tokens_for_tree[token_i + 1] != "(" and
                          tokens_for_tree[token_i - 2] != "/"):
                        if tokens_for_tree[token_i + 2] == ")" and tokens_for_tree[token_i - 2] == "(":
                            tokens_for_tree = (tokens_for_tree[:token_i - 2] +
                                               [[tokens_for_tree[token_i - 1], "*", tokens_for_tree[token_i + 1]]] +
                                               tokens_for_tree[token_i + 3:])
                        else:
                            tokens_for_tree = (tokens_for_tree[:token_i - 1] +
                                               [[tokens_for_tree[token_i - 1], "*", tokens_for_tree[token_i + 1]]] +
                                               tokens_for_tree[token_i + 2:])
                            token_i += 1
                    elif (tokens_for_tree[token_i] == "-" and
                          tokens_for_tree[token_i - 1] != ")" and
                          tokens_for_tree[token_i + 1] != "(" and
                          tokens_for_tree[token_i - 2] not in ["-", "*", "/"] and
                          tokens_for_tree[token_i + 2] not in ["*", "/"]):
                        if tokens_for_tree[token_i + 2] == ")" and tokens_for_tree[token_i - 2] == "(":
                            tokens_for_tree = (tokens_for_tree[:token_i - 2] +
                                               [[tokens_for_tree[token_i - 1], "-", tokens_for_tree[token_i + 1]]] +
                                               tokens_for_tree[token_i + 3:])
                        else:
                            tokens_for_tree = (tokens_for_tree[:token_i - 1] +
                                               [[tokens_for_tree[token_i - 1], "-", tokens_for_tree[token_i + 1]]] +
                                               tokens_for_tree[token_i + 2:])
                            token_i += 1
                    elif (tokens_for_tree[token_i] == "+" and
                          tokens_for_tree[token_i - 1] != ")" and
                          tokens_for_tree[token_i + 1] != "(" and
                          tokens_for_tree[token_i - 2] not in ["-", "*", "/"] and
                          tokens_for_tree[token_i + 2] not in ["*", "/"]):
                        if tokens_for_tree[token_i + 2] == ")" and tokens_for_tree[token_i - 2] == "(":
                            tokens_for_tree = (tokens_for_tree[:token_i - 2] +
                                               [[tokens_for_tree[token_i - 1], "+", tokens_for_tree[token_i + 1]]] +
                                               tokens_for_tree[token_i + 3:])
                        else:
                            tokens_for_tree = (tokens_for_tree[:token_i - 1] +
                                               [[tokens_for_tree[token_i - 1], "+", tokens_for_tree[token_i + 1]]] +
                                               tokens_for_tree[token_i + 2:])
                            token_i += 1
                token_i += 1
        return tokens_for_tree

    def building_tree(self):
        tokens_for_tree = self._building_tree_list()

        def building_tree_helper(tokens_for_tree):
            root = MyNode(value=tokens_for_tree[1])
            root.left = MyNode(value=tokens_for_tree[0])
            root.right = MyNode(value=tokens_for_tree[2])
            if isinstance(root.left.value, list):
                root.left = building_tree_helper(root.left.value)
            if isinstance(root.right.value, list):
                root.right = building_tree_helper(root.right.value)
            return root

        return building_tree_helper(tokens_for_tree)

    def print_tree(self):
        my_root = self.building_tree()

        def print_tree_helper(my_root):
            root = Node(my_root.value)
            if my_root.left:
                root.left = print_tree_helper(my_root.left)
            if my_root.right:
                root.right = print_tree_helper(my_root.right)
            return root

        print()
        print("Expression tree:")
        print(print_tree_helper(my_root))


class MyNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


if __name__ == "__main__":
    """
    a+b*(c*cos(t-a*x)-d*sin(t+a*x)/(4.81*k-q*t))/(d*cos(t+a*y/f1(5.616*x-t))+c*sin(t-a*y*(u-v*i)))
    1*2/a+1+2-(1*c/1*1+1+0-2+0)+cos()-sin(1+2)*tg(0-1+a*1)
    0*c+1*a*1+1*5/2*3*1/3+3*21+0*(a+b+0*c)/1*0+(4*5)
    0*(10/1)+(1.618+0)+(5-3)/1-(0+7*2.71)
    """
    expression = "1*2/a+1+2-(1*c/1*1+1+0-2+0)-(1+2)*(0-1+a*1)"
    expression_optimizer = ExpressionOptimizer(expression)
    expression_optimizer.print_tree()
