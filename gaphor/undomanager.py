# vim:sw=4:et:

import gobject


def get_undo_manager():
    """Return the default undo manager.
    """
    return _default_undo_manager


def undoable(func):
    """Descriptor. Enables an undo transaction around the method/function.
    """
    def wrapper(*args, **kwargs):
        undo_manager = get_undo_manager()
        undo_manager.begin_transaction()
        try:
            func(*args, **kwargs)
        finally:
            undo_manager.commit_transaction()
    return wrapper

class TransactionError(Exception):

    def __init__(self, msg):
        self.args = msg


class Transaction(object):
    """A transaction. Every action that is added between a begin_transaction()
    and a commit_transaction() call is recorded in a transaction, do it can
    be played back when a transaction is undone.
    """

    def __init__(self):
        self._actions = []

    def add(self, action):
        self._actions.append(action)

    def can_undo(self):
        return self._actions and True or False

    def undo(self):
        self._actions.reverse()
        for action in self._actions:
            try:
                #log.debug('Undoing action %s' % action)
                action.undo()
            except Exception, e:
                log.error('Error while undoing action %s' % action, e)

    def redo(self):
        self._actions.reverse()
        for action in self._actions:
            try:
                #log.debug('Redoing action %s' % action)
                action.redo()
            except Exception, e:
                log.error('Error while redoing action %s' % action, e)


class UndoManager(gobject.GObject):
    """Simple transaction manager for Gaphor.
    This transaction manager supports nested transactions.
    """

    def __init__(self):
        self.__gobject_init__()
        self._in_undo = False
        self._undo_stack = []
        self._redo_stack = []
        self._stack_depth = 20
        self._current_transaction = None
        self._transaction_depth = 0
        self._short_circuit = False

    def clear_undo_stack(self):
        self._undo_stack = []
        self._current_transaction = None

    def clear_redo_stack(self):
        self._redo_stack = []

#    def add_undo_action(self, action):
#        try:
#            self._short_circuit = True
#            diacanvas.UndoManager.add_undo_action(self, action)
#            self.on_add_undo_action(action)
#        finally:
#            self._short_circuit = False

    def begin_transaction(self):
        """Add an action to the current transaction
        """
        if self._in_undo:
            return

        #log.debug('begin_transaction')
        if self._current_transaction:
            self._transaction_depth += 1
            #raise TransactionError, 'Already in a transaction'
            return

        self._current_transaction = Transaction()
        self.clear_redo_stack()
        self._transaction_depth += 1

    def add_undo_action(self, action):
        """Add an action to undo. An action
        """
        if self._short_circuit:
            return

        #log.debug('add_undo_action: %s %s' % (self._current_transaction, action))
        if not self._current_transaction:
            return

        if self._redo_stack:
            self.clear_redo_stack()

        self._current_transaction.add(action)

    def commit_transaction(self):
        if self._in_undo:
            return

        #log.debug('commit_transaction')
        if not self._current_transaction:
            return #raise TransactionError, 'No transaction to commit'

        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            if self._current_transaction.can_undo():
                self._undo_stack.append(self._current_transaction)
            else:
                pass #log.debug('nothing to commit')

            self._current_transaction = None

    def discard_transaction(self):
        if self._in_undo:
            return

        if not self._current_transaction:
            raise TransactionError, 'No transaction to discard'

        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            self._current_transaction = None

    def undo_transaction(self):
        if not self._undo_stack:
            return

        if self._current_transaction:
            log.warning('Trying to undo a transaction, while in a transaction')
            self.commit_transaction()
        transaction = self._undo_stack.pop()
        try:
            self._in_undo = True
            transaction.undo()
        finally:
            self._in_undo = False
        self._redo_stack.append(transaction)

    def redo_transaction(self):
        if not self._redo_stack:
            return

        transaction = self._redo_stack.pop()
        try:
            self._in_undo = True
            transaction.redo()
        finally:
            self._in_undo = False
        self._undo_stack.append(transaction)

    def in_transaction(self):
        return self._current_transaction is not None

    def can_undo(self):
        return bool(self._current_transaction or self._undo_stack)

    def can_redo(self):
        return bool(self._redo_stack)


# Register as resource:
import gaphor
_default_undo_manager = gaphor.resource(UndoManager)
del gaphor
