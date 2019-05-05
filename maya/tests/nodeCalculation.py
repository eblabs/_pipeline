import ast
import operator
import maya.cmds as cmds

## operation functions
def _add(left, right):
    strBool_l = isinstance(left, basestring)
    strBool_r = isinstance(right, basestring)
    if strBool_l or strBool_r:
        add = cmds.createNode('addDoubleLinear')
        for i, attr in enumerate([left, right]):
            if isinstance(attr, basestring):
                cmds.connectAttr(attr, '{}.input{}'.format(add, i+1))
            else:
                cmds.setAttr('{}.input{}'.format(add, i+1), attr)
        return add+'.output'
    else:
        return left+right

def _mult(left, right):
    strBool_l = isinstance(left, basestring)
    strBool_r = isinstance(right, basestring)
    if strBool_l or strBool_r:
        mult = cmds.createNode('multDoubleLinear')
        for i, attr in enumerate([left, right]):
            if isinstance(attr, basestring):
                cmds.connectAttr(attr, '{}.input{}'.format(mult, i+1))
            else:
                cmds.setAttr('{}.input{}'.format(mult, i+1), attr)
        return mult+'.output'
    else:
        return left*right

def _minus(left, right):
    strBool_l = isinstance(left, basestring)
    strBool_r = isinstance(right, basestring)
    if strBool_l or strBool_r:
        add = cmds.createNode('addDoubleLinear')
        if strBool_r:
            mult = cmds.createNode('multDoubleLinear')
            cmds.connectAttr(right, mult+'.input1')
            cmds.setAttr(mult+'.input2', -1)
            cmds.connectAttr(mult+'.output', add+'.input2')
        else:
            cmds.setAttr(add+'.input2', right)
        if strBool_l:
            cmds.connectAttr(left, add+'.input1')
        else:
            cmds.setAttr(add+'.input1', left)
        return add+'.output'
    else:
        return left-right

def _divide(left, right):
    strBool_l = isinstance(left, basestring)
    strBool_r = isinstance(right, basestring)
    if strBool_l or strBool_r:
        div = cmds.createNode('multiplyDivide')
        cmds.setAttr(div+'.operation', 2)
        for i, attr in enumerate([left, right]):
            if isinstance(attr, basestring):
                cmds.connectAttr(attr, '{}.input{}X'.format(div, i+1))
            else:
                cmds.setAttr('{}.input{}X'.format(div, i+1), attr)
        return div+'.outputX'
    else:
        return left/float(right)

def _inverse(value):
    inv = cmds.createNode('reverse')
    cmds.connectAttr(value, inv+'.inputX')
    return inv+'.outputX'

def _uSub(value):
    strBool = isinstance(value, basestring)
    if strBool:
        mult = cmds.createNode('multDoubleLinear')
        cmds.connectAttr(value, mult+'.input1')
        cmds.setAttr(mult+'.input2', -1)
        return mult+'.output'
    else:
        return -value




_BINOP_MAP = {
    ast.Add: _add,
    ast.Sub: _minus,
    ast.Mult: _mult,
    ast.Div: _divide,
}

_UNARYOP_MAP = {
    ast.USub : _uSub,
    ast.Invert : _inverse
}


class Calc(ast.NodeVisitor):

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return _BINOP_MAP[type(node.op)](left, right)

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        return _UNARYOP_MAP[type(node.op)](operand)

    def visit_Num(self, node):
        return node.n

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_Attribute(self, node):
        return '{}.{}'.format(node.value.id, node.attr)

    @classmethod
    def evaluate(cls, expression):
        tree = ast.parse(expression)
        calc = cls()
        return calc.visit(tree.body[0])


def nodeCalculation(expression, affectAttr=None):
    outputAttr = Calc.evaluate(expression)
    if affectAttr:
        cmds.connectAttr(outputAttr, affectAttr)
    return outputAttr

## example
# nodeCalculation('(pCube1.tx*2-pCube2.ty)/2', affectAttr='pCube3.tz')