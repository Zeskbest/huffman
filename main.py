import huffman


def main():
    data = b"ajhhsg238oidjwnfdwpnjnwcdijwcipdhbwdhidciwspdcsoacdsoducbkshodbhokbk\b,diuwer823iu4dsazfuwpc89249\n\00" * 9
    encoded = huffman.encode(data).dumps()
    data1 = huffman.decode(huffman.HEncoded.loads(encoded))
    assert len(encoded) < len(data), f"{len(encoded)} < {len(data)}"
    assert data == data1, f'{data} != {data1}'


if __name__ == '__main__':
    main()
