# Copyright 2020 Dimitri Ségard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import uuid
from anki import hooks
from anki.template import TemplateRenderContext
from aqt import mw
from .static import css, js

config = mw.addonManager.getConfig(__name__)

try:
    drawing_speed = float(config["drawing_speed"])
except ValueError:
    drawing_speed = 0.5

try:
    time_between_strokes = int(config["time_between_strokes"])
except ValueError:
    time_between_strokes = 750


def small_uuid(length=8):
    return str(uuid.uuid4())[:length]


def is_kanji(v):
    v = ord(v)
    return (
        (v >= 0x4E00 and v <= 0x9FC3)
        or (v >= 0x3400 and v <= 0x4DBF)
        or (v >= 0xF900 and v <= 0xFAD9)
        or (v >= 0x2E80 and v <= 0x2EFF)
        or (v >= 0x20000 and v <= 0x2A6DF)
    )


def realord(s, pos=0):
    """
        Returns the unicode of a character in a unicode string, taking surrogate pairs into account
    """
    if s is None:
        return None
    code = ord(s[pos])
    if code >= 0xD800 and code < 0xDC00:
        if len(s) <= pos + 1:
            print("realord warning: missing surrogate character")
            return 0
        code2 = ord(s[pos + 1])
        if code2 >= 0xDC00 and code < 0xE000:
            code = 0x10000 + ((code - 0xD800) << 10) + (code2 - 0xDC00)
    return hex(code).replace("x", "")


def format_headers():
    headers = """
    <style>
    {css}
    </style>
    <script type="text/javascript">
    {js}
    </script>
    """
    return headers.format(css=css, js=js(drawing_speed, time_between_strokes))


def svg_insert(field_text):
    template = '<div id="tooltip-{svg_id}" class="tooltip">'
    template += "<span onmouseover=\"animate_strokes('{svg_id}');\">"
    template += "{kanji}"
    template += "</span>"
    template += '<div id="bottom-{svg_id}" class="bottom">'
    template += '<svg id="{svg_id}"></svg>'
    template += "</div></div>"

    output = ""
    load_svg = []
    for i, item in enumerate(field_text):
        if not is_kanji(item):
            output += item
            continue

        ret = realord(item)
        if ret == 0:
            output += item
            continue

        svg_id = f"svg{i}-{small_uuid()}"

        load_svg.append((svg_id, ret))
        output += template.format(svg_id=svg_id, kanji=item, kanji_id=ret)

    output += "<script>"
    output += "".join(
        [
            "loadSvg('{svg_id}', '{url}/{kanji_id}{svg_suffix}');".format(
                svg_id=c[0],
                kanji_id=c[1],
                url=config["url"],
                svg_suffix=config["svg_suffix"],
            )
            for c in load_svg
        ]
    )
    output += "</script>"

    return output


def on_card_render(output, context):
    headers = format_headers()
    output.question_text = headers + output.question_text
    output.answer_text = headers + output.answer_text


def on_field_filter(text, field, filter, context: TemplateRenderContext):
    if filter != config["filter_name"]:
        return text

    try:
        return svg_insert(context.fields()[field])
    except KeyError:
        return text


hooks.card_did_render.append(on_card_render)
hooks.field_filter.append(on_field_filter)
