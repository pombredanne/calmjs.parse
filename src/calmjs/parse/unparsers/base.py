# -*- coding: utf-8 -*-
"""
Base unparser implementation

Brings together the different bits from the different helpers.
"""

from calmjs.parse.ruletypes import (
    Space,
    OptionalSpace,
    Newline,
    OptionalNewline,
    Indent,
    Dedent,
)
from calmjs.parse.unparsers.walker import (
    Dispatcher,
    walk,
)
from calmjs.parse.layout import (
    rule_handler_noop,
    token_handler_str_default,
    layout_handler_space_imply,
    layout_handler_newline_optional_pretty,
    layout_handler_newline_simple,
    layout_handler_space_optional_pretty,
    layout_handler_space_minimum,
)


def default_layout_handlers():
    return {
        Space: layout_handler_space_imply,
        OptionalSpace: layout_handler_space_optional_pretty,
        Newline: layout_handler_newline_simple,
        OptionalNewline: layout_handler_newline_optional_pretty,
        # if an indent is immediately followed by dedent without actual
        # content, simply do nothing.
        (Indent, Newline, Dedent): rule_handler_noop,
    }


def minimum_layout_handlers():
    return {
        Space: layout_handler_space_minimum,
        OptionalSpace: layout_handler_space_minimum,
    }


class BaseUnparser(object):
    """
    A simple base class for gluing together the default Dispatcher and
    walk function together to achieve unparsing.
    """

    def __init__(
            self,
            definitions,
            token_handler=token_handler_str_default,
            layouts=(default_layout_handlers,),
            layout_handlers=None,
            walk=walk,
            dispatcher_cls=Dispatcher):
        """
        Optional arguements

        definition
            The definition for unparsing.
        token_handler
            passed onto the dispatcher object; this is the handler that
            will process
        layouts
            An tuple of callables that will provide the setup of
            indentation.  The callables must return a layout_handlers
            mapping, which is a dict with the key being the layout class
            and the value being the callable that accept a
            Dispatcher instance, a Node, before and after chunk.
        layout_handlers
            Additional layout handlers, given in the mapping that was
            described above.
        walk
            The walk function - defaults to the version from the walker
            module
        dispatcher_cls
            The Dispatcher class - defaults to the version from the
            prettyprint module
        """

        self.token_handler = token_handler
        self.layout_handlers = {}
        for layout in layouts:
            self.layout_handlers.update(layout())
        if layout_handlers:
            self.layout_handlers.update(layout_handlers)
        self.definitions = {}
        self.definitions.update(definitions)
        self.walk = walk
        self.dispatcher_cls = dispatcher_cls

    def __call__(self, node):
        dispatcher = self.dispatcher_cls(
            self.definitions, self.token_handler, self.layout_handlers)
        for chunk in self.walk(dispatcher, node, dispatcher[node]):
            yield chunk
