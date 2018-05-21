#!/usr/bin/env python
#coding:utf-8
# Author:  ao2
# Purpose: create Inkscape layers with svgwrite
# Created: 26.01.2018
# License: MIT License
# Copyright (C) 2018  Antonio Ospite <ao2@ao2.it>

import svgwrite
from svgwrite.data.types import SVGAttribute


class InkscapeDrawing(svgwrite.Drawing):
    """An svgwrite.Drawing subclass which supports Inkscape layers"""
    def __init__(self, *args, **kwargs):
        super(InkscapeDrawing, self).__init__(*args, **kwargs)

        inkscape_attributes = {
            'xmlns:inkscape': SVGAttribute('xmlns:inkscape',
                                           anim=False,
                                           types=[],
                                           const=frozenset(['http://www.inkscape.org/namespaces/inkscape'])),
            'inkscape:groupmode': SVGAttribute('inkscape:groupmode',
                                               anim=False,
                                               types=[],
                                               const=frozenset(['layer'])),
            'inkscape:label': SVGAttribute('inkscape:label',
                                           anim=False,
                                           types=frozenset(['string']),
                                           const=[])
        }

        self.validator.attributes.update(inkscape_attributes)

        elements = self.validator.elements

        svg_attributes = set(elements['svg'].valid_attributes)
        svg_attributes.add('xmlns:inkscape')
        elements['svg'].valid_attributes = frozenset(svg_attributes)

        g_attributes = set(elements['g'].valid_attributes)
        g_attributes.add('inkscape:groupmode')
        g_attributes.add('inkscape:label')
        elements['g'].valid_attributes = frozenset(g_attributes)

        self['xmlns:inkscape'] = 'http://www.inkscape.org/namespaces/inkscape'



    def layer(self, **kwargs):
        """Create an inkscape layer.

        An optional 'label' keyword argument can be passed to set a user
        friendly name for the layer."""
        label = kwargs.pop('label', None)

        new_layer = self.g(**kwargs)
        new_layer['inkscape:groupmode'] = 'layer'

        if label:
            new_layer['inkscape:label'] = label

        return new_layer


def main():
    svg = InkscapeDrawing('output.svg', profile='full', size=(640, 480))


    layer = svg.layer(label="Layer one")
    svg.add(layer)

    line = svg.line((100, 100), (300, 100),
                    stroke=svgwrite.rgb(10, 10, 16, '%'),
                    stroke_width='10')
    layer.add(line)

    text = svg.text('Test', insert=(100, 100), font_size='100', fill='red')
    layer.add(text)

    svg.save()


if __name__ == "__main__":
    main()
