# coding: utf_8
import io
from mp4tojson.main import mp4_to_boxes, adjust_boxes_length, boxes_to_mp4


def test_main():
    # https://www.sample-videos.com/
    with open('SampleVideo_360x240_1mb.mp4', 'rb') as f:
        src_bytes = f.read()

    src_stream = io.BytesIO(src_bytes)
    boxes = mp4_to_boxes(src_stream)
    adjust_boxes_length(boxes)
    dst_stream = io.BytesIO()
    boxes_to_mp4(boxes, dst_stream)
    assert src_bytes == dst_stream.getvalue()
