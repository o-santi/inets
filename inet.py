from dataclasses import dataclass
from typing import List
from enum import IntEnum, auto

class Label(IntEnum):
    Erase = auto()
    Zero  = auto()
    Plus  = auto()
    Copy  = auto()
    Root  = auto()

    def arity(self) -> int:
        match self:
            case Label.Erase: return 0
            case Label.Zero:  return 0
            case Label.Plus:  return 2
            case Label.Copy:  return 2
            case Label.Root:  return 0
            
    def __str__(self) -> str:
        match self:
            case Label.Erase: return "Erase"
            case Label.Zero:  return "Zero"
            case Label.Plus:  return "Plus"
            case Label.Copy:  return "Copy"
            case Label.Root:  return "Root"

NodeId = int
    
@dataclass(frozen=True)
class Node:
    node_id: NodeId
    label: Label
    
@dataclass(frozen=True)
class Porta:
    node: Node
    port: int
        
class InteractionNet:

    def __init__(self):
        self.arestas = dict()        
        self.node_count = 0
        self.portas_ativas = list()
            
        
    def normalize(self):
        while (len(self.portas_ativas) > 0):
            left, right = self.portas_ativas.pop() # Porta y, Porta z,
            self.apply_rewrite(left.node, right.node)
            
    def apply_rewrite(self, left: Node, right: Node) -> bool:
        match left.label, right.label:
            case (Label.Erase, Label.Zero):
                self.delete_node(left)
                self.delete_node(right)

            case (Label.Zero, Label.Copy) | (Label.Erase, Label.Copy) | (Label.Erase, Label.Plus) | (Label.Zero, Label.Plus):
                left1 = self.add_node(left.label)
                left2 = self.add_node(left.label)
                conn1 = self.arestas[Porta(right, 1)]
                conn2 = self.arestas[Porta(right, 2)]
                self.connect_ports(Porta(left1, 0), conn1)
                self.connect_ports(Porta(left2, 0), conn2)

                self.delete_node(left)
                self.delete_node(right)

            case (Label.Plus, Label.Copy):
                pls1 = self.add_node(Label.Plus)
                pls2 = self.add_node(Label.Plus)
                cpy1 = self.add_node(Label.Copy)
                cpy2 = self.add_node(Label.Copy)
                conn1 = self.arestas[Porta(right, 1)]
                conn2 = self.arestas[Porta(right, 2)]
                conn3 = self.arestas[Porta(left,  1)]
                conn4 = self.arestas[Porta(left,  2)]
                self.connect_ports(Porta(pls1, 0), conn1)
                self.connect_ports(Porta(pls2, 0), conn2)
                self.connect_ports(Porta(cpy1, 0), conn3)
                self.connect_ports(Porta(cpy2, 0), conn4)

                self.connect_ports(Porta(pls1, 1), Porta(cpy1, 1))
                self.connect_ports(Porta(pls1, 2), Porta(cpy2, 1))
                self.connect_ports(Porta(pls2, 1), Porta(cpy1, 2))
                self.connect_ports(Porta(pls2, 2), Porta(cpy2, 2))
                
                self.delete_node(left)
                self.delete_node(right)
                
                
    def add_node(self, label: Label) -> Node:
        new_id = self.node_count
        self.node_count += 1
        node = Node(new_id, label)
        return node

    def connect_ports(self, left: Porta, right: Porta):
        self.arestas[left] = right
        self.arestas[right] = left
        if (left.port == right.port == 0): # se as portas estiverem ativas
            # usa a ordem entre as labels para 
            if (left.node.label < right.node.label):
                self.portas_ativas.append((left, right))
            else:
                self.portas_ativas.append((right, left))
            
    def delete_node(self, node: Node):
        for i in range(node.label.arity() + 1):
            del self.arestas[Porta(node, i)]
        
    def print_arestas(self):
        print("Inet arestas:")
        for left in self.arestas.keys():
            right = self.arestas[left]
            print(f"{left.node.label}({left.node.node_id}) @ {left.port} --> {right.node.label}({right.node.node_id}) @ {right.port}")

            
if __name__ == "__main__":

    def zero_erased():
        inet = InteractionNet()
        zero = inet.add_node(Label.Zero)
        eras = inet.add_node(Label.Erase)

        inet.connect_ports(Porta(zero, 0), Porta(eras, 0))

        # Zero > - < Erase
   
        inet.normalize()
        assert len(inet.arestas) == 0
        print("zero_erased .... OK")

    def zero_copy_into_erased():
        inet = InteractionNet()
        
        zero = inet.add_node(Label.Zero)
        copy = inet.add_node(Label.Copy)
        era1 = inet.add_node(Label.Erase)
        era2 = inet.add_node(Label.Erase)

        #                 / Erase 
        # Zero > ~ < Copy 
        #                 \ Erase

        inet.connect_ports(Porta(zero, 0), Porta(copy, 0))
        inet.connect_ports(Porta(era1, 0), Porta(copy, 1))
        inet.connect_ports(Porta(era2, 0), Porta(copy, 2))

        # inet.print_arestas()
        inet.normalize()
        # inet.print_arestas()
        assert len(inet.arestas) == 0
        print("zero_copy_into_erased .... OK")

    def plus_into_copy():
        inet = InteractionNet()
        rot1 = inet.add_node(Label.Zero)
        rot2 = inet.add_node(Label.Zero)
        rot3 = inet.add_node(Label.Erase)
        rot4 = inet.add_node(Label.Erase)

        plus = inet.add_node(Label.Plus)
        copy = inet.add_node(Label.Copy)

        inet.connect_ports(Porta(plus, 0), Porta(copy, 0))
        inet.connect_ports(Porta(plus, 1), Porta(rot1, 0))
        inet.connect_ports(Porta(plus, 2), Porta(rot2, 0))
        inet.connect_ports(Porta(copy, 1), Porta(rot3, 0))
        inet.connect_ports(Porta(copy, 2), Porta(rot4, 0))

        # Zero \               / Erase
        #       Plus > ~ < Copy
        # Zero /               \ Erase

        # first becomes
        # Zero > ~ Copy --- Plus > ~ < Erase
        #               \ /
        #                X
        #               / \        
        # Zero > ~ Copy --- Plus > ~ < Erase
        # which then, becomes
        # Zero > ~ < Erase
        # Zero > ~ < Erase
        # Zero > ~ < Erase
        # Zero > ~ < Erase
        # which annihilates the whole graph.
        
        inet.normalize()
        assert len(inet.arestas) == 0
        print("plus_into_copy .... OK")

    def naturals(number):
        
        inet = InteractionNet()

        left = inet.add_node(Label.Erase)
        right = inet.add_node(Label.Zero)

        def rec(n, free_left: Porta, free_right: Porta):
            if n == 0:            
                zero = inet.add_node(Label.Zero)
                eras = inet.add_node(Label.Erase)
                inet.connect_ports(Porta(zero, 0), free_left)
                inet.connect_ports(Porta(eras, 0), free_right)
            else:
                plus = inet.add_node(Label.Plus)
                copy = inet.add_node(Label.Copy)
                inet.connect_ports(Porta(copy, 0), free_left)
                inet.connect_ports(Porta(plus, 0), free_right)

                inet.connect_ports(Porta(copy, 1), Porta(plus, 2))
                rec(n - 1, Porta(copy, 2), Porta(plus, 1))

        rec(number, Porta(left, 0), Porta(right, 0))

        inet.normalize()
        # inet.print_arestas()

        assert len(inet.arestas) == 0
        print(f"naturals({number}) .... OK ")
        
    zero_erased()
    zero_copy_into_erased()
    plus_into_copy()
    naturals(500)

