class State:

    _state = {}

    def __init__(self):
        self.__dict__ = self._state


class AppState(State):

    def __init__(self, last_added=None, last_updated=None, last_deleted=None):
        State.__init__(self)
        if last_added or self._state.get('last_added') is None:
            self.last_added = last_added
        if last_updated or self._state.get('last_updated') is None:
            self.last_updated = last_updated
        if last_deleted or self._state.get('last_deleted') is None:
            self.last_deleted = last_deleted
