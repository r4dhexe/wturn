#!/usr/bin/env python3
'''
WTURN
Description:    DEEPL asisted translator for wikipedia articles
                with original reference positioning, basic
                wiki formatting and glossary.
Version:        0.0.2
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
    parser = argparse.ArgumentParser(prog='wturn', description='Deepl assisted translation of English Wikipedia articles', epilog = 'Written by Ivana Kleban - iva.kleban@tuta.io',  formatter_class=argparse.HelpFormatter)
    parser.add_argument('-a', '--article', help='Article for conversion.') #default value for testing, remove later
    parser.add_argument('-l', '--lang', default=def_target_lang,  metavar='lang', help='Target language code as provided in .wturnrc configuration file. (default: CS - Czech)' )
    parser.add_argument('-u', '--usage', action='store_true', help='Check for usage data.' )
    parser.add_argument('-x', '--xref', action='store_true', help='Do not include references.' )
    parser.add_argument('-k', '--kat', action='store_true', help='Also translate categories.' )
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 0.0.2')
    
    return parser.parse_args()


def extract_article(source_article):
    '''
    Extract text and reference list from article, translate and combine.
    '''



    # extract text and reference position to be run through translator engine

    html_a = requests.get('https://en.wikipedia.org/wiki/'+source_article)
    article = (BeautifulSoup(html_a.text, 'html.parser').find('div',
        attrs={'class':'mw-parser-output'}).find_all(['p','ul','h1', 'h2','h3','h4','h5','h6']))

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
            case 'ul':
                lister = re.sub(r'^', '* ', item.get_text(), flags=re.M) # wiki format for strings in ul
                
                src_art += '\n '+lister+'\n'
            case 'h2':    
                src_art += ('='*2)+' '+item.get_text()+' '+('='*2)+'\n'
                if item.get_text() == 'References':
                    src_art += '\n<references />\n'
            case 'h3':
                src_art += ('='*3)+' '+item.get_text()+' ' +('='*3)+'\n'
            case 'h4':
                src_art += ('='*4)+' '+item.get_text()+' '+('='*4)+'\n'
            case 'h5':
                src_art += ('='*5)+' '+item.get_text()+' '+('='*5)+'\n'
            case 'h6':
                src_art += ('='*6)+' '+item.get_text()+' '+('='*6)+'\n'
            
    src_art = src_art.replace('[edit]', '')
    # list reference numbers
    nums = re.findall('\[[0-9]+\]', src_art)
    return src_art, nums, article, rev_id

def extract_with_ref(source_article):
    article_name = re.sub('_',' ', source_article) # used in translation_widget

    src_art, nums, article, rev_id = extract_article(source_article)
    ''' 
    Reference parser option.
    Either parse without references on -x/-xref
    Or first check reference vs. pointer list and 
    either abort or continue.
    '''
   
    if ref_switch == True:
        result = translate(src_art).__str__()
    else:
        ref_list = get_reference_html_list()
        if len(nums) != len(ref_list):
            print("Error: Reference list and reference pointers do not match!")
            continue_check = input('Continue without references? y/n:')
            if continue_check != 'y':
                print('Aborting now.')
                exit()
            else:
                result = translate(src_art).__str__()

        else:
            result = translate(src_art).__str__()
            
            i=0
            for ref in nums:
                reference = str(ref_list[i])
                result = result.replace(ref, reference)
                i = i+1
        
   
   
    '''
    Translates and prints article categories in wiki markup.
    Left as switch for now, to save on character usage.
    '''
    translation_widget = translate('Translation')
    result += '\n{'+translation_widget.text+'|en|'+article_name+'|'+rev_id+'}\n'
    result += '\n<references />\n'

    if kat_switch == True:
        categories = []
        article_categories = BeautifulSoup(html_a.text, 'html.parser').find('div', attrs={'class':'mw-normal-catlinks'}).find_all('a')
        for category in article_categories:
            categories.append(category.get_text())
        categories.remove(categories[0])
        categories_turned = translate(categories)
        for c in categories_turned:
            result += (f'[[{c.text}]]\n')           
    else:
        pass
               
    return result

def get_reference_html_list():
    '''
    Get reference list in html format(<ref></ref>) from wiki editor
    to be parsed and replace [d] mark in target tanslation.
    '''
    
    html = requests.get('https://en.wikipedia.org/w/index.php?title=' + source_article  + '&action=edit')
    
    origin = (BeautifulSoup(html.text, 'html.parser').find('textarea', attrs={'id':'wpTextbox1'}).prettify(formatter='html'))
    original = origin.replace('&lt;','<').replace('&gt;','>')
    ref_list = BeautifulSoup(original,'html.parser').find_all('ref')
    return ref_list
 

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

if __name__ == '__main__':
    auth_key, def_target_lang = read_config()  #read authorisation key and default language configuration from ~/.wturnrc
    args = args_parser()
    ref_switch, kat_switch = args.xref, args.kat

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

    translator=deepl.Translator(auth_key).set_app_info("wturn", "0.1")  #tconstruct ranslator

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
        source_article = args.article
        result =  extract_with_ref(source_article)
    
        print(result)
    exit()
