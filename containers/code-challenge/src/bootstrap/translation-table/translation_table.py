#!/usr/bin/env python3

"""
    translates ABC to Alchemical Symbols
    https://en.wikipedia.org/wiki/Alchemical_symbol

    The first letter of the alchemical symbol equals it's letter in the albaphet
    We only support lower case!
"""

import click
import sys

# https://unicode.org/charts/PDF/U1F700.pdf
BASE_UNICODE_CHAR = 0x1F700
TRANSLATION_TABLE = dict(
    a = chr(BASE_UNICODE_CHAR + 0x01), # 🜁 Air
    b = chr(BASE_UNICODE_CHAR + 0x3E), # 🜾 Bismuth
    c = chr(BASE_UNICODE_CHAR + 0x13), # 🜓 Cinnabar
    d = chr(BASE_UNICODE_CHAR + 0x56), # 🝖 Digestion
    e = chr(BASE_UNICODE_CHAR + 0x03), # 🜃 Earth
    f = chr(BASE_UNICODE_CHAR + 0x02), # 🜂 Fire
    g = chr(BASE_UNICODE_CHAR + 0x1A), # 🜚 Gold
    h = chr(BASE_UNICODE_CHAR + 0x18), # 🜘 Halite
    i = chr(BASE_UNICODE_CHAR + 0x1C), # 🜜 Iron
    # j = chr(BASE_UNICODE_CHAR + N), no matching symbol
    # k = chr(BASE_UNICODE_CHAR + N), no matching symbol
    l = chr(BASE_UNICODE_CHAR + 0x2A), # 🜪 Lead
    m = chr(BASE_UNICODE_CHAR + 0x10), # 🜐 Mercury
    n = chr(BASE_UNICODE_CHAR + 0x15), # 🜕 Nitre
    o = chr(BASE_UNICODE_CHAR + 0x46), # 🝆 Oil
    p = chr(BASE_UNICODE_CHAR + 0x0E), # 🜎 Philosophers Stone
    q = chr(BASE_UNICODE_CHAR + 0x41), # 🝁 Quick Lime
    r = chr(BASE_UNICODE_CHAR + 0x3B), # 🜻 Realgar
    s = chr(BASE_UNICODE_CHAR + 0x0F), # 🜏 Sulfur
    t = chr(BASE_UNICODE_CHAR + 0x29), # 🜩 Tin
    u = chr(BASE_UNICODE_CHAR + 0x55), # 🝕 Urine
    v = chr(BASE_UNICODE_CHAR + 0x0A), # 🜊 Vingear
    w = chr(BASE_UNICODE_CHAR + 0x04), # 🜄 Water
    # x = chr(BASE_UNICODE_CHAR + N), no matching symbol
    # y = chr(BASE_UNICODE_CHAR + N), no matching symbol
    z = chr(BASE_UNICODE_CHAR + 0x4D), # 🝍 Zinc
)

def read_file(file: click.File) -> str:
    """ reads the file and returns the content as string """

    content = file.read()

    try:
        return content.decode('utf-8')
    except Exception as e:
        return content

def encode_data(data: str) -> str:
    """ encodes the data """
    output = ""
    for char in data.lower():
        if char in TRANSLATION_TABLE:
            output += TRANSLATION_TABLE[char]
        else:
            output += char
    return output

def decode_data(data: str) -> str:
    """ decodes the data """
    output = ""
    for char in data:
        if char in TRANSLATION_TABLE.values():
            output += list(TRANSLATION_TABLE.keys())[list(TRANSLATION_TABLE.values()).index(char)]
        else:
            output += char
    return output

@click.command()
@click.argument('input', type=click.File('rb'), default=sys.stdin)
@click.option('--decode', '-d', is_flag=True, help="decode the input file, if not set encode the input file")
def main(input: click.File, decode: bool):


    # read the input file
    input_data = read_file(input)
    output_data = ""

    if decode:
        output_data = decode_data(input_data)
    else:
        output_data = encode_data(input_data)

    # print the output
    print(output_data)

if __name__ == "__main__":
    main()
