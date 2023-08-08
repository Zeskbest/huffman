# src https://neerc.ifmo.ru/wiki/index.php?title=%D0%90%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC_%D0%A5%D0%B0%D1%84%D1%84%D0%BC%D0%B0%D0%BD%D0%B0#:~:text=Huffman's%20algorithm)%20%E2%80%94%20%D0%B0%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC%20%D0%BE%D0%BF%D1%82%D0%B8%D0%BC%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%B5%D1%84%D0%B8%D0%BA%D1%81%D0%BD%D0%BE%D0%B3%D0%BE,PKZIP%202%2C%20LZH%20%D0%B8%20%D0%B4%D1%80.
from typing import NamedTuple, Union, Iterable
import bitarray

class HNode(NamedTuple):
    byte: int  # 0-255
    freq: int

class HTree:
    def __init__(self, left: Union["HTree", HNode], right: Union["HTree", HNode]):
        self.left = left
        self.right = right

        self.freq = left.freq + right.freq

    @staticmethod
    def from_alphabet(alphabet: list[HNode]) -> "HTree":
        """
        Restore Huffman tree from the weighted alphabet.
        Args:
            alphabet: sorted list of byte-frequency pares
        """
        alphabet: list[Union[HNode,HTree]]
        while 1 < len(alphabet):
            alphabet.sort(key=lambda x: x.freq, reverse=True)  # popular first
            new_elem = HTree(alphabet.pop(), alphabet.pop())
            alphabet.append(new_elem)

        tree: HTree = alphabet.pop()
        return tree

    def get_encode_map(self) -> dict[int, bitarray.bitarray]:
        res = {}
        for prefix, node in (("0", self.left), ("1", self.right)):
            if isinstance(node, HNode):
                res[node.byte] = bitarray.bitarray(prefix)
            elif isinstance(node, HTree):
                for key, value in node.get_encode_map():
                    res[key] = bitarray.bitarray(prefix) + value
            else:
                raise RuntimeError(f"Got {type(node)}")
        return res

    def decode(self, arr: Iterable[bool]) -> bytes:
        res = []
        curr = self
        for b in arr:
            if b:
                curr = curr.right
            else:
                curr = curr.left
            if isinstance(curr, HNode):
                res.append(curr.byte)
                curr = self
        return bytes(res)


def encode(data: bytes) -> tuple[list[HNode], bytes]:
    """
    Prepare letter-to-bits dictionary.
    Args:
        data: input bytes

    Returns:
        alphabet
        encoded data
    """
    frequencies = {}
    for byte in data:
        frequencies[byte] = frequencies.get(byte, 0) + 1
    alphabet: list[HNode] = list(map(HNode, frequencies.items()))

    huffman_tree = HTree.from_alphabet(alphabet)
    map_ = huffman_tree.get_encode_map()

    res = bitarray.bitarray()
    for byte in data:
        res += map_[byte]
    return alphabet, res.tobytes()

def decode(alphabet: list[HNode], data: bytes) -> bytes:
    huffman_tree = HTree.from_alphabet(alphabet)
    arr = bitarray.bitarray()
    arr.frombytes(data)
    res = huffman_tree.decode(arr.tolist())
    return res
