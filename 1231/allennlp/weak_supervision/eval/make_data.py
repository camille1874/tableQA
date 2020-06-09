#! /usr/bin/env python

# pylint: disable=invalid-name,wrong-import-position,protected-access
import sys
import os
import argparse

from allennlp.data.dataset_readers import WikiTablesDatasetReader
from allennlp.data.dataset_readers.semantic_parsing.wikitables.util import parse_example_line
from allennlp.models.archival import load_archive

#sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir)))))

from weak_supervision.data.dataset_readers import WikiTablesVariableFreeDatasetReader

def make_data(input_examples_file: str,
              tables_directory: str,
              archived_model_file: str,
              output_dir: str,
              num_logical_forms: int,
              variable_free: bool) -> None:
    if variable_free:
        reader = WikiTablesVariableFreeDatasetReader(tables_directory=tables_directory,
                                                     keep_if_no_logical_forms=True)
    else:
        reader = WikiTablesDatasetReader(tables_directory=tables_directory,
                                         keep_if_no_dpd=True)
    dataset = reader.read(input_examples_file)
    input_lines = []
    with open(input_examples_file) as input_file:
        input_lines = input_file.readlines()
    if variable_free:
        new_tables_config = {}
    else:
        # Note: Double { for escaping {.
        new_tables_config = f"{{model: {{tables_directory: {tables_directory}}}}}"
    archive = load_archive(archived_model_file,
                           overrides=new_tables_config)
    model = archive.model
    print("#" * 50)
    for param in model.named_parameters():
        print(param)
        

    model.eval()
    correct_num = 0
    for instance, example_line in zip(dataset, input_lines):
        outputs = model.forward_on_instance(instance)
        for k, v in outputs.items():
            print(k, v)
        parsed_info = parse_example_line(example_line)
        example_id = parsed_info["id"]
        best_action_sequence = outputs["best_action_sequence"]
        logical_forms = outputs["logical_form"]
        # print(logical_forms)
        world = instance.fields["world"].metadata
        try:
            logical_form = world.get_logical_form(best_action_sequence, add_var_function=False)
        except:
            logical_form = "placeholder"
        target_values = instance.fields["target_values"].metadata
        if world.evaluate_logical_form(logical_form, target_values):
            correct_num += 1
        # for logical_form in logical_forms:
        #     target_values = instance.fields["target_values"].metadata
        #     logical_form_is_correct = world.evaluate_logical_form(logical_form,
        #                                                       target_values)
        #     if logical_form_is_correct:
        #         correct_num += 1
        #         break
    print(len(dataset))
    print(correct_num / len(dataset))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", type=str, help="Input file", default="/home/xuzh/1231/data/WikiTableQuestions/data/pristine-unseen-tables.examples")
    #argparser.add_argument("--input", type=str, help="Input file", default="/home/xuzh/mnt/allennlp/nsm_allen/WikiTableQuestions/data/random-split-1-train-with-lgfs.examples")
    #argparser.add_argument("--input", type=str, help="Input file", default="/home/xuzh/mnt/allennlp/nsm_allen/WikiTableQuestions/data/random-split-1-train-noaligned.examples")
    argparser.add_argument("--tables_directory", type=str, help="Tables directory", default="/home/xuzh/1231/data/WikiTableQuestions/")
    argparser.add_argument("--archived_model", type=str, help="Archived model.tar.gz", default="/home/xuzh/mnt/allennlp/1016_1/model.tar.gz")
    argparser.add_argument("--output-dir", type=str, dest="output_dir", help="Output directory",
                           default="../../test_output_dir/")
    argparser.add_argument("--num-logical-forms", type=int, dest="num_logical_forms",
                           help="Number of logical forms to output", default=1)
    argparser.add_argument("--variable-free", dest="variable_free", action="store_true",
                           help="""Will use the variable free dataset reader, and assume the
                           archived model is trained on variable free language if set.""")
    args = argparser.parse_args()
    make_data(args.input, args.tables_directory, args.archived_model, args.output_dir,
              args.num_logical_forms, True)
