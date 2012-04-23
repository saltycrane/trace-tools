import linecache
import sys
from functools import wraps

from trace_tools.module_names import builtin_modules, stdlib_modules


global_trace_on = False
global_modules_to_ignore = ()
global_level = 0
global_max_level = 100


def trace(modules_to_ignore, max_level):
    global global_modules_to_ignore
    global global_max_level
    global_modules_to_ignore = modules_to_ignore
    global_max_level = max_level

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

    retval = _trace_function

    if not global_trace_on:
        return retval

    if event == 'call':
        global_level += 1
    elif event == 'return':
        global_level -= 1

    if global_level > global_max_level:
        return retval

    if '__name__' in frame.f_globals:
        name = frame.f_globals["__name__"]
    else:
        name = 'whatisthename'

    # skip builtin modules and stdlib modules
    if name in builtin_modules:
        return retval
    if name in stdlib_modules:
        return retval

    # skip modules_to_ignore
    if name.startswith(global_modules_to_ignore):
        return retval

    # get line number
    lineno = frame.f_lineno

    # get filename
    if '__file__' in frame.f_globals:
        filename = frame.f_globals["__file__"]
    else:
        filename = 'asdf'
    if filename == "<stdin>":
        filename = "trace_function.py"
    if (filename.endswith(".pyc") or
        filename.endswith(".pyo")):
        filename = filename[:-1]

    # get line
    line = linecache.getline(filename, lineno)
    line = line.rstrip()
    output = "%s:%s: %s" % (name, lineno, line)

    if line.strip():
        if event == 'line':
            sys.stderr.write(output + '\n')

    return retval


sys.settrace(_trace_function)
