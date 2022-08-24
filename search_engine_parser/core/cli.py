"""@desc
        Making use of the parser through cli
"""
from __future__ import print_function

import argparse
import sys
from datetime import datetime
from importlib import import_module

from blessed import Terminal
from search_engine_parser import __version__
from search_engine_parser.core.base import ReturnType
from search_engine_parser.core.exceptions import NoResultsOrTrafficError


def display(results, term, args):
    """ Displays search results
    """
    def print_one(kwargs):
        """ Print one result to the console """
        # Header
        if kwargs.get("titles"):
            print("\t{}".format(term.magenta(kwargs.pop("titles"))))
        if kwargs.get("links"):
            print("\t{}".format(kwargs.pop("links")))
            print("\t-----------------------------------------------------")
        if kwargs.get("descriptions"):
            print(kwargs.pop("descriptions"))
        if kwargs.values():
            for k, v in kwargs.items():
                if v:
                    print(k.strip(), " : ", v)
        print("\n")

    if args.rank and args.rank > 10:
        sys.exit(
            "Results are only limited to 10, specify a different page number instead")

    if not args.rank:
        for i in results:
            print_one(i)
    else:
        rank = args.rank
        print_one(results[rank])


def get_engine_class(engine):
    """ Return the Engine Class """
    try:
        module = import_module(f"search_engine_parser.core.engines.{engine.lower()}")
        return getattr(module, "Search")
    except ImportError:
        sys.exit(f'Engine < {engine} > does not exist')


def show_summary(term, engine_class):
    """ Show the summary of an Engine"""
    print(f"\t{term.magenta(engine_class.name)}")
    print("\t-----------------------------------------------------")
    print(engine_class.summary)


def main(args):    # pylint: disable=too-many-branches
    """
        Executes logic from parsed arguments
    """
    term = Terminal()
    engine_class = get_engine_class(args.engine)

    if args.show_summary:
        show_summary(term, engine_class)
        return

    if not args.query:
        print("--show-summary or --query argument must be passed")
        sys.exit(1)

    # Initialize search Engine with required params
    engine = engine_class()
    try:
        if args.clear_cache:
            engine.clear_cache()
        # Display full details: Header, Link, Description
        start = datetime.now()
        results = engine.search(
            args.query, args.page, return_type=ReturnType(args.type), url=args.url, proxy=args.proxy, proxy_auth=(args.proxy_user, args.proxy_password))
        duration = datetime.now() - start
        display(results, term, args)
        print(f"Total search took -> {duration} seconds")
    except NoResultsOrTrafficError as exc:
        print('\n', f'{term.red(str(exc))}')


def create_parser():
    """
    runner that handles parsing logic
    """
    parser = argparse.ArgumentParser(description='SearchEngineParser', prog="pysearch")

    parser.add_argument(
        '-V', '--version', action="version", version=f"%(prog)s v{__version__}"
    )


    parser.add_argument(
        '-e', '--engine',
        help='Engine to use for parsing the query e.g google, yahoo, bing,'
             'duckduckgo (default: google)',
        default='google')

    parser.add_argument(
        '--show-summary',
        action='store_true',
        help='Shows the summary of an engine')

    parser.add_argument(
        '-u',
        '--url',
        help='A custom link to use as base url for search e.g google.de')

    parser.add_argument(
        '-p',
        '--page',
        type=int,
        help='Page of the result to return details for (default: 1)',
        default=1)

    parser.add_argument(
        '-t', '--type',
        help='Type of detail to return i.e full, links, desciptions or titles (default: full)',
        default="full")

    parser.add_argument(
        '-cc', '--clear-cache',
        action='store_true',
        help='Clear cache of engine before searching')

    parser.add_argument(
        '-r',
        '--rank',
        type=int,
        help='ID of Detail to return e.g 5 (default: 0)')

    parser.add_argument(
        '--proxy',
        required=False,
        help='Proxy address to make use of')

    parser.add_argument(
        '--proxy-user',
        required='--proxy' in sys.argv,
        help='Proxy user to make use of')

    parser.add_argument(
        '--proxy-password',
        required='--proxy' in sys.argv,
        help='Proxy password to make use of')

    parser.add_argument(
        'query', type=str, nargs='?',
        help='Query string to search engine for')

    return parser


def runner():
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])
    main(args)


if __name__ == '__main__':
    runner()
