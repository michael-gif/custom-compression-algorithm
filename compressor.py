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
    # index table with format {token: index} is very efficient compared to doing generated_tokens.index()
    index_table = {v: i for i, v in enumerate(generated_tokens)}
    input_text_bytes = input_text.encode()
    compressed_text = b''
    prev_index = 0
    for token in sorted_tokens:
        prev_text = input_text_bytes[prev_index: token[1]]
        token_key_index = index_table[token[0]]
        pointer = create_pointer(token_key_index)
        compressed_text += prev_text + pointer
        prev_index = token[1] + len(token[0])

    # separate each token with a null byte.  0x02 is used to identify the end of the metadata
    print('Generating metadata...')
    metadata = b'\x00'.join(token.encode() for token in generated_tokens) + b'\x02'

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
    #cProfile.run('compress()', sort='cumtime')
