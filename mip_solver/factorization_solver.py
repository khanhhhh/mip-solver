import math
from typing import Optional

from mip_solver.circuit_sat_solver import VarNode, Node, And, Or, Not, satisfy


def Mul(*node_list: Node) -> Node:
    return And(*node_list)

def Xor2(node1: Node, node2: Node) -> Node:
    return Not(Or(And(node1, node2), And(Not(node1), Not(node2))))

def Add2(node1: Node, node2: Node) -> tuple[Node, Node]:
    """
    :return: sum, carry
    """
    return Xor2(node1, node2), And(node1, node2)

def Equal(node: Node, value: bool) -> Node:
    if value:
        return node
    else:
        return Not(node)

def Add(*node_list: Node) -> tuple[Node, ...]:
    def add(node_list: list[Node]) -> tuple[Node, list[Node]]:
        carry_list: list[Node] = []
        sum: Node = node_list[0]
        for i in range(1, len(node_list)):
            sum, carry = Add2(sum, node_list[i])
            carry_list.append(carry)
        return sum, carry_list
    sum_list_length: int = len(bin(len(node_list)))-2
    sum_list = []
    carry_list: list[Node] = list(node_list)
    for i in range(sum_list_length):
        if len(carry_list) == 0:
            break
        sum, carry_list = add(carry_list)
        sum_list.append(sum)
    return tuple(sum_list)

def factorize(i: int) -> int:
    bit_count = len(bin(i)) - 2
    bit_list = list(bin(i))[2:]
    bit_list.reverse()
    bit_list = [bool(int(b)) for b in bit_list] # bit list in reverse order
    bit_list.extend([False for _ in range(bit_count-1)])
    factor1 = [VarNode(name=f"factor1[{i}]") for i in range(bit_count)]
    factor2 = [VarNode(name=f"factor2[{i}]") for i in range(bit_count)]
    # factor1 >= 2
    dummy = And(Or(*factor1[1:]), Or(*factor2[1:]))
    #
    row_list: list[list[Optional[Node]]] = []
    for r in range(bit_count):
        row = [None for _ in range(r)]
        for c in range(bit_count):
            row.append(Mul(factor2[r], factor1[c]))
        row.extend([None for _ in range(bit_count-1-r)])
        row_list.append(row)
    col_list: list[list[Node]] = []
    for c in range(2*bit_count-1):
        col = [row_list[r][c] for r in range(bit_count) if row_list[r][c] is not None]
        col_list.append(col)

    cnf_list = []
    for i in range(2*bit_count-1):
        sum_list = Add(*col_list[i])
        cnf_list.append(Equal(sum_list[0], bit_list[i]))
        for j in range(1, len(sum_list)):
            if i+j < len(col_list):
                col_list[i+j].append(sum_list[j])

    objective = And(dummy, *cnf_list)
    if satisfy(objective):
        factor1_value = 0
        for i in range(bit_count):
            factor1_value += factor1[i].value * (2**i)
        return factor1_value
    return 1

