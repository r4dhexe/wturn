# wturn
Wturn is a CLI utility to automate translation of english wikipedia articles using DEEPL translation service. Written in Python, tested on GNU/Linux. 

## Installation

**These instructions are pertinent to Bash shell commands.**

Clone this repository to destination folder of preference.

```bash
mkdir <destination folder>
cd <destination folder>
git clone https:////github.com/r4dhexe/wturn
cd wturn
chmod +x wturn.py
```

You can alias this utility in your .bashrc to make it available user-space wide.
Just echo or manually append this line to at the end of your .bashrc:
```bash
alias wturn = '/home/<your_user_name>/<install_location>/wturn.py'

# reload shell config
source ~/.bashrc
```
*Note: If you run this utility in python virtual environment, the alias will only work there.*

### Python module dependencies
Make sure you have these modules instaled:
- beautifulsoup4 # for scraping html tree
- deepl # actual translation CLI interface
- requests # http library
- yaml  # yaml parser for config file
- pathlib 
- argaprse

To install a python module run:

```bash
$ pip install <ModuleName>
```

## Usage

```
usage: wturn [-h] [-a ARTICLE] [-l lang] [-u] [-k]

Deepl assisted translation of English Wikipedia articles

options:
  -h, --help            show this help message and exit
  -a ARTICLE, --article ARTICLE
                        Article for conversion.
  -l lang, --lang lang  Target language code as provided in .wturnrc configuration file. (default: CS - Czech)
  -u, --usage           Check for usage data.
  -k, --kat             Also translate categories. (default: False)

```

---

This tool requires you to be registered with at least DEEPL Free plan.
To facilitate this, wturn somes with .wturnrc file found in your home folder. 
Wturn creates this config file interactively during first run.

```yaml
auth_key: #your DEEPL authorization key
def_lang: #prefered default target language
```

Let's say we want to translate an article called 'Example Article' with
https://en.wikipedia.org/wiki/Example_Article address and into default target language provided in .wturnrc:

```bash
$ wturn -a Example_Article

# result
Translated text with apropriate reference<ref /> positioning and basic wiki markup.

== References ==
<references />
```
To get article without references use **-x** switch:
```bash
$ wturn -a Example_Article -x

# result
Translated text with apropriate reference positioning and basic wiki markup.
```
**Note: Even -x/--xref option still appends the *== References ==* headline and *<references />* tag.**

As source and target wiki do not allways share same category structure, nor
are some categories relatable, the article is, per default, translated without category list
to save on character quota.
This behaviour can be altered by boolean **-k** switch:

```bash
$ wturn -a Example_Article -k

#result
Translated text with apropriate reference<ref /> positioning and basic wiki markup.

== References ==
<references />

[[Categories]]
```
The **-l** option let's us choose target language. Value is checked against list of Deepl supported target languages.

```bash
$ wturn -a Example_Article -l CS

#result 
Přeložený text s referencemi<ref /> a základní wiki značení.

== Reference ==
<references />
```
Currently supported languages:

BG, CS, DA, DE, EL, EN-GB, EN-US, ES, ET, FI, FR, HU, ID, IT, JA, KO, LT, LV, NB, NL, PL, PT-BR, PT-PT, RO, RU, SK, SL, SV, TR, UK, ZH

For very basic usage check use boolean **-u** switch:

```bash
$ wturn -u

#result
Character usage:  25671  of 500000. Characters left: 474329. 
```
---
Note: run this utility in for loop on predefinded list of articles and output to files
```bash
# exapmle list
$ cat example_list
Example One
Example Two
Example Three
$ mapfile -t list < example_list
$ for item in ${list[@]}; do wturn -a $i >> $i.wiki; done
```
---

## Dictionary
Wturn comes with **very** basic dictionary module. Dictionary source file can be specified in
config file. For now it's just kept in the main folder, but might migrate to dict/ later.
Dictionary formatting is basic yaml, parsed with yaml python module. 

```yaml
# example dictionary
Hello: Ahoj
world: světe
```
**Note: Does not convert case automaticaly.**

## Logic flow

```
read configuration from ~/.wturnrc / creates one on first run 
on article url 200 status proceed / if not 200: exit()
check character count against deepl quota / exit() on exceeding quota (FREE tier)
check target language against deepl target languages list 
construct source text, add wiki markdown to h* elements -> translate
  optional translate and append category list
run text throught user maintained dictionary
output to <stdout>
exit()
```

## Support

Hit me up at iva.kleban at tuta.io

## TODO
- test a lot and improve
- add verbose flow
- Firefox add-on, so port to JS

## License
[MIT](https://choosealicense.com/licenses/mit/)
