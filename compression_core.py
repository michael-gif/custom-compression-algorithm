from collections import defaultdict


def obtain_tokens_and_offsets(raw_input: str) -> dict:
    def get_initial_tokens():
        """
        Uses a sliding window to obtain every possible token.

        Rather than appending to a list and returning said list, this method uses 'yield'.
        'yield' creates a generator object which results in the method completing slightly faster
        :return:
        """
        for i in range(3, 4):
            window_size = i
            for j in range(len(raw_input) - window_size):
                yield raw_input[j:j + window_size], j

    def group_tokens(tokens: list) -> dict:
        """
        Groups the tokens into a dictionary. The keys are the tokens, and the values are lists of offsets
        Example: {key: [1, 2, 3]}
        :param tokens:
        :return:
        """
        grouped = defaultdict(list)
        for token in tokens:
            grouped[token[0]].append(token[1])
        return grouped

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
            offset_count = len(v)
            if token_length == 3 and offset_count >= 5:
                filtered_tokens[k] = v
            elif token_length == 4 and offset_count >= 3:
                filtered_tokens[k] = v
            elif token_length >= 5 and offset_count >= 2:
                filtered_tokens[k] = v
        return filtered_tokens

    def flatten_tokens(tokens: dict) -> list:
        """
        Flattens the token dict into a list containing all of the tokens in the format (token, offset)
        :param tokens:
        :return:
        """
        flattened = []
        for token, offsets in tokens.items():
            flattened_token_list = [(token, off) for off in offsets]
            flattened += flattened_token_list
        return flattened

    def within_bounds(offset: int, offset_length: int, offset2: int, offset2_length: int) -> bool:
        if offset2 <= offset <= offset2 + offset2_length:
            return True
        if offset2 <= offset + offset_length <= offset2 + offset2_length:
            return True
        return False

    def remove_overlapping_tokens(tokens: list):
        """
        Efficiently checks if each token is overlapping the last. If so, discard the token and move to the next one.
        :param tokens:
        :return:
        """
        print('Removing redundant tokens: ', end='')
        number_of_tokens = len(tokens)
        interval = number_of_tokens // 41
        progress_bar = ['0', '.', '.', '.', '1', '.', '.', '.', '2', '.', '.', '.', '3', '.', '.', '.', '4', '.', '.',
                        '.',
                        '5', '.', '.', '.', '6', '.', '.', '.', '7', '.', '.', '.', '8', '.', '.', '.', '9', '.', '.',
                        '.',
                        '10']
        progress_bar_index = 0

        unique_tokens = []
        token_counter = 0
        for token in tokens:
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
        print('\r')
        return unique_tokens

    tokens = list(get_initial_tokens())
    print(f'Generated tokens: {len(tokens)} tkns')
    grouped_tokens = group_tokens(tokens)
    print(f'Grouped tokens')
    filtered_tokens = filter_tokens(grouped_tokens)
    print(f'Filtered tokens: {sum(len(offsets) for offsets in filtered_tokens.values())} tkns')

    flattened_tokens = flatten_tokens(filtered_tokens)
    print(f'Flattened tokens')
    sorted_tokens = sorted(flattened_tokens, key=lambda item: item[1])
    print(f'Sorted tokens')

    non_overlapped_tokens = remove_overlapping_tokens(sorted_tokens)
    print(f'Removed redundant tokens: {len(non_overlapped_tokens)} tkns')
    grouped_tokens = group_tokens(non_overlapped_tokens)
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
    So to differentiate between an ASCII character and a pointer, flip that first bit to a 1, by XOR'ing with 0x80
    This results in pointers being 2 bytes.

    The rest of the 15 bits are used for the token index, from 0-32768.
    So a file can have up to 32768 different tokens, which is plenty.
    :param token_key_index:
    :return:
    """
    pointer_bytes = token_key_index.to_bytes(2, 'little')
    marked_pointer_bytes = bytes([pointer_bytes[0] ^ 0x80, pointer_bytes[1]])
    return marked_pointer_bytes
