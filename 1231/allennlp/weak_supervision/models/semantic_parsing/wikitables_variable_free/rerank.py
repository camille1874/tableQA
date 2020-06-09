#from typing import Any, Dict, List
#
#from overrides import overrides
#import torch
#
#from allennlp.data import Vocabulary
#from allennlp.data.fields.production_rule_field import ProductionRuleArray
#from allennlp.models.model import Model
#from allennlp.modules import Attention, FeedForward, Seq2SeqEncoder, Seq2VecEncoder, TextFieldEmbedder
#from allennlp.state_machines.states import GrammarBasedState
#from allennlp.state_machines.transition_functions import LinkingTransitionFunction
#from allennlp.state_machines import util
#
#from weak_supervision.semparse.worlds import WikiTablesVariableFreeWorld
#from weak_supervision.models.semantic_parsing.wikitables_variable_free.wikitables_variable_free_parser import WikiTablesVariableFreeParser
#
#from allennlp.nn.util import get_text_field_mask
#from allennlp.training.trainer import Trainer
#from allennlp.training.metrics import CategoricalAccuracy, F1Measure
#
#@Model.register("classifier")
#class Classifier(WikiTablesVariableFreeParser):
#    """
#    A ``WikiTablesVariableFreeMml`` is a :class:`WikiTablesVariableFreeSemanticParser` which is trained to
#    maximize the marginal likelihood of an approximate set of logical forms which give the correct
#    denotation. This is a re-implementation of the model used for the paper `Neural Semantic Parsing with Type
#    Constraints for Semi-Structured Tables
#    <https://www.semanticscholar.org/paper/Neural-Semantic-Parsing-with-Type-Constraints-for-Krishnamurthy-Dasigi/8c6f58ed0ebf379858c0bbe02c53ee51b3eb398a>`_,
#    by Jayant Krishnamurthy, Pradeep Dasigi, and Matt Gardner (EMNLP 2017).
#    Parameters
#    ----------
#    vocab : ``Vocabulary``
#    question_embedder : ``TextFieldEmbedder``
#        Embedder for questions. Passed to super class.
#    action_embedding_dim : ``int``
#        Dimension to use for action embeddings. Passed to super class.
#    encoder : ``Seq2SeqEncoder``
#        The encoder to use for the input question. Passed to super class.
#    entity_encoder : ``Seq2VecEncoder``
#        The encoder to used for averaging the words of an entity. Passed to super class.
#    decoder_beam_search : ``BeamSearch``
#        When we're not training, this is how we will do decoding.
#    max_decoding_steps : ``int``
#        When we're decoding with a beam search, what's the maximum number of steps we should take?
#        This only applies at evaluation time, not during training. Passed to super class.
#    attention : ``Attention``
#        We compute an attention over the input question at each step of the decoder, using the
#        decoder hidden state as the query.  Passed to the transition function.
#    mixture_feedforward : ``FeedForward``, optional (default=None)
#        If given, we'll use this to compute a mixture probability between global actions and linked
#        actions given the hidden state at every timestep of decoding, instead of concatenating the
#        logits for both (where the logits may not be compatible with each other).  Passed to
#        the transition function.
#    add_action_bias : ``bool``, optional (default=True)
#        If ``True``, we will learn a bias weight for each action that gets used when predicting
#        that action, in addition to its embedding.  Passed to super class.
#    training_beam_size : ``int``, optional (default=None)
#        If given, we will use a constrained beam search of this size during training, so that we
#        use only the top ``training_beam_size`` action sequences according to the model in the MML
#        computation.  If this is ``None``, we will use all of the provided action sequences in the
#        MML computation.
#    use_neighbor_similarity_for_linking : ``bool``, optional (default=False)
#        If ``True``, we will compute a max similarity between a question token and the `neighbors`
#        of an entity as a component of the linking scores.  This is meant to capture the same kind
#        of information as the ``related_column`` feature. Passed to super class.
#    dropout : ``float``, optional (default=0)
#        If greater than 0, we will apply dropout with this probability after all encoders (pytorch
#        LSTMs do not apply dropout to their last layer). Passed to super class.
#    num_linking_features : ``int``, optional (default=10)
#        We need to construct a parameter vector for the linking features, so we need to know how
#        many there are.  The default of 10 here matches the default in the ``KnowledgeGraphField``,
#        which is to use all ten defined features. If this is 0, another term will be added to the
#        linking score. This term contains the maximum similarity value from the entity's neighbors
#        and the question. Passed to super class.
#    rule_namespace : ``str``, optional (default=rule_labels)
#        The vocabulary namespace to use for production rules.  The default corresponds to the
#        default used in the dataset reader, so you likely don't need to modify this. Passed to super
#        class.
#    """
#    def __init__(self,
#                 vocab: Vocabulary,
#                 question_embedder: TextFieldEmbedder,
#                 action_embedding_dim: int,
#                 encoder: Seq2SeqEncoder,
#                 entity_encoder: Seq2VecEncoder,
#                 decoder_beam_search: BeamSearch,
#                 max_decoding_steps: int,
#                 attention: Attention,
#                 mixture_feedforward: FeedForward = None,
#                 add_action_bias: bool = True,
#                 training_beam_size: int = None,
#                 use_neighbor_similarity_for_linking: bool = False,
#                 dropout: float = 0.0,
#                 num_linking_features: int = 10,
#                 word_embeddings: TextFieldEmbedder,
#                 positive_label: str = '1',
#                 rule_namespace: str = 'rule_labels') -> None:
#        use_similarity = use_neighbor_similarity_for_linking
#        super().__init__(vocab=vocab,
#                         question_embedder=question_embedder,
#                         action_embedding_dim=action_embedding_dim,
#                         encoder=encoder,
#                         entity_encoder=entity_encoder,
#                         max_decoding_steps=max_decoding_steps,
#                         add_action_bias=add_action_bias,
#                         use_neighbor_similarity_for_linking=use_similarity,
#                         dropout=dropout,
#                         num_linking_features=num_linking_features,
#                         rule_namespace=rule_namespace)
#        self.vocab = vocab
#        self.linear = torch.nn.Linear(in_features=encoder.get_output_dim(),
#                                    out_features=vocab.get_vocab_size('labels'))
#        positive_index = vocab.get_token_index(positive_label, namespace='labels')
#        self.accuracy = CategoricalAccuracy()
#        self.f1_measure = F1Measure(positive_index)
#        self.loss_function = torch.nn.CrossEntropyLoss()
#
#
#    @overrides
#    def forward(self,  # type: ignore
#                question: Dict[str, torch.LongTensor],
#                table: Dict[str, torch.LongTensor],
#                table_lines: List[List[List[str]]],
#                question_lines: List[str],
#                world: List[WikiTablesVariableFreeWorld],
#                actions: List[List[ProductionRuleArray]],
#                #target_values: List[List[str]] = None,
#                #target_action_sequences: torch.LongTensor = None,
#                #target_action_scores: List[float] = None) -> Dict[str, torch.Tensor]:
#                target_action_sequences: torch.LongTensor = None,
#                target_action_scores: float) -> Dict[str, torch.Tensor]:
#        # pylint: disable=arguments-differ
#        """
#        In this method we encode the table entities, link them to words in the question, then
#        encode the question. Then we set up the initial state for the decoder, and pass that
#        state off to either a DecoderTrainer, if we're training, or a BeamSearch for inference,
#        if we're not.
#
#        Parameters
#        ----------
#        question : Dict[str, torch.LongTensor]
#           The output of ``TextField.as_array()`` applied on the question ``TextField``. This will
#           be passed through a ``TextFieldEmbedder`` and then through an encoder.
#        table : ``Dict[str, torch.LongTensor]``
#            The output of ``KnowledgeGraphField.as_array()`` applied on the table
#            ``KnowledgeGraphField``.  This output is similar to a ``TextField`` output, where each
#            entity in the table is treated as a "token", and we will use a ``TextFieldEmbedder`` to
#            get embeddings for each entity.
#        world : ``List[WikiTablesWorld]``
#            We use a ``MetadataField`` to get the ``World`` for each input instance.  Because of
#            how ``MetadataField`` works, this gets passed to us as a ``List[WikiTablesWorld]``,
#        actions : ``List[List[ProductionRuleArray]]``
#            A list of all possible actions for each ``World`` in the batch, indexed into a
#            ``ProductionRuleArray`` using a ``ProductionRuleField``.  We will embed all of these
#            and use the embeddings to determine which action to take at each timestep in the
#            decoder.
#        target_action_sequence : torch.Tensor, optional (default = None)
#           valid action sequence, an index into the list
#           of possible actions.  This tensor has shape ``(batch_size, sequence_length)``.
#        """
#        outputs: Dict[str, Any] = {}
#        rnn_state, grammar_state = self._get_initial_rnn_and_grammar_state(question,
#                                                                           table,
#                                                                           world,
#                                                                           actions,
#                                                                           outputs)
#        batch_size = len(rnn_state)
#        initial_score = rnn_state[0].hidden_state.new_zeros(batch_size)
#        initial_score_list = [initial_score[i] for i in range(batch_size)]
#        initial_state = GrammarBasedState(batch_indices=list(range(batch_size)),  # type: ignore
#                                          action_history=[[] for _ in range(batch_size)],
#                                          score=initial_score_list,
#                                          rnn_state=rnn_state,
#                                          grammar_state=grammar_state,
#                                          possible_actions=actions,
#                                          extras=target_values,
#                                          debug_info=None)
#
#        
#        
#        
#        
#        if self.training:
#            return self._decoder_trainer.decode(initial_state,
#                                                self._decoder_step,
#                                                (target_action_sequences, target_mask), target_action_scores)
#        else:
#            if target_action_sequences is not None:
#                tmp = self._decoder_trainer.decode(initial_state, self._decoder_step, (target_action_sequences, target_mask), target_action_scores)
#                outputs['loss'] = tmp['loss']
#            num_steps = self._max_decoding_steps
#            # This tells the state to start keeping track of debug info, which we'll pass along in
#            # our output dictionary.
#            initial_state.debug_info = [[] for _ in range(batch_size)]
#            
#           # ttext_idx = table['text']['tokens'][0].cpu().numpy()
#           # table_lines = []
#           # for x in ttext_idx:
#           #     tmp = []
#           #     for y in x:
#           #         tmp.append(self.vocab.get_token_from_index(index=y))
#           #     table_lines.append(tmp)
#           # index = 1
#           # idx2row = {}
#           # kg = {}
#           # while table_lines[index][0] == "-1":
#           #     column_name = table_lines[index][2].replace('fb:row.row.', '')
#           #     kg[column_name] = []
#           #     idx2row[table_lines[index][1].strip()] = column_name
#           #     index += 1
#           # for line in table_lines[index:]:
#           #     if line[1] in idx2row:
#           #         kg[idx2row[line[1]]].append(line[2].replace('fb:cell.', ''))
#
#            table_lines = table_lines[0]
#            index = 1
#            idx2row = {}
#            kg = {}
#            while table_lines[index][0] == "-1":
#                column_name = table_lines[index][2].replace('fb:row.row.', '')
#                kg[column_name] = []
#                idx2row[table_lines[index][1].strip()] = column_name
#                index += 1
#            for line in table_lines[index:]:
#                if line[1] in idx2row:
#                    kg[idx2row[line[1]]].append(line[2].replace('fb:cell.', ''))
#        
#            #ques = [self.vocab.get_token_from_index(index=x) for x in list(question['tokens'][0].cpu().numpy())]
#            #ques = ' '.join(ques)
#            ques = question_lines[0]
#
#            best_final_states = self._beam_search.search(num_steps,
#                                                         initial_state,
#                                                         self._decoder_step,
#                                                         ques,
#                                                         kg,
#                                                         actions,
#                                                         world,
#                                                         keep_final_unfinished_states=False)
#            for i in range(batch_size):
#                # Decoding may not have terminated with any completed logical forms, if `num_steps`
#                # isn't long enough (or if the model is not trained enough and gets into an
#                # infinite action loop).
#                if i in best_final_states:
#                    best_action_indices = best_final_states[i][0].action_history[0]
#                    if target_action_sequences is not None:
#                        # Use a Tensor, not a Variable, to avoid a memory leak.
#                        targets = target_action_sequences[i].data
#                        sequence_in_targets = 0
#                        sequence_in_targets = self._action_history_match(best_action_indices, targets)
#                        self._action_sequence_accuracy(sequence_in_targets)
#
#            metadata = None
#            self._compute_validation_outputs(actions,
#                                             best_final_states,
#                                             world,
#                                             target_values,
#                                             metadata,
#                                             outputs)
#            return outputs