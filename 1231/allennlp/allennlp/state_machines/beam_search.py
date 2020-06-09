from collections import defaultdict
from typing import Dict, Generic, List, Mapping, Sequence, TypeVar

from allennlp.common.registrable import FromParams
from allennlp.state_machines.states import State
from allennlp.state_machines.transition_functions import TransitionFunction
from allennlp.state_machines.align_score import align
##from allennlp.state_machines.align_model_multi import Classification
#from allennlp.state_machines.align_model import Classification
from allennlp.data.fields.production_rule_field import ProductionRuleArray
import logging

StateType = TypeVar('StateType', bound=State)  # pylint: disable=invalid-name
logger = logging.getLogger(__name__)

class BeamSearch(FromParams, Generic[StateType]):
    """
    This class implements beam search over transition sequences given an initial ``State`` and a
    ``TransitionFunction``, returning the highest scoring final states found by the beam (the
    states will keep track of the transition sequence themselves).

    The initial ``State`` is assumed to be `batched`.  The value we return from the search is a
    dictionary from batch indices to ranked finished states.

    IMPORTANT: We assume that the ``TransitionFunction`` that you are using returns possible next
    states in sorted order, so we do not do an additional sort inside of ``BeamSearch.search()``.
    If you're implementing your own ``TransitionFunction``, you must ensure that you've sorted the
    states that you return.

    Parameters
    ----------
    beam_size : ``int``
        The beam size to use.
    per_node_beam_size : ``int``, optional (default = beam_size)
        The maximum number of candidates to consider per node, at each step in the search.
        If not given, this just defaults to `beam_size`. Setting this parameter
        to a number smaller than `beam_size` may give better results, as it can introduce
        more diversity into the search. See Freitag and Al-Onaizan 2017,
        "Beam Search Strategies for Neural Machine Translation".
    """
    def __init__(self, beam_size: int, per_node_beam_size: int = None) -> None:
        self._beam_size = beam_size
        self._per_node_beam_size = per_node_beam_size or beam_size
        #self.align_model = Classification()

    def search(self,
               num_steps: int,
               initial_state: StateType,
               transition_function: TransitionFunction,
               question: List[str],
               kg,
               actions: List[List[ProductionRuleArray]],
               world,
               embedded_ques,
               keep_final_unfinished_states: bool = True) -> Mapping[int, Sequence[StateType]]:
        """
        Parameters
        ----------
        num_steps : ``int``
            How many steps should we take in our search?  This is an upper bound, as it's possible
            for the search to run out of valid actions before hitting this number, or for all
            states on the beam to finish.
        initial_state : ``StateType``
            The starting state of our search.  This is assumed to be `batched`, and our beam search
            is batch-aware - we'll keep ``beam_size`` states around for each instance in the batch.
        transition_function : ``TransitionFunction``
            The ``TransitionFunction`` object that defines and scores transitions from one state to the
            next.
        keep_final_unfinished_states : ``bool``, optional (default=True)
            If we run out of steps before a state is "finished", should we return that state in our
            search results?

        Returns
        -------
        best_states : ``Dict[int, List[StateType]]``
            This is a mapping from batch index to the top states for that instance.
        """
        finished_states: Dict[int, List[StateType]] = defaultdict(list)
        states = [initial_state]
        step_num = 1
        
        action_mapping = {}
        for batch_index, batch_actions in enumerate(actions):
            for action_index, action in enumerate(batch_actions):
                action_mapping[(batch_index, action_index)] = action[0]
        
        while states and step_num <= num_steps:
            next_states: Dict[int, List[StateType]] = defaultdict(list)
            grouped_state = states[0].combine_states(states)
            for next_state in transition_function.take_step(grouped_state, embedded_ques, question, kg, action_mapping, world, max_actions=self._per_node_beam_size):
                # NOTE: we're doing state.batch_indices[0] here (and similar things below),
                # hard-coding a group size of 1.  But, our use of `next_state.is_finished()`
                # already checks for that, as it crashes if the group size is not 1.
                batch_index = next_state.batch_indices[0]
                if next_state.is_finished():
                    finished_states[batch_index].append(next_state)
                else:
                    if step_num == num_steps and keep_final_unfinished_states:
                        finished_states[batch_index].append(next_state)
                    next_states[batch_index].append(next_state)
            states = []
            for batch_index, batch_states in next_states.items():
                # The states from the generator are already sorted, so we can just take the first
                # ones here, without an additional sort.
                states.extend(batch_states[:self._beam_size])
            step_num += 1
        best_states: Dict[int, Sequence[StateType]] = {}
        #logger.info("*" * 20 + "decoding:" + "*" * 20)
        for batch_index, batch_states in finished_states.items():
            # The time this sort takes is pretty negligible, no particular need to optimize this
            # yet.  Maybe with a larger beam size...
            #finished_to_sort = [(-state.score[0].item() for state in batch_states]
            finished_to_sort = []
            for state in batch_states:
                raw_score = -state.score[0].item()
                
                #logger.info("#" * 50)
                #logger.info("raw_score:")
                #logger.info(raw_score)
                #logger.info("question:")
                #logger.info(question)
                #logger.info("table:")
                #logger.info(kg)
                #align_score = self.get_score(batch_index, state, question, kg, action_mapping, world[batch_index], raw_score)
                #logger.info("align_score:")
                #logger.info(align_score)
                finished_to_sort.append((raw_score, state))
                #finished_to_sort.append((raw_score - align_score, state))
            ##finished_to_sort = [(-state.score[0].item() + self.get_score(batch_index, state, question, table, action_mapping, world[batch_index]), state) for state in batch_states]
            

            finished_to_sort.sort(key=lambda x: x[0])
            best_states[batch_index] = [state[1] for state in finished_to_sort[:self._beam_size]]
            
        return best_states

    def get_score(self, batch_idx, state, question, table, action_mapping, world, predict_score):
        action_strings = [action_mapping[(batch_idx, action_index)] for action_index in state.action_history[0]]
        #logger.info("logical_form:")
        try:
            logical_form = world.get_logical_form(action_strings, add_var_function=False)
            #logger.info(logical_form)
        except Exception:
            #logger.info("Error generating logical form.")
            return 0
        decoded = state.action_history[0]
        raw_align_score = align(logical_form, question, table)
        align_score = self.align_model.get_score(question, table, logical_form, predict_score, raw_align_score)
        #align_score = self.align_model.get_score_multi(question, table, logical_form, predict_score)
        return align_score