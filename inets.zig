const std = @import("std");

const NodeId = u32;

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

    inline fn porta(node: Inet.Node, port: u8) Inet.Porta {
        return Inet.Porta{ .node = node, .port = port };
    }

    fn rewrite(inet: *Inet, left: Inet.Node, right: Inet.Node) void {
        if (left.label == Self.zero and right.label == Self.erase) {
            inet.delete_node(left);
            inet.delete_node(right);
        }
    }
};

fn INet(comptime labels: type) type {
    return struct {
        arestas: std.HashMap(Porta, Porta, PortaContext(u64), 80),
        portas_talvez_ativas: std.ArrayHashMap(Porta, void, PortaContext(u32), true),

        const Self = @This();
        const Node = struct { id: NodeId, label: labels };
        const Porta = struct {
            node: Node,
            port: u8,
        };

        const EvalError = error{CannotRemoveNonExistantNode};

        fn PortaContext(comptime size: type) type {
            return struct {
                pub fn hash(_: PortaContext(size), k: Porta) size {
                    return @as(k.node.id, size) + @as(k.port, size); // every combination of id + port is unique
                }
                pub fn eql(_: PortaContext(size), fst: Porta, snd: Porta) bool {
                    return (fst.node.id == snd.node.id) and (fst.port == snd.port);
                }
            };
        }

        /// Create an empty interaction net
        fn init(allocator: std.mem.Allocator) Self {
            var arestas = std.HashMap(Porta, Porta, PortaContext(u64), 80).init(allocator);
            var portas_talvez_ativas = std.ArrayHashMap(Porta, void, PortaContext(u32), 80).init(allocator);
            return .{ .arestas = arestas, .portas_talvez_ativas = portas_talvez_ativas };
        }

        fn deinit(self: *Self) void {
            self.arestas.deinit();
            self.portas_talvez_ativas.deinit();
        }

        fn add_node(self: *Self, label: labels) !Node {
            var new_id = self.arestas.count();
            var node = Node{ .label = label, .id = new_id };
            return node;
        }

        fn delete_node(self: *Self, node: Node) EvalError!void {
            var i = 0;
            while (i < labels.arity(node.label)) : (i += 1) {
                const deleted = self.arestas.remove(Porta{ .node = node, .port = i });
                if (!deleted) {
                    return EvalError.CannotRemoveNonExistantNode;
                }
            }
        }

        pub fn connect_ports(self: *Self, left: Porta, right: Porta) !void {
            try self.arestas.put(left, right);
            try self.arestas.put(right, left);
            try self.portas_talvez_ativas.put(left, {});
            try self.portas_talvez_ativas.put(right, {});
        }

        fn normalize(self: *Self) void {
            while (self.arestas_talvez_ativas.iterator()) |keyvalue| {
                const left = keyvalue[0];
                const right = keyvalue[1];
                if (left.port == 0 and right.port == 0) {
                    labels.rewrite(self, left.node, right.node);
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
    try inet.connect_ports(.{ .node = zer, .port = 0 }, .{ .node = era, .port = 0 });
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
    try inet.connect_ports(.{ .node = zer, .port = 0 }, .{ .node = copy, .port = 0 });
    try inet.connect_ports(.{ .node = copy, .port = 1 }, .{ .node = era1, .port = 0 });
    try inet.connect_ports(.{ .node = copy, .port = 2 }, .{ .node = era2, .port = 0 });
    inet.print_arestas();
    inet.normalize();
    inet.print_arestas();
    try std.testing.expect(inet.arestas.count() == 0);
}
