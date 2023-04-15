import sys
import cProfile

from compression_core import ValveProgressBar


def extract_metadata(input_bytes: bytes) -> tuple:
    """
    Identifies the tokens and their frequencies by finding 0x02 bytes.
    Everything after the second 0x02 is the compressed file data
    :param input_bytes:
    :return:
    """
    metadata_end = input_bytes.index(b'\x02')
    token_metadata = input_bytes[:metadata_end]
    print('Extracted token metadata')
    remaining = input_bytes[metadata_end + 1:]

    temp = remaining.index(b'\x02')
    frequencies = remaining[:temp]
    print('Extracted frequency metadata')
    remaining = remaining[temp + 1:]

    return token_metadata, frequencies, remaining


def reconstruct_tokens(token_metadata: bytes, frequencies: bytes) -> list:
    """
    Separates the bytes into tokens using the lengths and counts provided by the frequency bytes.
    This could be considered 'uncompressing' the metadata about the tokens
    :param token_metadata:
    :param frequencies:
    :return:
    """
    total = 0
    tokens = []
    for i in range(0, len(frequencies), 3):
        lengths_byte, count_bytes = frequencies[i], frequencies[i + 1: i + 3]
        length_1 = (lengths_byte >> 4) & 15  # high half
        length_2 = lengths_byte & 15  # low half
        count_1 = int(count_bytes[0])
        count_2 = int(count_bytes[1])

        index = 0
        for j in range(count_1):
            tokens.append(token_metadata[total + index: total + index + length_1])
            index += length_1
        total += length_1 * count_1

        index = 0
        for j in range(count_2):
            tokens.append(token_metadata[total + index: total + index + length_2])
            index += length_2
        total += length_2 * count_2
    print('Reconstructed tokens')
    return tokens


def decompress_data(tokens: list, compressed_bytes: bytes) -> bytes:
    """
    Replaces each pointer with the token it's referencing. Also prints out a nice progress bar
    :param tokens:
    :param compressed_bytes:
    :return:
    """
    progress_bar = ValveProgressBar()
    progress_bar.set_steps(len(compressed_bytes))

    print('Uncompressing bytes: ', end='')
    decompressed = bytearray()
    i = 0
    content_length = len(compressed_bytes)
    while i < content_length:
        byte = compressed_bytes[i]
        progress_bar.increment()
        if byte & 128 == 128:
            pointer_bytes = compressed_bytes[i: i + 2]
            encoded_pointer = int.from_bytes(pointer_bytes, 'big')
            decoded_pointer = encoded_pointer ^ 0x8000
            t = tokens[decoded_pointer]
            decompressed += t
            i += 2
            progress_bar.increment()
            continue
        else:
            decompressed.append(byte)
            i += 1
    print('Uncompressed bytes')
    return decompressed


def uncompress():
    """
    Driver code for uncompressing a file.
    :return:
    """
    with open(sys.argv[1], 'rb') as f:
        compressed_bytes = f.read()

    token_metadata, frequencies, remaining = extract_metadata(compressed_bytes)
    tokens = reconstruct_tokens(token_metadata, frequencies)
    decompressed = decompress_data(tokens, remaining)

    print('Writing to file')
    with open('decompressed.txt', 'wb') as f:
        f.write(decompressed)


if __name__ == '__main__':
    uncompress()
    #cProfile.run('uncompress()', sort='cumtime')
