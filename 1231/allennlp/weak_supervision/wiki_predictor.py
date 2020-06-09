import os
import pathlib
from subprocess import run
from typing import List
import shutil
import requests

from overrides import overrides

from allennlp.common.util import JsonDict, sanitize
from allennlp.data import DatasetReader, Instance
from allennlp.models import Model
from allennlp.predictors.predictor import Predictor



@Predictor.register('wikifree-parser')
class WikiTablesParserPredictor(Predictor):

    def __init__(self, model: Model, dataset_reader: DatasetReader) -> None:
        super().__init__(model, dataset_reader)


    @overrides
    def predict_instance(self, instance: Instance) -> JsonDict:
        outputs = self._model.forward_on_instance(instance)
        fmodel = open('/mnt/shige_0929.txt', "a+")

        # for key, value in outputs.items():
        #     fmodel.write(key + "\n")
        for item in outputs['logical_form']:
            fmodel.write(item + '\n')
        fmodel.write(100*"*"+'\n')
        # for item in outputs['best_logical_form']:
        #     fmodel.write(item+"\n")
        return sanitize(outputs)

    def predict_batch_instance(self, instances: List[Instance]) -> List[JsonDict]:
        fmodel = open('/mnt/shige_0929.txt', "w")
        outputs = self._model.forward_on_instances(instances)
        for output in outputs:
            for item in output['logical_form']:
                fmodel.write(item+'\n')
            fmodel.write(100*"*")
        fmodel.close()
        return sanitize(outputs)

