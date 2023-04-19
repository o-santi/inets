import qualified Data.Set as Set

data Label = Plus | Copy | Erase | Zero
type NodeId = Int
data Node  = Node { id :: NodeId, label :: Label }
data Porta = Porta { node :: Node, port :: Int }
data Aresta = Aresta { left :: Porta, right :: Porta }

data InteractionNet = INet { arestas :: List Aresta }

removeNode :: InteractionNet -> NodeId -> InteractionNet
removeNode (INet arestas) id = INet (filter arestas (\(Aresta (Porta (Node lid _)) (Porta (Node rid _))) -> lid != id && rid != 
 
norm :: List Aresta -> InteractionNet -> InteractionNet
norm [] inet = inet
norm ((Aresta (Porta left 0) (Porta right 0))::rest) inet =
  let new_actives, new_inet = rewrite inet left right in
    norm (new_actives ++ rest) new_inet

norm (_::rest) inet = norm rest inet

rewrite :: InteractionNet -> Node -> Node -> (List Arestas, InteractionNets)
rewrite inet (Node left_id Erase) (Node right_id erase) = remove
  
