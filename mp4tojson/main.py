# coding: utf_8
import io
import json
import logging
from pathlib import Path
import struct
import sys
import uuid
import click


@click.command()
@click.option('-d', '--debug', is_flag=True)
@click.argument('src', type=Path)
def main(debug, src):
    level = logging.DEBUG if debug else logging.WARNING
    logging.basicConfig(format='%(message)s', level=level)

    if src.suffix.lower() == '.mp4':
        with src.open('rb') as f:
            json.dump(mp4_to_boxes(f), sys.stdout)
    elif src.suffix.lower() == '.json':
        with src.open('r', encoding='utf_8') as f:
            boxes = json.load(f)
        adjust_boxes_length(boxes)
        boxes_to_mp4(boxes, sys.stdout.buffer)


def mp4_to_boxes(src):
    boxes = []
    try:
        while True:
            boxes.append(mp4_to_box(src))
    except EndOfFile:
        return boxes


def mp4_to_box(src):
    box = {}

    b = src.read(4)
    logging.debug('read length: %s', b)
    bl = len(b)
    if bl == 0:
        raise EndOfFile()
    elif bl < 4:
        raise ParseError('length', b)
    box['length'] = struct.unpack('>I', b)[0]
    if box['length'] < 8:
        raise ParseError('length', b)

    b = src.read(4)
    logging.debug('read type: %s', b)
    if len(b) != 4:
        raise ParseError('type', b)
    try:
        box['type'] = str(b, encoding='ascii')
    except UnicodeDecodeError as e:
        raise ParseError('type', b) from e

    if box['type'] == 'uuid':
        b = src.read(16)
        logging.debug('read uuid: %s', b)
        if len(b) != 16:
            raise ParseError('uuid', b)
        box['uuid'] = str(uuid.UUID(bytes=b))

        bl = box['length'] - 24
        b = src.read(bl)
        logging.debug('read data: %box bytes', len(b))
        if len(b) != bl:
            raise ParseError('data', b)
        try:
            box['str'] = bytes_to_str_lines(b)
        except UnicodeDecodeError:
            box['hex'] = bytes_to_hex_lines(b)
    else:
        bl = box['length'] - 8
        b = src.read(bl)
        logging.debug('read data: %d bytes', len(b))
        if len(b) != bl:
            raise ParseError('data', b)
        boxes = []
        try:
            _src = io.BytesIO(b)
            while True:
                boxes.append(mp4_to_box(_src))
        except ParseError:
            try:
                box['str'] = bytes_to_str_lines(b)
            except UnicodeDecodeError:
                box['hex'] = bytes_to_hex_lines(b)
        except EndOfFile:
            box['boxes'] = boxes
    return box


def boxes_to_mp4(boxes, dst):
    for box in boxes:
        box_to_mp4(box, dst)
    dst.flush()


def box_to_mp4(box, dst):
    dst.write(struct.pack('>I', box['length']))
    dst.write(bytes(box['type'], encoding='ascii'))
    if box['type'] == 'uuid':
        dst.write(uuid.UUID(box['uuid']).bytes)
    if 'str' in box:
        dst.write(str_lines_to_bytes(box['str']))
    elif 'hex' in box:
        dst.write(hex_lines_to_bytes(box['hex']))
    elif 'boxes' in box:
        for n in box['boxes']:
            box_to_mp4(n, dst)


def adjust_boxes_length(boxes):
    for box in boxes:
        adjust_box_length(box)


def adjust_box_length(box):
    tmp = 24 if (box['type'] == 'uuid') else 8
    if 'str' in box:
        tmp += len(str_lines_to_bytes(box['str']))
    elif 'hex' in box:
        tmp += len(hex_lines_to_bytes(box['hex']))
    elif 'boxes' in box:
        for n in box['boxes']:
            tmp += adjust_box_length(n)
    box['length'] = tmp
    return box['length']


def bytes_to_hex_lines(b):
    i = 0
    j = len(b)
    L = []
    while i < j:
        L.append(b[i:i + 16].hex())
        i += 16
    return L


def bytes_to_str_lines(b):
    return str(b, encoding='ascii').split('\n')


def hex_lines_to_bytes(hl):
    return bytes.fromhex(''.join(hl))


def str_lines_to_bytes(sl):
    return bytes('\n'.join(sl), encoding='ascii')


class EndOfFile(Exception):
    pass


class ParseError(Exception):
    pass


if __name__ == '__main__':
    main()
