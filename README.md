# anki-kakijun

[![Rate on AnkiWeb](https://glutanimate.com/logos/ankiweb-rate.svg)](https://ankiweb.net/shared/info/1250448937)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Kanji stroke order add-on for Anki (beta version)

## Getting the add-on

- Go to Tools → Add-ons (Keyboard shortcut: Ctrl+Shift+A)
- Select Get Add-ons
- Insert the Add-on's code (1250448937)
- Click on OK

## Usage 

- Go to Tools > Manage Note Types (Keyboard shortcut: Ctrl+Shift+N)
- Select the note type you want to edit or create a new note type
- Click on Cards on the right side to edit the Note Type's Cards
- At the top of the window select the card type you want to edit
- Select the template you want to edit (for example: Front Template or Back Template)
- Add the **kakijun** filter to your card templates by changing 
```html
{{field-name}}
```
to
```html
{{kakijun:field-name}}
```
- Repeat for any other templates and card types of this note type, where you want to use anki-kakijun
- Click Save in the bottom right of the window

![Animated example](images/example.gif "Animated example")

## Configuration

## References

This project is based on those wonderful opensource projects :

+ [kanimaji](https://github.com/maurimo/kanimaji)
+ [KanjiVG](https://github.com/KanjiVG/kanjivg)

## Licensing

The source code of this add-on is released under the MIT License.

The SVG images located in the [kanjisvg folder](https://github.com/midse/anki-kakijun/blob/master/kanjisvg) are released under the <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>. 

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a>