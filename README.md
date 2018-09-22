mp4tojson
====

Convert mp4 to json. Reverse conversion is also supported.

## Requirement

* Python >= 3.6
* click

## Install

```
pip install git+https://github.com/shinoaki-tatsuya/mp4tojson.git
```

## Usage

* mp4 to json

```
mp4tojson SampleVideo_360x240_1mb.mp4 > SampleVideo_360x240_1mb.json
```

* json to mp4

```
mp4tojson SampleVideo_360x240_1mb.json > SampleVideo_360x240_1mb.mp4
```

## Limitations

* Largesize box does not supported.

## Licence

[MIT](https://github.com/shinoaki-tatsuya/mp4tojson/blob/master/LICENSE)
