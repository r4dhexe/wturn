'''
Simple dictionary module.
There's nothing really here now, but the idea is to keep
possibly future complexity as a module rather than 
mashup with other code.
'''
import yaml

def translate(text, conversion_dict):
    dictionary = yaml.safe_load(open(conversion_dict))
    
    if not text: return text
    for key, value in dictionary.items():
        text = text.replace(key, value)
     
    return text    
