from datetime import datetime
from pathlib import Path
import re
from yaml import safe_load, Loader

from dateutil.relativedelta import relativedelta
from cerberus import Validator

from . import actions
from . import filters as filt
from .helpers import is_valid_path

cwd = Path(__file__).parent
print(cwd)

class SchemaValidator(Validator):
    def _check_with_path(self, field, value):
        if not is_valid_path(value):
            self._error(field, "Path to directory is not valid.")
        elif Path(value).is_file():
            self._error(field, "Folder must be a directory, not a file.")

schema_filt = Validator(safe_load((cwd / Path('schemas/filt_main.yaml')).open()))
schema_rule = SchemaValidator(safe_load((cwd / Path('schemas/schema_rule.yaml')).open()))#schema_rule._check_with_path = lambda a, b: check_path(a, b, schema_rule._error) # Must add the function to schema explicity, see https://docs.python-cerberus.org/en/stable/customize.html#check-with-rule-methods

# -- Coercions -- #

def to_delta(s):
    pttn = re.compile(r'(?:(\d+)yr)?\s*(?:(\d+)mo)?\s*(?:(\d+)dy)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:(\d+)s)?')
    match = pttn.fullmatch(s.lower())
    keys = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
    kwargs = dict()
    for i in range(6):
        if match[i+1]:
            kwargs[keys[i]] = int(match[i+1])
    return relativedelta(**kwargs)

def to_bytes(s):
    pttn = re.compile(r'(\d+)(b|kb|mb|gb|tb)')
    match = pttn.fullmatch(s.lower())
    mag, unit = match.groups()
    mag = int(mag) * 1024 ** {'b': 0, 'kb': 1, 'mb': 2, 'gb': 3, 'tb': 4}.get(unit)
    return mag

def to_datetime(s):
    pttn = re.compile(r'(\d{4})-(\d{1,2})-(\d{1,2})(?:T(\d{1,2}):(\d{1,2}):(\d{1,2}))?')
    match = pttn.fullmatch(s)
    keys = ['year', 'month', 'day', 'hour', 'minute', 'second']
    kwargs = dict()
    for i in range(6):
        if match[i+1]:
            kwargs[keys[i]] = int(match[i+1])
    return datetime(**kwargs)

# -- Filter and Rule extraction -- #

def get_filter(conf):
    # Conf should be a dictionary as returned by yaml
    success = schema_filt.validate(conf)
    print(success)
    if not success:
        print(schema_filt._errors)
        # TODO: Write a parser that displays tese errors in a useful way
        return filt._false_filter()
    return gen_filter(conf)

def get_rule(conf):
    # Conf should be a dictionary as returned by yaml
    success = schema_rule.validate(conf)
    conf = schema_rule.normalized(conf)
    print(success)
    if not success:
        print(schema_rule._errors)
        # TODO: Write a parser that displays tese errors in a useful way
        return filt._false_filter()
    acts = list()
    for key, item in conf.items():
        if key == 'delete':
            acts.append(actions.delete())
        elif key == 'move':
            acts.append(actions.move(**item))
        elif key == 'rename':
            item['old_pat'] = item.pop('old pattern') # The nice, readable yaml key won't work for python attributes. Need underscores
            item['new_pat'] = item.pop('new pattern')
            acts.append(actions.rename(**item))
        elif key == 'command':
            acts.append(actions.command(**item))
    return {
        'folders': [Path(f) for f in conf['folders']],
        'interval': int(conf['interval']),
        'actions': acts
    }


    
# -- Filter Parsing & Generation -- #

def gen_filter(obj):
    for key, item in obj.items():
        if key == 'name':
            obj['name'] = filt.name_filter(item)
        elif key == 'size':
            obj['size'] = filt_size(item)
        elif key == 'filetype':
            obj['filetype'] = filt.type_filter(*item)
        elif key == 'age':
            obj['age'] = filt_age(item)
        elif key == 'date created':
            obj['date created'] = filt_created(item)
        elif key == 'date modified':
            obj['date modified'] = filt_created(item)
        elif key == 'or':
            obj['or'] = filt.or_filter(gen_filter(item))
        elif key == 'xor':
            obj['xor'] = filt.xor_filter(gen_filter(item))
        elif key == 'and':
            obj['and'] = filt.and_filter(gen_filter(item))
        elif key == 'not':
            obj['not'] = filt.not_filter(gen_filter(item))
    filters = [item for _, item in obj.items()]
    if len(filters) > 1:
        return filt.and_filter(*filters) # Filters placed side-by-side are implicityly assumed to be an AND.
    else:
        return filters

def filt_age(obj):
    for key, item in obj.items():
        obj[key] = to_delta(item)
    return filt.age_filter(**obj)

def filt_size(obj):
    for key, item in obj.items():
        obj[key] = to_bytes(item)
    return filt.size_filter(**obj)

def filt_created(obj):
    for key, item in obj.items():
        obj[key] = to_datetime(item)
    return filt.created_filter(**obj)

def filt_modified(obj):
    for key, item in obj.items():
        obj[key] = to_datetime(item)
    return filt.created_filter(**obj)

def from_file(path, parser='yaml'):
    parser = parser.lower()
    p = Path(path)
    with p.open('r') as f:
        if parser == 'yaml':
            conf = safe_load(f)
        else:
            raise ValueError(f'Invalid parser: {parser}')
    
    parsed_conf = get_rule(conf.get('rule'))
    parsed_conf['filter'] = get_filter(conf.get('filter'))
    return parsed_conf
