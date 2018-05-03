from typing import List, Callable
from template_manager import get_sentence

class State:
    def __init__(self, *, name: str, next_state: Callable, **kwargs):
        self.name = name
        self.next_state = next_state
        self.template_name = kwargs.get('template_name', self.name)
        self.template_sentence_query = kwargs.get('template_sentence_query', {
            'dialogue_type': 'utterances',
            'state': self.template_name
        })

    def __str__(self):
        return self.name

    def utterance(self):
        get_sentence(**self.template_sentence_query)


class Condition:
    pass


class StateManager:

    def __init__(self, possible_states: List[State]):
        self.possible_states = {state.name: state for state in possible_states}
        self._current_state = possible_states[0].name

    @property
    def current_state(self) -> State:
        return self.possible_states[self._current_state]

    def next_state(self, **kwargs) -> State:
        next_state_str = self.current_state.next_state(**kwargs)
        if next_state_str is not None:
            self._current_state = next_state_str
        return self.current_state

    def to_state(self, state: str):
        if state in self.possible_states:
            self._current_state = state
            return self.current_state
        else:
            return None


if __name__ == '__main__':
    states = [
        State(name='intro', next_state=lambda: 'genre'),
        State(name='genre', next_state=lambda: 'actor'),
        State(name='actor', next_state=lambda: 'director'),
        State(name='director', next_state=lambda: 'mpaa'),
        State(name='mpaa', next_state=lambda: 'thinking'),
        State(name='thinking', next_state=lambda: 'tell'),
        State(name='tell', next_state=lambda: 'has_watched'),
        State(name='has_watched',
              next_state=lambda has_watched: 'has_watched_yes' if has_watched else 'has_watched_no'),
        State(name='has_watched_yes', next_state=lambda: 'bye'),
        State(name='has_watched_no', next_state=lambda: 'bye'),
        State(name='bye', next_state=lambda: None)
    ]

    sm = StateManager(states)

    print(sm.current_state)
    print(sm.to_state('has_watched'))
    print(sm.next_state(has_watched=False))

    pass