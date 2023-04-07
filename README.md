# Tokenized Frequency Compression Algorithm

### Identify all possible tokens, including their offsets from 0, excluding tokens of length 1 and 2, because they are not compressable
In this example, I will allow tokens with only two offsets, because it is easier to explain. But in practice, tokens with two offsets are filtered out.
`"the theatre"`

| `tokens`       | `respective offsets`  |
|--------------- | ---------- |
| `th`, `he`, `e `, ` t`, `th`, `he`, `ea`, `at`, `tr`, `re`     | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 |
| `the`, `he `, `e t`, ` th`, `the`, `hea`, `eat`, `atr`, `tre`  | 0, 1, 2, 3, 4, 5, 6, 7, 8    |
| `the `, `he t`, `e th`, ` the`, `thea`, `heat`, `eatr`, `atre` | 0, 1, 2, 3, 4, 5, 6, 7       |
| `the t`, `he th`, `e the`, ` thea`, `theat`, `heatr`, `eatre`  | 0, 1, 2, 3, 4, 5, 6          |

### Group the tokens and their offsets
| `tokens`       | `offsets`  |
|--------------- | ---------- |
| `th`, `he`, `e `, ` t`, `ea`, `at`, `tr`, `re`                 | [0, 4], [1, 5], [2], [3], [6], [7], [8], [9] |
| `the`, `he `, `e t`, ` th`, `hea`, `eat`, `atr`, `tre`         | [0, 4], [1], [2], [3], [5], [6], [7], [8] |
| `the `, `he t`, `e th`, ` the`, `thea`, `heat`, `eatr`, `atre` | [0], [1], [2], [3], [4], [5], [6], [7] |
| `the t`, `he th`, `e the`, ` thea`, `theat`, `heatr`, `eatre`  | [0], [1], [2], [3], [4], [5], [6] |

### Sort the tokens by descending order according to the number of offsets and filter out tokens with two offsets
| `tokens`       | `offsets`  |
|--------------- | ---------- |
|`th`            | [0, 4]     | 
|`he`            | [1, 5]     |
|`the`           | [0, 4]     |

### Adjust the offsets to be the differences between each offset rather than the actual offset.
If an offset is more than 255 away from the previous offset, exclude it.  
By replacing offsets with differences, the numbers are made much smaller, allowing for them to fit within a byte.

| `tokens`       | `offsets`  |
|--------------- | ---------- |
|`th`            | [0, 4]     | 
|`he`            | [1, 4]     |
|`the`           | [0, 4]     |

Filter out tokens with only two offsets.  

### Remove overlapping tokens.
| `tokens`       | `offsets`  |
|--------------- | ---------- |
|`th`            | [0, 4]     |
Above you can see only 2 tokens remain. Both tokens are `th` tokens.  
So `the theatre` becomes `(th)e (th)eatre`

Again, filter out tokens with only two offsets.

### Remove all tokens from the input text.  
`the theatre` becomes `e eatre` because `th` was removed.  

### Generate the metadata for the tokens.
The offsets are stored next to each other, with no spaces:  
`th 0x00 0x04 0x00`.  
Note that a `0x00` has been concatenated on the end, this is to identify the end of a token.  
In hex:  
`74 68 00 04 00`

If there was another token `in, [2, 7, 9]`, then the bytes would look like this:  
`th 0x00 0x04 0x00 in 0x02 0x07 0x09 0x00`  
And in hex:  
`74 68 00 04 00 69 6E 02 07 09 00`

### Finally, concatenate the compressed input text `e eatre`:  
`th 0x00 0x04 0x00 e eatre`.  
In hex:  
`74 68 00 04 00 65 20 65 61 74 72 65`

### Write that hex to the compressed file
The original bytes:  
`74 68 65 20 74 68 65 61 74 72 65`  
The new bytes:
`74 68 00 04 00 65 20 65 61 74 72 65`

In this example, the file size grew by one byte, because barely anything could be compressed. In a larger file however, there would be a reduction in the number of bytes.  
The bee movie script got compressed from `49473 bytes (49.5 KB)` to `48045 bytes (48 KB)`.  
A saving of `1428 bytes (1.5 KB)`!!!