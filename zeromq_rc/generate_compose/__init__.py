from typing import Dict, Iterable
import networkx
import yaml

ADJACENCY_DICT = {
    0: [1, 2, 3, 4],
    1: [0],
    2: [0],
    3: [0],
    4: [5],
    5: [0],
}

NETWORK_DICT = {
    "rc_network": {
        "driver": "bridge",
        "ipam": {"config": [{"subnet": "192.168.0.0/24"}]},
    }
}


class Node:
    def __init__(
        self,
        id: int,
        digraph: networkx.DiGraph,
        y0: float,
        z0: float,
        base_ip: str = "192.168.0.10",
        port: int = 10000,
        image="rc_demo",
        base_name="rc_node",
    ) -> None:
        self.id = id
        self.graph = digraph
        self.y0 = y0
        self.z0 = z0

        ip_chunks = [int(i) for i in base_ip.split(".")]
        ip_chunks[-1] += id
        self.ip = ".".join([str(i) for i in ip_chunks])
        self.port = port
        self.image = image
        self.name = f"{base_name}_{id}"

    def to_dict(self) -> Dict[str, str]:
        predecessors = [str(i) for i in self.graph.predecessors(self.id)]
        successors = [str(i) for i in self.graph.successors(self.id)]
        command = (
            f"--id {self.id} --out {' '.join(successors)} "
            f"--in {' '.join(predecessors)} --x0 {self.y0}"
        )
        return {
            "image": self.image,
            "container_name": self.name,
            "command": command,
            "networks": {"rc_network": {"ipv4_address": self.ip}},
        }


def main():
    G = networkx.DiGraph(ADJACENCY_DICT)
    assert networkx.is_strongly_connected(G)
    y0_list = [*range(len(ADJACENCY_DICT))]
    z0_list = [i + 1 for i in range(len(ADJACENCY_DICT))]
    node_list = [
        Node(key, G, y0, z0) for key, y0, z0 in zip(ADJACENCY_DICT, y0_list, z0_list)
    ]

    service_dict = {}
    for node in node_list:
        service_dict[f"node{node.id}"] = node.to_dict()

    output = {"version": "2", "services": service_dict, "networks": NETWORK_DICT}
    with open("compose.yaml", "w") as outfile:
        yaml.dump(output, outfile)
