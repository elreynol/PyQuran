#!/usr/local/bin/python3
from sys import path
import os
# The current path of the current module.
path_current_module = os.path.dirname(os.path.abspath(__file__))
tools_modules = '../tools/'
tools_path = os.path.join(path_current_module, tools_modules)
core_modules = '../core/'
core_path = os.path.join(path_current_module,core_modules)
path.append(tools_path)
# Adding another searching path
path.append(core_path)

import pyquran
import quran
import arabic
import re
import inspect
import shutil
import sys


# {{autogenerated}}

'''NOTES
    1 * All files MUST have {{autogenerated}} flag.
    2 * foo(arg1:type) not supported yet; use foo(arg1)!
'''


PAGES = [
        {
       'page': 'quran_tools.md',
       'functions': [
          quran.get_sura,#
          quran.get_verse,#
          quran.get_sura_number,#
          quran.get_sura_name,#
       ]
       },

     {
      'page': 'arabic_tools.md',
      'functions': [
          pyquran.check_system, #
          pyquran.shape, #
          pyquran.factor_alef_mad, #
          pyquran.grouping_letter_diacritics,#
          arabic.alphabet_excluding,#
          arabic.strip_tashkeel,#
          pyquran.buckwalter_transliteration,#
         ]},

        {
       'page': 'analysis_tools.md',
       'functions': [
           pyquran.count_shape,
           pyquran.frequency_of_character,
           pyquran.generate_frequency_dictionary,
           pyquran.sort_dictionary_by_similarity,
           pyquran.check_sura_with_frequency,
           pyquran.search_sequence,
           pyquran.search_string_with_tashkeel,
          ]},


           
           
      
]


ROOT = 'https://github.com/TahaMagdy/PyQuran'
def get_earliest_class_that_defined_member(member, cls):
    ancestors = get_classes_ancestors([cls])
    result = None
    for ancestor in ancestors:
        if member in dir(ancestor):
            result = ancestor
    if not result:
        return cls
    return result


def get_classes_ancestors(classes):
    ancestors = []
    for cls in classes:
        ancestors += cls.__bases__
    filtered_ancestors = []
    for ancestor in ancestors:
        if ancestor.__name__ in ['object']:
            continue
        filtered_ancestors.append(ancestor)
    if filtered_ancestors:
        return filtered_ancestors + get_classes_ancestors(filtered_ancestors)
    else:
        return filtered_ancestors


def get_function_signature(function, method=True):
    signature = inspect.getargspec(function)
    defaults = signature.defaults
    if method:
        args = signature.args[1:]
    else:
        args = signature.args
    if defaults:
        kwargs = zip(args[-len(defaults):], defaults)
        args = args[:-len(defaults)]
    else:
        kwargs = []
    st = '%s.%s(' % (function.__module__, function.__name__)
    for a in args:
        st += str(a) + ', '
    for a, v in kwargs:
        if isinstance(v, str):
            v = '\'' + v + '\''
        st += str(a) + '=' + str(v) + ', '
    if kwargs or args:
        return st[:-2] + ')'
    else:
        return st + ')'


def get_class_signature(cls):
    try:
        class_signature = get_function_signature(cls.__init__)
        class_signature = class_signature.replace('__init__', cls.__name__)
    except:
        # in case the class inherits from object and does not
        # define __init__
        class_signature = cls.__module__ + '.' + cls.__name__ + '()'
    return class_signature


def class_to_docs_link(cls):
    module_name = cls.__module__
    assert module_name[:6] == 'keras.'
    module_name = module_name[6:]
    link = ROOT + module_name.replace('.', '/') + '#' + cls.__name__.lower()
    return link


def class_to_source_link(cls):
    module_name = cls.__module__
    assert module_name[:6] == 'core/pyquran.'
    path = module_name.replace('.', '/')
    path += '.py'
    line = inspect.getsourcelines(cls)[-1]
    link = 'https://github.com/TahaMagdy/PyQuran' + path + '#L' + str(line)
    return '[[source]](' + link + ')'


def code_snippet(snippet):
    result = '```python\n'
    result += snippet + '\n'
    result += '```\n'
    return result
    

def process_class_docstring(docstring):
    docstring = re.sub(r'\n    # (.*)\n',
                       r'\n    __\1__\n\n',
                       docstring)

    docstring = re.sub(r'    ([^\s\\]+):(.*)\n',
                       r'    - __\1__:\2\n',
                       docstring)

    docstring = docstring.replace('    ' * 5, '\t\t')
    docstring = docstring.replace('    ' * 3, '\t')
    docstring = docstring.replace('    ', '')
    return docstring


def process_function_docstring(docstring):
    docstring = re.sub(r'      # (.*)\n',
                       r'\n   __\1__\n\n',
                       docstring)
    docstring = re.sub(r'What it does\n',
                       r'__What it does__\n\n',
                       docstring)  
    docstring = re.sub(r'Args:\n',
                       r'\n__Args__\n\n',
                       docstring)  
    docstring = re.sub(r'Note:\n',
                       r'\n__Note__\n\n',
                       docstring)  
    docstring = re.sub(r'Returns:\n',
                       r'\n__Returns__\n\n',
                       docstring)
    docstring = re.sub(r'Assumption:\n',
                       r'\n__Assumption__\n\n',
                       docstring)
    docstring = re.sub(r'Cases:\n',
                       r'\n__Cases__\n\n',
                       docstring)
    docstring = re.sub(r'Issue:\n',
                       r'\n__Issue__\n\n',
                       docstring)
    docstring = re.sub(r'Example:\n',
                       r'\n__Example__\n\n',
                       docstring)

    docstring = re.sub(r'   ([^\s\\]+):(.*)\n',
                       r'\n    - __\1__:\2\n',
                       docstring)
    
  
   
    docstring = docstring.replace('    ' * 6, '\t\t')
    docstring = docstring.replace('    ' * 4, '\t')
    docstring = docstring.replace('    ', '')
    return docstring

print('Cleaning up existing sources directory.')
if os.path.exists('sources'):
    shutil.rmtree('sources')

print('Populating sources directory with templates.')
for subdir, dirs, fnames in os.walk('templates'):
    for fname in fnames:
        new_subdir = subdir.replace('templates', 'sources')
        if not os.path.exists(new_subdir):
            os.makedirs(new_subdir)
        if fname[-3:] == '.md':
            fpath = os.path.join(subdir, fname)
            new_fpath = fpath.replace('templates', 'sources')
            shutil.copy(fpath, new_fpath)

# Take care of index page.
#readme = open('README.md').read()
#index = open('index.md').read()
#index = index.replace('{{autogenerated}}', readme[readme.find('##'):])
#f = open('index.md', 'w')
#f.write(index)
#f.close()

print('Starting autogeneration.')
'''
for page_data in PAGES:
    blocks = []
    classes = page_data.get('classes', [])
    for module in page_data.get('all_module_classes', []):
        module_classes = []
        for name in dir(module):
            if name[0] == '_' or name in EXCLUDE:
                continue
            module_member = getattr(module, name)
            if inspect.isclass(module_member):
                cls = module_member
                if cls.__module__ == module.__name__:
                    if cls not in module_classes:
                        module_classes.append(cls)
        module_classes.sort(key=lambda x: id(x))
        classes += module_classes
    for cls in classes:
        subblocks = []
        signature = get_class_signature(cls)
        subblocks.append('<span style="float:right;">' + class_to_source_link(cls) + '</span>')
        subblocks.append('### ' + cls.__name__ + '\n')
        subblocks.append(code_snippet(signature))
        docstring = cls.__doc__
        if docstring:
            subblocks.append(process_class_docstring(docstring))
        blocks.append('\n'.join(subblocks))
'''
for page_data in PAGES:
    blocks = []
    functions = page_data.get('functions', [])
    for module in page_data.get('all_module_functions', []):
        module_functions = []
        for name in dir(module):
            if name[0] == '_' or name in EXCLUDE:
                continue
            module_member = getattr(module, name)
            if inspect.isfunction(module_member):
                function = module_member
                if module.__name__ in function.__module__:
                    if function not in module_functions:
                        module_functions.append(function)
        module_functions.sort(key=lambda x: id(x))
        functions += module_functions

    for function in functions:
        subblocks = []
        # TEST
        print(function)
        signature = get_function_signature(function, method=False)
        signature = signature.replace(function.__module__ + '.', '')
        subblocks.append('### ' + function.__name__ + '\n')
        subblocks.append(code_snippet(signature))
        docstring = function.__doc__
        if docstring:
            subblocks.append(process_function_docstring(docstring))
        blocks.append('\n\n'.join(subblocks))

    if not blocks:
        raise RuntimeError('Found no content for page ' +
                           page_data['page'])

    mkdown = '\n----\n\n'.join(blocks)
    # save module page.
    # Either insert content into existing page,
    # or create page otherwise
    page_name = page_data['page']
    path = os.path.join('docs/', page_name)
#    '''
    if os.path.exists(path):
        template = open(path).read()
        assert '{{autogenerated}}' in template, ('Template found for ' + path +
                                                 ' but missing {{autogenerated}} tag.')
        mkdown = template.replace('{{autogenerated}}', mkdown)
        print('...inserting autogenerated content into template:', path)
    else:
        print('...creating new page with autogenerated content:', path)
#    '''
    print('...creating new page with autogenerated content:', path)
    subdir = os.path.dirname(path)
    '''
    if not os.path.exists(subdir):
        os.makedirs(subdir)
    '''
    open(path, 'w').write(mkdown)
