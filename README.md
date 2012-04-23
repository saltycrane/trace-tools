Install
-------
 - `pip install -e git://github.com/saltycrane/trace-tools.git#egg=trace_tools`

Usage
-----

    from trace_tools.decorators import trace

    @trace()
    def some_function_to_trace(arg):
        do_something()

    @trace(max_level=2)
    def some_function_to_trace(arg):
        do_something()

    @another_decorator
    @trace(
        max_level=4,
        ignore=(
            'httplib', 'logging', 'ssl', 'email', 'encodings', 'gzip', 'urllib',
            'multiprocessing', 'django', 'cgi', 'requests', 'cookielib', 'base64',
            'slumber', 'zipfile', 'redis'))
    def some_other_function():
        do_something_else()

    @trace(max_level=10, calls_only=False, ignore=('debugtools', 'blessings', 'ipdb', 'IPython',), ignore_builtins=True, ignore_stdlib=True)
    def process(self, content):
        do_stuff()

    @trace(max_level=115, calls_only=True, ignore=(
            'suds.resolver',
            'suds.sudsobject',
            'suds.xsd',
            'debugtools', 'blessings', 'ipdb', 'IPython',),
           ignore_builtins=True, ignore_stdlib=True)
    def process(self, content):
        do_stuff()
