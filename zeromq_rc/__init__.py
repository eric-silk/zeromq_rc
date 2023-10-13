import argparse
import logging
from typing import Any, Iterable
import time

import zmq

BASE_PORT = 10000
PUBLISH_DELAY_MS = 1000


class Publisher:
    def __init__(self, id: int) -> None:
        self.id = int(id)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{BASE_PORT}")

    def publish(self, x: float) -> None:
        print(f"Publishing '{self.id} {x}'...")
        self.socket.send_string(f"node{self.id} {x}")

    def __call__(self, x: float) -> None:
        return self.publish(x)


class Subscriber:
    def __init__(self, id: int) -> None:
        self.id = int(id)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.addr = f"tcp://192.168.0.{10+id}:{BASE_PORT}"
        self._connect()

    def _connect(self):
        print(f"Subscriber connecting to: {self.addr}")
        self.socket.connect(self.addr)
        self.socket.set_string(zmq.SUBSCRIBE, f"node{self.id}")

    def read(self) -> int:
        event = self.socket.poll(timeout=3 * PUBLISH_DELAY_MS)
        if 0 == event:
            print("No message received")
            self._connect()
            return -1000000
        else:
            msg = self.socket.recv_string()

        topic, data = msg.split()
        return int(data)

    def __call__(self) -> int:
        return self.read()


class Node:
    def __init__(
        self,
        id: int,
        initial_value: float,
        in_neighbors: Iterable[int],
        out_neighbors: Iterable[int],
    ) -> None:
        self.id = id
        self.x = initial_value
        self.in_neighbors = [int(i) for i in in_neighbors]
        self.out_neighbors = out_neighbors
        self.in_degree = len(self.in_neighbors)
        self.out_degree = len(self.out_neighbors)

        self.pub = Publisher(self.id)
        self.subs = [Subscriber(i) for i in self.in_neighbors]

    def pubsub(self) -> None:
        self.pub(self.x)
        remote_states = [sub() for sub in self.subs]
        print("Remote States:", remote_states)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="RC Demo", description="Runs an example RC demo"
    )
    parser.add_argument("--id", type=int, help="This node's ID", required=True)
    parser.add_argument("--out", nargs="*", help="Out Neighbor ID's", required=True)
    parser.add_argument(
        "--in", nargs="*", help="In Neighbor ID's", dest="in_", required=True
    )
    parser.add_argument("--x0", type=int, help="The initial value of x", required=True)

    args = parser.parse_args()
    logging.warning("ARGS WERE:")
    logging.warning(str(args))
    node = Node(args.id, args.x0, args.in_, args.out)
    time.sleep(1)
    while True:
        print("Pubsub and waiting...")
        node.pubsub()
        time.sleep(PUBLISH_DELAY_MS / 1000.0)
