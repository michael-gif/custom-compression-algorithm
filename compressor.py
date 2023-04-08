import sys
import time

from compression_core import *


def compress():
    with open(sys.argv[1]) as f:
        input_text = f.read()

    start = time.perf_counter()
    generated_tokens = obtain_tokens_and_offsets(input_text)

    # sort the tokens in ascending order according to their offsets
    tokens = []
    for token, offsets in generated_tokens.items():
        for off in offsets:
            tokens.append((token, off))
    sorted_tokens = sorted(tokens, key=lambda item: item[1])

    print('Adding pointers...')
    token_keys = list(generated_tokens.keys())
    compressed_text = b''
    prev_index = 0
    for i in range(len(sorted_tokens)):
        token = sorted_tokens[i]
        prev_text = input_text[prev_index: token[1]].encode()
        token_key_index = token_keys.index(token[0])
        pointer = create_pointer(token_key_index)
        compressed_text += prev_text + pointer
        prev_index = token[1] + len(token[0])

    # separate each token with a null byte.  0x02 is used to identify the end of the metadata
    print('Generating metadata...')
    metadata = b'\x00'.join(token.encode() for token in token_keys) + b'\x02'

    print('Writing to file...')
    with open('compressed.txt', 'wb') as f:
        f.write(metadata + compressed_text)

    finish = time.perf_counter()
    size_before = len(input_text)
    size_after = len(metadata + compressed_text)

    print(f'\nMetadata size: {len(metadata)} bytes')
    print(f'Compressed text size: {len(compressed_text)} bytes')
    print(f'Size before: {size_before} bytes')
    print(f'Size after: {size_after} bytes')
    print(f'Saving: {size_before - size_after} bytes')
    print(f'Compressed file by {round(100 - ((size_after / size_before) * 100), 3)}%')
    print(f'Time taken: {finish - start}s')


if __name__ == '__main__':
    compress()
