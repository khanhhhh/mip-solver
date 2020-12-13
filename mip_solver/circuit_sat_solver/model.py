import mip

from mip_solver.circuit_sat_solver.node import Node, VarNode, OpNode, NotNode, OrNode, AndNode


def satisfy(root: Node) -> bool:
    model = mip.Model()
    model.verbose = False
    leaf_node_set: set[VarNode] = set()
    node_set: set[Node] = set()
    def add_var(node: Node):
        if node in node_set:
            return
        if isinstance(node, VarNode):
            leaf_node_set.add(node)
        node.var = model.add_var(var_type=mip.BINARY)
        if isinstance(node, OpNode):
            for child in node.op_list:
                add_var(child)
    add_var(root)
    # constraints
    def add_constr(node: Node):
        if isinstance(node, NotNode):
            # either one of the var is 1
            model.add_constr(mip.xsum([node.var, node.op_list[0].var]) == 1)
        if isinstance(node, OrNode):
            # var is greater or equal than all child
            for child in node.op_list:
                model.add_constr(node.var >= child.var)
            # var is 1 if at least one of the child is 1
            model.add_constr(node.var <= mip.xsum([child.var for child in node.op_list]))
        if isinstance(node, AndNode):
            # var is less or equal than all child
            for child in node.op_list:
                model.add_constr(node.var <= child.var)
            # all child is 1 -> var is 1
            model.add_constr(node.var + len(node.op_list) - 1 >= mip.xsum([child.var for child in node.op_list]))
        if isinstance(node, OpNode):
            for child in node.op_list:
                add_constr(child)

    add_constr(root)
    # root must be true
    model.add_constr(root.var == 1)
    model.optimize()
    if model.num_solutions:
        for node in leaf_node_set:
            node.value = float(node.var.x) > 0.5
        return True

    return False