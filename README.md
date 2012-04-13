Install
-------
 - `pip install -e git://github.com/saltycrane/trace-tools.git#egg=trace_tools`

Usage
-----

    from trace_tools.decorators import trace

    @trace((), max_level=2)
    def some_function_to_trace(arg):
        """
        """
        do_something()

    @another_decorator
    @trace(('httplib', 'logging', 'ssl', 'email', 'encodings', 'gzip', 'urllib',
            'multiprocessing', 'django', 'cgi', 'requests', 'cookielib', 'base64',
            'slumber', 'zipfile', 'redis',),
           max_level=4)
    def some_other_function():
        """
        """
        do_something_else()
