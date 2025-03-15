# paprika server (ReNet)
This project aims to provide various services to older devices through XHTML in a way that makes them not throw up from the parser limit.
It includes things like weather, news, downloads and much more, including an (albeit insecure) account system!

### Why?
Because why not. As one wise man once said, "not everything in life has to have a purpose".
I simply wanted to make another project that compliments InterVillage (an earlier project of mine).
Since XHTML is essentially just stricter HTML, this allowed me to learn more about its history
and also give me another oppoturnity at learning Flask on a deeper level.

### How?
Simple; Python server using Flask provides XHTML pages rendered in Jinja2. That's pretty much all there is to it. Boring, I know..

## Installation procedure
This assumes you have at least Python 3.11 installed.

First, create a venv and install all packages:
```
python -m venv venv
pip install -r requirements.txt
```
Next, copy ```secret-example.py``` into ```secret.py``` and edit its contents
as you need.

Afterwards, simply run the program using ```python main.py``` or set up a WSGI server and you're good to go! If needed, you can change
the port on the last line in ```main.py```.

## Contributions & LICENSE
If you genuinely want to contribute, thank you! Feel free to submit a pull request.
This project is licensed under GPLv3.0. Details can be found in the LICENSE file.
Thanks for checking this absolutely awesome project out!

<sup>Sorry, I don't have time to make a more technical writeup right now.
If you know Python and (X)HTML, the code *should* be fairly easy to understand.
Also yes, this is mostly copied from the InterVillage README, who cares. They're similar so it doesn't matter.