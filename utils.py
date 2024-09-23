import sys
import re
import traceback
import os
import datetime

VERBOSE = False

def print_verbose(*args):
    pargs = list(args)
    if len(pargs) > 1:
        pargs[0] = (str(pargs[0]) + ':').ljust(15)

    if VERBOSE:
        print(*pargs, file=sys.stderr, flush=True)

def print_error(*args):
    last_message = 'ERROR:'
    messages = [ last_message ]
    is_exception = False

    for arg in list(args):
        if isinstance(arg, Exception):
            is_exception = True
        if arg:
            message = str(arg).strip()
            if len(message) > 0:
                new_message_needs_space = len(messages) > 0 and not re.match(r'^[,;:]', message)
                if new_message_needs_space:
                    messages.append(' ')
                messages.append(message)
                last_message = message

    print(''.join(messages), file=sys.stderr, flush=True)
    if VERBOSE and is_exception:
        traceback.print_exc(file=sys.stderr)

def list_models(name, list_models_func, allows_caching, cache_directory_path):
    return list_items(name, 'models', list_models_func, allows_caching, cache_directory_path)

def list_voices(name, list_voices_func, allows_caching, cache_directory_path):
    return list_items(name, 'voices', list_voices_func, allows_caching, cache_directory_path)

def list_items(name, suffix, list_func, allows_caching, cache_directory_path):
    items = []
    file_path = None
    if allows_caching:
        file_path = os.path.join(cache_directory_path, f'{name}.{suffix}')
    if file_path and os.path.exists(file_path):
        mod_time = os.path.getmtime(file_path)
        mod_date = datetime.date.fromtimestamp(mod_time)
        if mod_date == datetime.date.today():
            with open(file_path, 'r') as f:
                items = f.read().splitlines()
    if len(items) == 0:
        items = list_func()
        if file_path:
            with open(file_path, 'w') as f:
                f.write('\n'.join(items))
    return items