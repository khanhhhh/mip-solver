import mip


class Node:
    name: str
    var: mip.Optional[mip.Var]
    def __init__(self, name: str=""):
        self.name = name
        self.var = None

    def eval(self) -> bool:
        return NotImplemented

    def __repr__(self) -> str:
        return f"Node[{self.name}: {int(self.eval())}]"


class VarNode(Node):
    value: bool

    def __init__(self, value: bool=False, *args, **kwargs):
        super(VarNode, self).__init__(*args, **kwargs)
        self.value = value

    def eval(self) -> bool:
        return self.value


class OpNode(Node):
    op_list: tuple[Node, ...]

    def __init__(self, op_list: tuple[Node, ...], *args, **kwargs):
        super(OpNode, self).__init__(*args, **kwargs)
        self.op_list = op_list

    def eval(self) -> bool:
        return NotImplemented

class NotNode(OpNode):
    def __init__(self, ref: Node, *args, **kwargs):
        super(NotNode, self).__init__((ref,), *args, **kwargs)
    def eval(self) -> bool:
        return not self.op_list[0].eval()

class AndNode(OpNode):
    def __init__(self, op_list: tuple[Node, ...], *args, **kwargs):
        super(AndNode, self).__init__(op_list, *args, **kwargs)
    def eval(self) -> bool:
        for child in self.op_list:
            if child.eval() == False:
                return False
        return True



class OrNode(OpNode):
    def __init__(self, op_list: tuple[Node, ...], *args, **kwargs):
        super(OrNode, self).__init__(op_list, *args, **kwargs)
    def eval(self) -> bool:
        for child in self.op_list:
            if child.eval() == True:
                return True
        return False


def Not(node: Node) -> Node:
    return NotNode(node)


def Or(*node_list: Node) -> Node:
    return OrNode(node_list)

def And(*node_list: Node) -> Node:
    return AndNode(node_list)

