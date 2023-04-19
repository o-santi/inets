from dataclasses import dataclass
from typing import List
from enum import Enum, auto

class Label(Enum):
    Plus  = auto()
    Copy  = auto()
    Erase = auto()
    Zero  = auto()
    Root  = auto()

NodeId = int
    
@dataclass(frozen=True)
class Node:
    node_id: NodeId
    label: Label
    
@dataclass(frozen=True)
class Porta:
    node: Node
    port: int

class ArestaMap(dict):

    def __init__(self, *args, **kwargs):
        super(ArestaMap, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        # assert super(ArestaMap, self).
        # assert value not in super(ArestaMap, self)
        super(ArestaMap, self).__setitem__(key, value)
        super(ArestaMap, self).__setitem__(value, key)

    def __delitem__(self, key):
        val = super(ArestaMap, self).__getitem__(key)
        super(ArestaMap, self).__delitem__(key)
        super(ArestaMap, self).__delitem__(val)
        
        
class InteractionNet:

    def __init__(self):
        self.arestas = dict()
        self.node_count = 0
        self.arestas_talvez_ativas = list()

    def normalize(self):
        while (len(self.arestas_talvez_ativas) > 0):
            left = self.arestas_talvez_ativas.pop()
            right = self.arestas[left]
            self.print_arestas()
            self.arestas_talvez_ativas.remove(right)
            if left.port == right.port == 0:
                self.apply_rewrite(left.node, right.node)            
                
    def apply_rewrite(self, left: Node, right: Node) -> bool:
        match left.label, right.label:        
            case (Label.Zero, Label.Erase) | (Label.Erase, Label.Zero):
                del self.arestas[Porta(left, 0)]
                del self.arestas[Porta(right, 0)]
            case (Label.Zero, Label.Copy) | (Label.Erase, Label.Copy) | (Label.Erase, Label.Plus) | (Label.Zero, Label.Plus):
                left1 = self.add_node(left.label)
                left2 = self.add_node(left.label)
                conn1 = self.arestas[Porta(right, 1)]
                conn2 = self.arestas[Porta(right, 2)]
                self.connect_ports(Porta(left1, 0), conn1)
                self.connect_ports(Porta(left2, 0), conn2)

                del self.arestas[Porta(left, 0)]
                del self.arestas[Porta(right, 0)]
                del self.arestas[Porta(right, 1)]
                del self.arestas[Porta(right, 2)]

            case (Label.Copy, Label.Zero) | (Label.Copy, Label.Erase) | (Label.Plus, Label.Erase) | (Label.Plus, Label.Zero):
                right1 = self.add_node(left.label)
                right2 = self.add_node(left.label)
                conn1 = self.arestas[Porta(left, 1)] 
                conn2 = self.arestas[Porta(left, 2)]
                self.connect_ports(Porta(right1, 0), conn1)
                self.connect_ports(Porta(right2, 0), conn2)

                del self.arestas[Porta(right, 0)]
                del self.arestas[Porta(left, 0)]
                del self.arestas[Porta(left, 1)]
                del self.arestas[Porta(left, 2)]
                
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

                del self.arestas[Porta(right, 0)]
                del self.arestas[Porta(right, 1)]
                del self.arestas[Porta(right, 2)]
                
                del self.arestas[Porta(left, 0)]
                del self.arestas[Porta(left, 1)]
                del self.arestas[Porta(left, 2)]

            case (Label.Copy, Label.Plus):                
                pls1 = self.add_node(Label.Plus)
                pls2 = self.add_node(Label.Plus)
                cpy1 = self.add_node(Label.Copy)
                cpy2 = self.add_node(Label.Copy)
                conn1 = self.arestas[Porta(left, 1)]
                conn2 = self.arestas[Porta(left, 2)]
                conn3 = self.arestas[Porta(right,  1)]
                conn4 = self.arestas[Porta(right,  2)]
                self.connect_ports(Porta(pls1, 0), conn1)
                self.connect_ports(Porta(pls2, 0), conn2)
                self.connect_ports(Porta(cpy1, 0), conn3)
                self.connect_ports(Porta(cpy2, 0), conn4)

                self.connect_ports(Porta(pls1, 1), Porta(cpy1, 1))
                self.connect_ports(Porta(pls1, 2), Porta(cpy2, 1))
                self.connect_ports(Porta(pls2, 1), Porta(cpy1, 2))
                self.connect_ports(Porta(pls2, 2), Porta(cpy2, 2))

                del self.arestas[Porta(right, 0)]
                del self.arestas[Porta(right, 1)]
                del self.arestas[Porta(right, 2)]
                
                del self.arestas[Porta(left, 0)]
                del self.arestas[Porta(left, 1)]
                del self.arestas[Porta(left, 2)]
                
    def add_node(self, label: Label) -> Node:
        new_id = self.node_count
        self.node_count += 1
        return Node(new_id, label)

    def connect_ports(self, left: Porta, right: Porta):
        assert left not in arestas
        assert right not in arestas
        self.arestas[left] = right
        self.arestas[right] = left
        self.arestas_talvez_ativas.append(left)
        self.arestas_talvez_ativas.append(right)

    def print_arestas(self):
        print("Inet arestas:")
        for left in self.arestas.keys():
            right = self.arestas[left]
            print(f"{left.node.label}({left.node.node_id}) @ {left.port} --> {right.node.label}({right.node.node_id}) @ {right.port}")
            
            
            
if __name__ == "__main__":

    def zero_copy_into_erased():
        inet = InteractionNet()
        
        zero = inet.add_node(Label.Zero)
        copy = inet.add_node(Label.Copy)
        era1 = inet.add_node(Label.Erase)
        era2 = inet.add_node(Label.Erase)


        inet.connect_ports(Porta(zero, 0), Porta(copy, 0))
        inet.connect_ports(Porta(era1, 0), Porta(copy, 1))
        inet.connect_ports(Porta(era2, 0), Porta(copy, 2))

        inet.print_arestas()
        inet.normalize()
        inet.print_arestas()
        assert len(inet.arestas) == 0
        print("zero_copy_into_erased .... OK")

    def zero_erased():
        inet = InteractionNet()
        zero = inet.add_node(Label.Zero)
        eras = inet.add_node(Label.Erase)

        inet.connect_ports(Porta(zero, 0), Porta(eras, 0))

        inet.normalize()
        assert len(inet.arestas) == 0
        print("zero_erased .... OK")

    def plus_into_copy():
        inet = InteractionNet()
        rot1 = inet.add_node(Label.Root)
        rot2 = inet.add_node(Label.Root)
        rot3 = inet.add_node(Label.Root)
        rot4 = inet.add_node(Label.Root)

        plus = inet.add_node(Label.Plus)
        copy = inet.add_node(Label.Copy)

        inet.connect_ports(Porta(plus, 0), Porta(copy, 0))
        inet.connect_ports(Porta(plus, 1), Porta(rot1, 0))
        inet.connect_ports(Porta(plus, 2), Porta(rot2, 0))
        inet.connect_ports(Porta(copy, 1), Porta(rot3, 0))
        inet.connect_ports(Porta(copy, 2), Porta(rot4, 0))


        inet.normalize()
        inet.print_arestas()
        
    zero_erased()
    zero_copy_into_erased()

    plus_into_copy()
