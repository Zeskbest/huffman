import huffman


def main():
    data = b"ajhhsg238oidjwnfdwpnjuidnwcdijwcipdhbwdhidciwspdcsoacdsoducbkshodbhokbk\b,diuwer823iqu4dsazfuwpc89249\n\00"
    alphabet, encoded = huffman.encode(data)
    data1 = huffman.decode(alphabet, encoded)
    assert len(encoded) < len(data)
    assert data == data1


if __name__ == '__main__':
    main()
