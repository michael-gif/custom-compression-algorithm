def obtain_tokens_and_offsets(raw_input: str) -> dict:
    # generate all tokens and offsets
    tokens = []
    for i in range(3, 4):
        window_size = i
        for j in range(len(raw_input) - window_size):
            tokens.append((raw_input[j:j + window_size], j))
    print(f'Generated tokens: {len(tokens)} tkns')

    # group all the tokens into a dictionary
    grouped_tokens = {}
    for token in tokens:
        if token[0] not in grouped_tokens:
            grouped_tokens[token[0]] = [token[1]]
        else:
            grouped_tokens[token[0]].append(token[1])
    print(f'Grouped tokens')

    def filter_tokens(tokens_dict: dict) -> dict:
        """
        Token length | Number of offsets required for compression to be positive
        -------------|----------------------------------------------------------
        3            | 5
        4            | 3
        5+           | 2
        As the token length increases, the number of pointers needed in the final output decreases, until only 2 are
        required to have a net positive reduction in file size.
        :param tokens_dict:
        :return:
        """
        filtered_tokens = {}
        for k, v in tokens_dict.items():
            token_length = len(k)
            if token_length == 3 and len(v) >= 5:
                filtered_tokens[k] = v
            if token_length == 4 and len(v) >= 3:
                filtered_tokens[k] = v
            if token_length >= 5 and len(v) >= 2:
                filtered_tokens[k] = v
        return filtered_tokens

    # filter tokens
    filtered_tokens = filter_tokens(grouped_tokens)
    print(f'Filtered tokens: {sum(len(offsets) for offsets in filtered_tokens.values())} tkns')

    # flatten token dictionary into ordered list, ordered by offset
    flattened_tokens = []
    for token, offsets in filtered_tokens.items():
        flattened_token_list = [(token, off) for off in offsets]
        flattened_tokens += flattened_token_list
    sorted_tokens = sorted(flattened_tokens, key=lambda item: item[1])
    print(f'Flattened tokens')

    def within_bounds(offset: int, offset_length: int, offset2: int, offset2_length: int) -> bool:
        if offset2 <= offset <= offset2 + offset2_length:
            return True
        if offset2 <= offset + offset_length <= offset2 + offset2_length:
            return True
        return False

    # remove overlapping tokens
    print('Removing redundant tokens: ', end='')
    number_of_tokens = len(sorted_tokens)
    interval = number_of_tokens // 41
    progress_bar = ['0', '.', '.', '.', '1', '.', '.', '.', '2', '.', '.', '.', '3', '.', '.', '.', '4', '.', '.', '.',
                    '5', '.', '.', '.', '6', '.', '.', '.', '7', '.', '.', '.', '8', '.', '.', '.', '9', '.', '.', '.',
                    '10']
    progress_bar_index = 0

    unique_tokens = []
    token_counter = 0
    for token in sorted_tokens:
        if not unique_tokens:
            unique_tokens.append(token)
            continue
        last_token = unique_tokens[-1]
        unique_token_offset = last_token[1]
        token_offset = token[1]
        if not within_bounds(token_offset, len(token[0]), unique_token_offset, len(last_token[0])):
            unique_tokens.append(token)

        # increment progress bar if needed
        token_counter += 1
        if token_counter == interval:
            print(progress_bar[progress_bar_index], end='')
            progress_bar_index += 1
            token_counter = 0
    print(f'\nRemoved redundant tokens: {len(unique_tokens)} tkns')

    # The tokens are in an ordered list, so regroup them
    grouped_tokens = {}
    for token in unique_tokens:
        if token[0] not in grouped_tokens:
            grouped_tokens[token[0]] = [token[1]]
        else:
            grouped_tokens[token[0]].append(token[1])
    print(f'Regrouped tokens')

    # The redundancy check may have resulted in tokens having some of their offsets removed, so refilter the tokens
    filtered_tokens = filter_tokens(grouped_tokens)
    print(f'Refiltered tokens: {sum(len(offsets) for offsets in filtered_tokens.values())} tkns')

    return filtered_tokens


def create_pointer(token_key_index: int) -> bytes:
    """
    The pointer is 2 bytes, representing a number from 0-65536
    In order to identify a byte as the first half of a pointer, make the first bit always be 1:
    10000000 00000000
    ^ here
    ASCII characters are 7 bits, which allow for the encoding of all printable characters. So the first bit of an ASCII
    byte is always a 0. Example:
    'a' = 01100001
          ^ here
    So to differentiate between an ASCII character and a pointer, flip that first bit to a 1.
    This results in pointers being 2 bytes.

    The rest of the 15 bits are used for the token index, from 0-32768.
    So a file can have up to 32768 different tokens, which is plenty.
    :param token_key_index:
    :return:
    """
    pointer_bytes = token_key_index.to_bytes(2, 'little')
    bit_strings = [format(byte, '08b') for byte in pointer_bytes]  # convert bytes to bit strings
    first_bit_string = bit_strings[0]
    bit_strings[0] = '1' + first_bit_string[1:]  # flip the first bit to a 1
    marked_pointer_bytes = bytes([int(bit_strings[0], 2), int(bit_strings[1], 2)])  # convert bit strings back to bytes
    return marked_pointer_bytes
