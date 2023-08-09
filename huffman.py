# src https://neerc.ifmo.ru/wiki/index.php?title=%D0%90%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC_%D0%A5%D0%B0%D1%84%D1%84%D0%BC%D0%B0%D0%BD%D0%B0#:~:text=Huffman's%20algorithm)%20%E2%80%94%20%D0%B0%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC%20%D0%BE%D0%BF%D1%82%D0%B8%D0%BC%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D0%B3%D0%BE%20%D0%BF%D1%80%D0%B5%D1%84%D0%B8%D0%BA%D1%81%D0%BD%D0%BE%D0%B3%D0%BE,PKZIP%202%2C%20LZH%20%D0%B8%20%D0%B4%D1%80.
from typing import NamedTuple, Union, Iterable
import bitarray


class HNode(NamedTuple):
    byte: int  # 0-255
    freq: int
    BYTES_LEN = 2

    def to_bytes(self) -> bytes:
        return self.byte.to_bytes(1, 'big') + self.freq.to_bytes(1, 'big')

    @classmethod
    def from_bytes(cls, bin: bytes) -> "HNode":
        assert len(bin) == cls.BYTES_LEN
        return cls(bin[0], int.from_bytes(bin[1:], 'big'))


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
        alphabet_: list[Union[HNode, HTree]] = alphabet.copy()
        while 1 < len(alphabet_):
            alphabet_.sort(key=lambda x: x.freq, reverse=True)  # popular first
            new_elem = HTree(alphabet_.pop(), alphabet_.pop())
            alphabet_.append(new_elem)

        tree: HTree = alphabet_.pop()
        return tree

    def get_encode_map(self) -> dict[int, bitarray.bitarray]:
        res = {}
        for prefix, node in (("0", self.left), ("1", self.right)):
            if isinstance(node, HNode):
                res[node.byte] = bitarray.bitarray(prefix)
            elif isinstance(node, HTree):
                for key, value in node.get_encode_map().items():
                    res[key] = bitarray.bitarray(prefix) + value
            else:
                raise RuntimeError(f"Got {type(node)}")
        return res

    def decode(self, data_len: int, arr: list[bool]) -> bytes:
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

                if data_len <= len(res):
                    break
        return bytes(res)


class HEncoded(NamedTuple):
    alphabet: list[HNode]
    data_len: int
    encoded_data: bytes

    def dumps(self):
        """
        Create simple archieve with the following structure:
        | position: | 0-3       | 4-7                    | 8-9         | 10-      |   -  |
        | meaning:  | signature | decoded message length | data offset | alphabet | data \
        | example:  | HUFF      | 238742883249           | 33          | bsakcjsd | ksdj |

        """
        alphabet = b''.join((node.to_bytes() for node in self.alphabet))
        alphabet_offset = 10
        data_offset = alphabet_offset + len(alphabet)
        return b''.join((
            b"HUFF",
            self.data_len.to_bytes(4, 'big'),
            data_offset.to_bytes(2, 'big'),
            alphabet,
            self.encoded_data
        ))

    @staticmethod
    def loads(bin: bytes):
        if bin[:4] != b"HUFF":
            raise ValueError("Wrong file type")
        data_len = int.from_bytes(bin[4:8], 'big')
        alphabet_offset = 10
        data_offset = int.from_bytes(bin[8:10], 'big')
        assert alphabet_offset < data_offset < len(bin)
        # alphabet_bin = bin[alphabet_offset:data_offset]

        assert (data_offset - alphabet_offset) % HNode.BYTES_LEN == 0
        alphabet = []
        for i in range((data_offset - alphabet_offset) // HNode.BYTES_LEN):
            node_bin = bin[alphabet_offset + i * HNode.BYTES_LEN:alphabet_offset + (i + 1) * HNode.BYTES_LEN]
            alphabet.append(HNode.from_bytes(node_bin))
        
        return HEncoded(alphabet, data_len, bin[data_offset:])


def encode(data: bytes) -> HEncoded:
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
    alphabet: list[HNode] = [HNode(key, freq) for key, freq in frequencies.items()]

    huffman_tree = HTree.from_alphabet(alphabet)
    map_ = huffman_tree.get_encode_map()

    res = bitarray.bitarray()
    for byte in data:
        res += map_[byte]
    return HEncoded(alphabet, len(data), res.tobytes())


def decode(hdata: HEncoded) -> bytes:
    huffman_tree = HTree.from_alphabet(hdata.alphabet)
    arr = bitarray.bitarray()
    arr.frombytes(hdata.encoded_data)
    res = huffman_tree.decode(hdata.data_len, arr.tolist())
    return res
