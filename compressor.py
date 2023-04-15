import sys
import time
import cProfile

from compression_core import *


def compress():
    with open(sys.argv[1]) as f:
        input_text = f.read()

    start = time.perf_counter()
    generated_tokens = obtain_tokens_and_offsets(input_text)

    # flatten the tokens, sorting them in ascending order according to their offsets
    tokens = []
    for token, offsets in generated_tokens.items():
        flattened_token = [(token, off) for off in offsets]
        tokens += flattened_token
    sorted_tokens = sorted(tokens, key=lambda item: item[1])

    print('Adding pointers...')
    # sort the tokens according to their length, to make it easier to generate the metadata later
    sorted_keys = sorted(generated_tokens, key=lambda item: len(item))#, reverse=True)
    # index table with format {token: index} is very efficient compared to doing sorted_keys.index()
    index_table = {v: i for i, v in enumerate(sorted_keys)}

    input_text_bytes = input_text.encode()
    compressed_text = b''
    prev_index = 0
    for token in sorted_tokens:
        prev_text = input_text_bytes[prev_index: token[1]]
        token_key_index = index_table[token[0]]
        pointer = create_pointer(token_key_index)
        compressed_text += prev_text + pointer
        prev_index = token[1] + len(token[0])

    # join each token with no separators. 0x02 is used to identify the end of the tokens
    print('Generating metadata...')
    metadata = b''.join(token.encode() for token in sorted_keys) + b'\x02'

    # get the frequency of each token length
    frequencies = defaultdict(lambda: 0)
    for token in sorted_keys:
        frequencies[len(token)] += 1

    # flatten into list of tuples, each having max count of 256
    flattened_frequencies = []
    for key, count in frequencies.items():
        if count > 255:
            for i in range(count // 255):
                flattened_frequencies.append((key, 255))
            flattened_frequencies.append((key, count % 255))
        else:
            flattened_frequencies.append((key, count))
    # make sure the list is divisible by 2
    if len(flattened_frequencies) % 2 != 0:
        flattened_frequencies.append((0, 0))

    temp = b''
    # generate the rest of the metadata
    for i in range(0, len(flattened_frequencies), 2):
        key_1 = flattened_frequencies[i]
        key_2 = flattened_frequencies[i + 1]
        len_1, count_1 = key_1
        len_2, count_2 = key_2
        length_byte = ((len_1 << 4) + len_2).to_bytes(1, 'big')
        count_bytes = count_1.to_bytes(1, 'big') + count_2.to_bytes(1, 'big')
        temp += length_byte + count_bytes
    metadata += temp + b'\x02'

    print('Writing to file...')
    with open('compressed.txt', 'wb') as f:
        f.write(metadata + compressed_text)

    finish = time.perf_counter()
    size_before = len(input_text)
    size_after = len(metadata + compressed_text)

    results = 'RESULTS'
    print(f'\n{results:-^37}')
    print(f"{'Metadata size':<25} {len(metadata)} bytes")
    print(f"{'Compressed text size':<25} {len(compressed_text)} bytes")
    print(f"{'Size before':<25} {size_before} bytes")
    print(f"{'Size after':<25} {size_after} bytes")
    print(f"{'Saving':<25} {size_before - size_after} bytes")
    print(f"{'Compressed file by':<25} {round(100 - ((size_after / size_before) * 100), 3)}%")
    print(f"{'Time taken':<25} {finish - start}s")
    print(f"{results:-^37}")


if __name__ == '__main__':
    compress()
    #cProfile.run('compress()', sort='cumtime')
