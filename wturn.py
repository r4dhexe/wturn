#!/usr/bin/env python3
'''
WTURN
Description:    DEEPL asisted translator for wikipedia articles
                with original reference positioning, basic
                wiki formatting and glossary.
Version:        0.1
Author:         Ivy Kleban
Author email:   iva.kleban@tuta.io
'''

from bs4 import BeautifulSoup
import re
import deepl
import argparse
import requests
import yaml
import pathlib

def read_config():
    '''
    Retrieve configuration from .wturnrc file
    '''
    config_location = str(pathlib.Path.home())+'/.wturnrc'
    with open(config_location,'r') as config:
        if not config:
            auth_key = input('Your DeepL authorisation key:')
            print('''Available target languages: BG, CS, DA, DE, EL, EN-GB, EN-US,
            ES, ET, FI, FR, HU, ID, IT, JA, KO, LT, LV, NB, NL, PL, PT-BR,
            PT-PT, RO, RU, SK, SL, SV, TR, UK, ZH''')
            def_lang = input('Choose default target language please: ')
            setup_config_file = f'auth_key: {auth_key}\ndef_target_lang: {def_lang}'
            open(config_location,'w').write(setup_config_file)
            print('Creating config file now in  home directory and exiting.')
        else:
            config = yaml.safe_load(open(config_location))
            # print(f'Config OK. {config["auth_key"]} {config["def_target_lang"]}')
            return config['auth_key'], config['def_target_lang']

def args_parser():
    parser = argparse.ArgumentParser(prog='wturn', description='Deepl assisted translation of English Wikipedia articles', epilog = 'Written by Ivana Kleban - r4dhexe@tuta.io',  formatter_class=argparse.HelpFormatter)
    parser.add_argument('-a', '--article', help='Article for conversion.') #default value for testing, remove later
    parser.add_argument('-l', '--lang', default=def_target_lang,  metavar='lang', help='Target language code as provided in .wturnrc configuration file. (default: CS - Czech)' )
    parser.add_argument('-u', '--usage', action='store_true', help='Check for usage data.' )
    parser.add_argument('-k', '--kat', action='store_true', help='Also translate categories. (default: False)' )
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 0.1')
    
    return parser.parse_args()



def extract_with_ref(article):
    '''
    Extract text and reference list from article, translate and combine.
    '''
    article_name = re.sub('_',' ', article) # used in translation_widget 
    html = requests.get('https://en.wikipedia.org/w/index.php?title=' + article  + '&action=edit')
    
    origin = (BeautifulSoup(html.text, 'html.parser').find('textarea', attrs={'id':
    'wpTextbox1'}).prettify(formatter='html'))
    original = origin.replace('&lt;','<').replace('&gt;','>')
    ref_list = BeautifulSoup(original,'html.parser').find_all('ref')
    

    # extract text and reference position to be run through translator engine

    html_a = requests.get('https://en.wikipedia.org/wiki/'+article)
    

    article = (BeautifulSoup(html_a.text, 'html.parser').find('div', attrs={'class':'mw-parser-output'}).find_all(['p','h1', 'h2','h3','h4','h5','h6']))

    # retrieve revision id then destroy helper
    rev_id_helper = BeautifulSoup(html_a.text, 'html.parser').prettify()
    rev_id = re.search(r'\d{10}', re.search(r'id (\d{10})\.', rev_id_helper)[0])[0] 
    del(rev_id_helper)

    # construct article from bs4 tag list
    src_art = ''
    for item in article:
        match item.name:
            case 'p':
                src_art += '\n'+item.get_text()+'\n'
            case 'h2':    
                src_art += ('='*2)+' '+item.get_text()+' '+('='*2)
            case 'h3':
                src_art += ('='*3)+' '+item.get_text()+' ' +('='*3)
            case 'h4':
                src_art += ('='*4)+' '+item.get_text()+' '+('='*4)
            case 'h5':
                src_art += ('='*5)+' '+item.get_text()+' '+('='*5)
            case 'h6':
                src_art += ('='*6)+' '+item.get_text()+' '+('='*6)
            
    src_art = src_art.replace('[edit]', '')
    # list reference numbers
    nums = re.findall('\[[0-9]+\]', src_art)

    result = translate(src_art).__str__()
    
    def get_translated_categories():
        '''
        Translates and prints article categories in wiki markup.
        Left as switch for now, to save on character usage.
        '''

        if args.kat == True:
            categories = []
            article_categories = BeautifulSoup(html_a.text, 'html.parser').find('div', attrs={'class':'mw-normal-catlinks'}).find_all('a')
            for category in article_categories:
                categories.append(category.get_text())

            categories_turned = translate(categories.remove(categories[0]))
            for c in categories_turned:
                result += (f'[[{c.text}]]\n')

            return result    
        else:
            pass
    ''' replace reference numbers with references in wiki notation'''
    i=0
    for ref in nums:
        reference = str(ref_list[i])
        result = result.replace(ref, reference)
        i = i+1
    
    #result_formatted = re.sub(r'\n\n\d(.*\b)\n',r'\n\n== \1 ==\n', result)
    translation_widget = translate('Translation')
    result += '\n{'+translation_widget.text+'|en|'+article_name+'|'+rev_id+'}\n'
    result += '\n<references />\n'
    get_translated_categories()
    return result

def translate(text):
    translator=deepl.Translator(auth_key)
    result = translator.translate_text(text,target_lang=target_lang)

    return result
    
def check_article_existence(article):
    article = article.replace(' ','_')
    ref =  requests.get('https://en.wikipedia.org/wiki/'+article)
    if not ref.status_code == 200:
        print('Required article does not exist or misspelled.')
    else:
        '''Check whether article exists and return character count to be sent to
        translation engine.'''

       # print('Article OK')
        count = BeautifulSoup(ref.text,'html.parser').find('div', attrs={'class':'mw-parser-output'}).get_text()
        #print(f'Article lenght: {len(count)} chars.')
        return ref.text, len(count)

def check_deepl_quota():
    usage = translator.get_usage()
    if check_target_languages().__contains__(target_lang):
        pass
    else:
        print('Error: Specified target language not supported by DEEPL API.')
        exit()

    if usage.any_limit_reached:
        print('Translation limit reached.')
        
    if usage.character.valid:
        if (usage.character.limit-usage.character.count) > char_count:
            pass
        else:
            print('Warning : Character limit for billing period reached.')
            exit()

def check_target_languages():
    '''
    Check availability of target language. 
    NOTE: This is left as standalone func so it can be reused elsewhere
    than just in check_deepl_quota()
    '''
    ll = []
    for langs in translator.get_target_languages():
        ll.append(langs.code)
    return ll    

auth_key, def_target_lang = read_config()  #read authorisation key and default language configuration from ~/.wturnrc
args = args_parser()

'''
Checks whether user provided target language, or should default to config.
'''
if not args.lang:
    if  check_target_lang.__contains__(def_target_lang):
        target_lang = def_target_lang
    else:
        print('Error: Default language setting not compatible with DEEPL API')
        exit()
else:
    target_lang = args.lang

translator=deepl.Translator(auth_key) #tconstruct ranslator

if args.usage == True:
    usage = translator.get_usage()
    count_left = usage.character.limit-usage.character.count
    print(f'''Character usage:  {usage.character.count}  of {usage.character.limit}. Characters left: {count_left}. ''')
    if not args.article:
        exit()

if not args.article:
    print ('No article for conversion provided. Aborting.')
    exit()
else:
    source_article, char_count = check_article_existence(args.article) #check if article exists and count chars
    check_deepl_quota()
    print(extract_with_ref(args.article))
    exit()

