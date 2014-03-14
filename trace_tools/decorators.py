# TODO: preset ignore modules
# TODO: need a trace up tool that traces everything that called something
# check the inspect module or somewhere in the stdlib

import linecache
import sys
import time
from functools import wraps

from trace_tools.module_names import builtin_modules, stdlib_modules


# global constants
DEFAULT_MAX_LEVEL = 100
DEFAULT_MODULES_TO_IGNORE = ()
THIS_MODULE_NAME = 'trace_tools'

# global variables
global_trace_on = False
global_level = 0
global_started = None
global_prev_name = ''
global_output_prev = ''
global_ignored_call_count = 0
global_ignore_children_on = False
global_ignore_children_start_level = 0
global_options = {
    'max_level': None,
    'modules_to_ignore': None,
    'start_mod': None,
    'start_line': None,
    'end_mod': None,
    'end_line': None,
    'module_only': None,
    'calls_only': None,
    'ignore_builtins': None,
    'ignore_stdlib': None,
    'use_stderr': None,
    'ignore_children_of_ignored': None,
    'timestamp_lines': None,
}


def trace(
        start=None,
        end=None,
        max_level=DEFAULT_MAX_LEVEL,
        ignore=DEFAULT_MODULES_TO_IGNORE,
        module_only=False,
        calls_only=False,
        ignore_builtins=True,
        ignore_stdlib=True,
        use_stderr=False,
        ignore_children=False,
        timestamp_lines=False,
):
    """
    :param max_level: (integer) max nested call level
    :param ignore: list/tuple of modules to ignore
    :param start: e.g. 'suds.client:595'
    :param end: e.g. 'suds.client:596'
    :param ignore_children: ignore calls/lines that are children of
        ignored modules
    """
    global global_options
    global global_started
    global_options['modules_to_ignore'] = ignore
    global_options['max_level'] = max_level
    global_options['module_only'] = module_only
    global_options['calls_only'] = calls_only
    global_options['ignore_builtins'] = ignore_builtins
    global_options['ignore_stdlib'] = ignore_stdlib
    global_options['use_stderr'] = use_stderr
    global_options['ignore_children_of_ignored'] = ignore_children
    global_options['timestamp_lines'] = timestamp_lines
    if start:
        global_options['start_mod'], start_line = start.split(':')
        global_options['start_line'] = int(start_line)
        global_started = False
    else:
        global_started = True
    if end:
        global_options['end_mod'], end_line = end.split(':')
        global_options['end_line'] = int(end_line)

    def true_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            global global_trace_on
            global_trace_on = True
            r = f(*args, **kwargs)
            global_trace_on = False
            return r
        return wrapper
    return true_decorator


def _trace_function(frame, event, arg):
    global global_level
    global global_started
    global global_prev_name
    global global_output_prev
    global global_ignored_call_count
    global global_ignore_children_on
    global global_ignore_children_start_level

    retval = _trace_function

    if not global_trace_on:
        return retval

    # get module name
    if '__name__' in frame.f_globals:
        name = frame.f_globals["__name__"]
    else:
        name = 'couldnotdeterminename'

    # skip this module
    if name.startswith(THIS_MODULE_NAME):
        return retval

    # get line number
    lineno = frame.f_lineno

    # check start/end
    if global_options['start_mod'] and global_options['start_line']:
        if (name == global_options['start_mod'] and
                lineno == global_options['start_line']):
            global_started = True
    if (global_started and
            global_options['end_mod'] and global_options['end_line']):
        if (name == global_options['end_mod'] and
                lineno == global_options['end_line']):
            global_started = False
    if not global_started:
        return retval

    # check max nested call level. do this after start/end check to start the
    # level at 1 when using the "start" option
    if event == 'call' or event == 'c_call':
        global_level += 1
    elif event == 'return' or event == 'c_return':
        global_level -= 1
    if global_level > global_options['max_level']:
        return retval

    # skip children of ignored modules
    if (global_options['ignore_children_of_ignored'] and
            global_ignore_children_on):
        if global_level <= global_ignore_children_start_level:
            global_ignore_children_on = False
        # elif global_level < global_ignore_children_start_level:
        #     raise Exception('error tracking levels')
        else:
            if event == 'call':
                global_ignored_call_count += 1
            return retval

    # skip builtin modules and stdlib modules
    # skip modules_to_ignore
    if ((global_options['ignore_builtins'] and name in builtin_modules) or
            (global_options['ignore_stdlib'] and name in stdlib_modules) or
            name.startswith(tuple(global_options['modules_to_ignore']))):
        if event == 'call':
            global_ignored_call_count += 1
        global_ignore_children_on = True
        global_ignore_children_start_level = global_level
        return retval

    # get filename
    if '__file__' in frame.f_globals:
        filename = frame.f_globals["__file__"]
    else:
        filename = 'couldnotdeterminefilename'
    if (filename.endswith(".pyc") or filename.endswith(".pyo")):
        filename = filename[:-1]

    # get line
    line = linecache.getline(filename, lineno)
    line = line.rstrip()
    output = "%s:%s: %s" % (name, lineno, line)

    # print line
    if global_options['use_stderr']:
        foutput = sys.stderr
    else:
        foutput = sys.stdout

    if global_options['timestamp_lines']:
        time_prefix = '%10.2f ' % (time.time())
    else:
        time_prefix = ''

    prefix = '%slevel%02d%s>' % (time_prefix, global_level,
                                 ' -' * global_level)
    if line.strip():
        if global_options['module_only']:
            if name != global_prev_name and event == 'line':
                foutput.write(prefix + name + '\n')
        else:
            if event != 'line':
                prefix = '%s(%s)' % (prefix, event)
            output = prefix + output + '\n'

            if global_options['calls_only']:
                if event == 'call' or event == 'c_call':
                    foutput.write(global_output_prev)
                    foutput.write(output)
                elif event == 'return' or event == 'c_return':
                    foutput.write(output)
                global_output_prev = output
            else:
                if global_ignored_call_count > 0:
                    foutput.write(
                        '<%d call(s) ignored>\n' % global_ignored_call_count)
                    global_ignored_call_count = 0
                foutput.write(output)

        global_prev_name = name

    return retval


sys.settrace(_trace_function)
