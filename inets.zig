const std = @import("std");

const NodeId = usize;

const GLALabels = enum {
    plus,
    copy,
    erase,
    zero,

    const Self = @This();

    fn arity(self: Self) u8 {
        return switch (self) {
            .plus => 2,
            .copy => 2,
            .zero => 0,
            .erase => 0,
        };
    }

    const Inet = INet(Self);
    fn rewrite(inet: *Inet, left: Inet.Node, right: Inet.Node) void {
        const left_porta = Inet.Porta{ .node = left, .port = 0 };
        const right_porta = Inet.Porta{ .node = right, .port = 0 };
        var aresta_ativa = Inet.Aresta{ .left = &left_porta, .right = &right_porta };
        if (left.label == Self.zero and right.label == Self.erase) {
            _ = inet.arestas.remove(aresta_ativa);
        } else if (left.label == Self.zero and right.label == Self.copy) {
            _ = inet.arestas.remove(aresta_ativa);
            for (inet.node_ports.get(right.id).?) |*port| {
                port.* = &Inet.Porta{ .node = left, .port = 0 };
            }
        }
    }
};

fn INet(comptime labels: type) type {
    return struct {
        arestas: std.HashMap(Aresta, void, Self.ArestaContext, 80),
        arestas_talvez_ativas: std.ArrayList(Aresta),
        allocator: std.mem.Allocator,
        node_ports: std.AutoArrayHashMap(NodeId, []*Porta),

        const Self = @This();
        const Node = struct { id: NodeId, label: labels };
        const Porta = struct {
            node: Node,
            port: u8,
        };

        const Aresta = struct {
            left: *const Porta,
            right: *const Porta,

            fn is_active(self: Aresta) bool {
                return self.left.port == 0 and self.right.port == 0;
            }
        };

        const ArestaContext = struct {
            pub fn hash(_: ArestaContext, k: Aresta) u64 {
                return std.hash.Wyhash.hash(0, std.mem.asBytes(&k.left.node.id) ++
                    std.mem.asBytes(&k.right.node.id) ++
                    std.mem.asBytes(&k.left.port) ++
                    std.mem.asBytes(&k.right.port));
            }
            pub fn eql(_: ArestaContext, fst: Aresta, snd: Aresta) bool {
                return (fst.left.node.id == snd.left.node.id) and
                    (fst.right.node.id == snd.right.node.id) and
                    (fst.left.port == snd.left.port) and
                    (fst.right.port == snd.right.port);
            }
        };

        /// Create an empty interaction net
        fn init(allocator: std.mem.Allocator) Self {
            var arestas = std.HashMap(Aresta, void, ArestaContext, 80).init(allocator);
            var talvez_ativas = std.ArrayList(Aresta).init(allocator);
            var node_ports = std.AutoArrayHashMap(NodeId, []*Porta).init(allocator);
            return .{ .arestas = arestas, .arestas_talvez_ativas = talvez_ativas, .node_ports = node_ports, .allocator = allocator };
        }

        fn deinit(self: *Self) void {
            self.arestas.deinit();
            self.arestas_talvez_ativas.deinit();
            for (self.node_ports.values()) |ports| self.allocator.free(ports);
            self.node_ports.deinit();
        }

        fn add_node(self: *Self, label: labels) !Node {
            var new_id = self.node_ports.count();
            var node = Node{ .label = label, .id = new_id };
            var ports = try self.allocator.alloc(*Porta, labels.arity(label) + 1);
            try self.node_ports.put(node.id, ports);
            return node;
        }

        pub fn connect_ports(self: *Self, left: *Porta, right: *Porta) !void {
            var aresta = Aresta{ .left = left, .right = right };
            try self.arestas.put(aresta, {});
            try self.arestas_talvez_ativas.append(aresta);

            self.node_ports.get(left.node.id).?[left.port] = left;
            self.node_ports.get(right.node.id).?[right.port] = right;
        }

        fn normalize(self: *Self) void {
            while (self.arestas_talvez_ativas.items.len > 0) {
                const aresta = self.arestas_talvez_ativas.pop();
                if (aresta.is_active()) {
                    labels.rewrite(self, aresta.left.node, aresta.right.node);
                }
            }
        }

        fn print_arestas(self: *Self) void {
            std.debug.print("<---------->\n", .{});
            var iter = self.arestas.keyIterator();
            var aresta_opt = iter.next();
            while (aresta_opt) |aresta| {
                std.debug.print(" -- {}({}) @ {} <-> {}({}) @ {}\n", .{ aresta.left.node.label, aresta.left.node.id, aresta.left.port, aresta.right.node.label, aresta.right.node.id, aresta.right.port });
                aresta_opt = iter.next();
            }
        }
    };
}

test "zero erase cancel" {
    var inet = INet(GLALabels).init(std.testing.allocator);
    defer inet.deinit();
    var zer = try inet.add_node(GLALabels.zero);
    var era = try inet.add_node(GLALabels.erase);
    try inet.connect_ports(&.{ .node = zer, .port = 0 }, &.{ .node = era, .port = 0 });
    inet.normalize();
    try std.testing.expect(inet.arestas.count() == 0);
}

test "zero copy into 2 erases" {
    var inet = INet(GLALabels).init(std.testing.allocator);
    defer inet.deinit();
    var zer = try inet.add_node(GLALabels.zero);
    var copy = try inet.add_node(GLALabels.copy);
    var era1 = try inet.add_node(GLALabels.erase);
    var era2 = try inet.add_node(GLALabels.erase);
    try inet.connect_ports(&.{ .node = zer, .port = 0 }, &.{ .node = copy, .port = 0 });
    try inet.connect_ports(&.{ .node = copy, .port = 1 }, &.{ .node = era1, .port = 0 });
    try inet.connect_ports(&.{ .node = copy, .port = 2 }, &.{ .node = era2, .port = 0 });
    inet.print_arestas();
    inet.normalize();
    inet.print_arestas();
    try std.testing.expect(inet.arestas.count() == 0);
}
