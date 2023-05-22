use std::hash::Hash;

type NodeId = u8;

trait Label where Self: Sized + Copy + Hash + PartialEq + Eq + std::fmt::Debug {
  fn arity(&self) -> usize;
  fn rewrite(inet: &mut InteractionNet<Self>, left: Vec<Porta<Self>>, right: Vec<Porta<Self>>);
}

#[derive(Debug, Clone, Copy, Hash, PartialEq, Eq)]
struct Node<T: Label> {
  id: NodeId,
  label: T
}

#[derive(Debug, Hash, PartialEq, Eq)]
#[must_use]
struct Porta<T: Label> {
  node: Node<T>,
  port: usize,
}

// impl<T: Label> Drop for Porta<T> {
//   fn drop(&mut self) {
//     panic!("All ports must be used exactly once.")
//   }
// }


struct InteractionNet<T:Label> {
  arestas: Vec<(Porta<T>, Porta<T>)>,
  portas_ativas: Vec<(Porta<T>, Porta<T>)>,
  node_count: u8
}

impl<T:Label> InteractionNet<T> {
  
  fn new() -> Self {
    let arestas = Vec::new();
    let portas_ativas = Vec::new();
    let node_count = 0;
    InteractionNet { arestas, portas_ativas, node_count }
  }

  fn add_node(&mut self, label: T) -> Vec<Porta<T>> {
    let new_id = self.node_count;
    self.node_count += 1;
    let arity = T::arity(&label);
    let mut ret = Vec::with_capacity(arity);
    let node = Node { id: new_id, label };
    for port in 0..(arity + 1) {
      ret.push(Porta { node, port });
    }
    ret
  }

  fn connect_ports(&mut self, left: Porta<T>, right: Porta<T>) {
    if left.port == 0 && right.port == 0 {
      self.portas_ativas.push((left, right));
    } else {
      self.arestas.push((left, right));
    }
  }

  fn get_connected(&mut self, port: Porta<T>) -> Porta<T> {
    for (i, pair) in self.arestas.iter().enumerate() {
      match pair {
        (left, _) if left == &port => {
          let (_, right) = self.arestas.swap_remove(i);
          return right;
        }
        (_, right) if right == &port => {
          let (left, _) = self.arestas.swap_remove(i);
          return left;
        }
        _ => {}
      }
    }
    panic!("All ports should be connected");
  }

  fn get_auxiliary_ports(&mut self, porta: Porta<T>) -> Vec<Porta<T>> {
    let node = porta.node;
    let mut ports = vec![porta];
    for i in 0..T::arity(&node.label) {
      let port = self.get_connected(Porta { node, port: i + 1});
      ports.push(port);
    }
    ports
  }
  
  fn normalize(&mut self) {
    while let Some((left, right)) = self.portas_ativas.pop() {
      let left_ports  = self.get_auxiliary_ports(left);
      let right_ports = self.get_auxiliary_ports(right);
      T::rewrite(self, left_ports, right_ports);
    }
  }
  
}

#[derive(PartialEq, Debug, Clone, Copy, Hash, Eq)]
enum GLA {
  Zero = 0,
  Erase = 1,
  Plus = 2,
  Copy = 3
}

impl Label for GLA {

  fn arity(&self) -> usize {
    match self {
      GLA::Zero => 0,
      GLA::Erase => 0,
      GLA::Plus => 2,
      GLA::Copy => 2,
    }
  }
  
  fn rewrite(inet: &mut InteractionNet<Self>, mut left: Vec<Porta<Self>>, mut right: Vec<Porta<Self>>) {
    let (main_left, main_right) = (left.remove(0), right.remove(0)); // should always have 0 element
    match (main_left.node.label, main_right.node.label) {
      (GLA::Zero, GLA::Erase) |
      (GLA::Erase, GLA::Zero) => {}
      (GLA::Zero,  GLA::Copy) |
      (GLA::Erase, GLA::Plus) => {
        let mut left1 = inet.add_node(main_left.node.label);
        let mut left2 = inet.add_node(main_left.node.label);
        inet.connect_ports(right.remove(0), left1.remove(0)); // connects right[1] and left1[0]
        inet.connect_ports(right.remove(0), left2.remove(0)); // connects right[2] and left2[0]
      }
      (GLA::Plus,  GLA::Copy)  => {
        let mut pls1 = inet.add_node(Self::Plus);
        let mut pls2 = inet.add_node(Self::Plus);
        let mut cpy1 = inet.add_node(Self::Copy);
        let mut cpy2 = inet.add_node(Self::Copy);

        inet.connect_ports(pls1.remove(0), right.remove(0));
        inet.connect_ports(pls2.remove(0), right.remove(0));
        inet.connect_ports(cpy1.remove(0),  left.remove(0));
        inet.connect_ports(cpy2.remove(0),  left.remove(0));

        inet.connect_ports(pls1.remove(0), cpy1.remove(0));
        inet.connect_ports(pls1.remove(0), cpy2.remove(0));
        inet.connect_ports(pls2.remove(0), cpy1.remove(0));
        inet.connect_ports(pls2.remove(0), cpy2.remove(0));
      }
      (GLA::Erase, GLA::Erase) => todo!(),
      (GLA::Erase, GLA::Copy)  => todo!(),
      (GLA::Plus,  GLA::Zero)  => todo!(),
      (GLA::Plus,  GLA::Erase) => todo!(),
      (GLA::Plus,  GLA::Plus)  => todo!(),
      (GLA::Copy,  GLA::Zero)  => todo!(),
      (GLA::Copy,  GLA::Erase) => todo!(),
      (GLA::Copy,  GLA::Plus)  => todo!(),
      (GLA::Copy,  GLA::Copy)  => todo!(),
      (GLA::Zero,  GLA::Plus)  => todo!(),     
      (GLA::Zero,  GLA::Zero)  => todo!(),
    }
  }
}

fn main() {
  let mut inet = InteractionNet::new();
  let mut zero = inet.add_node(GLA::Zero);
  let mut copy = inet.add_node(GLA::Copy);
  let mut era1 = inet.add_node(GLA::Erase);
  let mut era2 = inet.add_node(GLA::Erase);
  
  inet.connect_ports(zero.remove(0), copy.remove(0));
  inet.connect_ports(era1.remove(0), copy.remove(0));
  inet.connect_ports(era2.remove(0), copy.remove(0));
  
  
  
  assert!(zero.is_empty());
  assert!(copy.is_empty());
  assert!(era1.is_empty());
  assert!(era2.is_empty());
  
  inet.normalize();

  println!("{:#?} {:#?}", inet.arestas, inet.portas_ativas);
}
