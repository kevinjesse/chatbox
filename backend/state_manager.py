from typing import List, Callable, Any
from template_manager import get_sentence, init_resources


class State:

    def __init__(self, *, name: str, next_state: Callable, **kwargs):
        self.name = name
        self.next_state = next_state
        self.template_sentence_query = kwargs.get('template_sentence_query', {})
        self.previous_state = kwargs.get('previous_state')

    def __str__(self):
        return self.name

    def utterance(self, **kwargs):
        if kwargs:
            # print('kwargs', kwargs)
            return get_sentence(dialogue_type=kwargs.get('dialogue_type', 'utterances'),
                                state=kwargs.get('state', self.name),
                                options=kwargs.get('options'),
                                returning_count=kwargs.get('returning_count', 0),
                                return_all=kwargs.get('return_all'))
        else:
            return get_sentence(dialogue_type='utterances',
                                state=self.template_sentence_query.get('state', self.name),
                                options=self.template_sentence_query.get('options'),
                                returning_count=self.template_sentence_query.get('returning_count', 0),
                                return_all=self.template_sentence_query.get('return_all'))


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
    init_resources()

    states = [
        State(name='intro', next_state=lambda: 'genre'),
        State(name='genre', next_state=lambda: 'actor'),
        State(name='actor', next_state=lambda: 'director'),
        State(name='director', next_state=lambda: 'mpaa'),
        State(name='mpaa', next_state=lambda: 'thinking'),
        State(name='thinking', next_state=lambda: 'tell',
              template_sentence_query={
                  'return_all': True
              }),
        State(name='tell', next_state=lambda: 'has_watched'),
        State(name='has_watched',
              next_state=lambda has_watched: 'has_watched_yes' if has_watched else 'has_watched_no'),
        State(name='has_watched_yes',
              next_state=lambda want_new_rec: 'thinking' if want_new_rec else 'bye',
              template_sentence_query={
                  'state': 'has_watched_response',
                  'options': 'yes'
              }),
        State(name='has_watched_no',
              next_state=lambda like_movie: 'thinking' if like_movie else 'bye',
              template_sentence_query={
                  'state': 'has_watched_response',
                  'options': 'no'
              }),
        State(name='bye', next_state=lambda: None)
    ]

    sm = StateManager(states)

    print(sm.current_state)
    print(sm.to_state('has_watched'))
    print(sm.next_state(has_watched=False).utterance())

    pass