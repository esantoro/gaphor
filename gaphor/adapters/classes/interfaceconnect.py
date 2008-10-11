"""
Interface item related connections.

The connectors implemented in this module check if connection is possible
to folded interface, see `gaphor.diagram.classes.interface` documentation
for details.
"""

from zope import interface, component

from gaphor import UML
from gaphor.diagram import items
from gaphor.adapters.connectors import ImplementationConnect, DependencyConnect

class ImplementationInterfaceConnect(ImplementationConnect):
    """
    Connect interface item and a behaviored classifier using an
    implementation.
    """
    component.adapts(items.InterfaceItem, items.ImplementationItem)

    def connect(self, handle, port):
        """
        Implementation item can be changed to draw in solid mode, when
        connected to folded interface.
        """
        super(ImplementationInterfaceConnect, self).connect(handle, port)
        if handle is self.line.head:
            self.line._solid = self.element.folded != self.element.FOLDED_NONE


    def disconnect(self, handle):
        """
        If implementation item is no longer connected to an interface, then
        draw it in non-solid mode.
        """
        super(ImplementationInterfaceConnect, self).disconnect(handle)
        if handle is self.line.head:
            self.line._solid = False


component.provideAdapter(ImplementationInterfaceConnect)



class DependencyInterfaceConnect(DependencyConnect):
    """
    Connect interface item with dependency item.
    """
    component.adapts(items.InterfaceItem, items.DependencyItem)

    def connect(self, handle, port):
        """
        Dependency item is changed to draw in solid mode, when connected to
        folded interface.
        """
        super(DependencyInterfaceConnect, self).connect(handle, port)
        line = self.line
        if handle is line.head and line.is_usage(self.element.subject):
            if self.element.folded != self.element.FOLDED_NONE:
                line._solid = True
                self.element.folded = self.element.FOLDED_REQUIRED


    def disconnect(self, handle):
        """
        If dependency item is no longer connected to an interface, then
        draw it in non-solid mode. Interface's folded mode changes to
        provided (ball) notation.
        """
        super(DependencyInterfaceConnect, self).disconnect(handle)
        if handle is self.line.head:
            self.line._solid = False
            self.element.folded = self.element.FOLDED_PROVIDED


component.provideAdapter(DependencyInterfaceConnect)