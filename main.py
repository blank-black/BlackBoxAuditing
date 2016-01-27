
# NOTE: These settings and imports should be the only things that change
#       across experiments on different datasets and ML model types.
from ricci_experiment.load_data import load_data
from model_factories.SVM_ModelFactory import ModelFactory
from measurements import accuracy
response_header = "Class"
graph_measurers = [accuracy]
rank_measurer = accuracy
features_to_ignore = ["Position"]

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# NOTE: You should not need to change anything below this point.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from gradient_feature_auditing import GradientFeatureAuditor
from audit_reading import graph_audit, graph_audits, rank_audit_files

def run():
  headers, train_set, test_set = load_data()

  """
   ModelFactories require a `build` method that accepts some training data
   with which to train a brand new model. This `build` method should output
   a Model object that has a `test` method -- which, when given test data
   in the same format as the training data, yields a confusion table detailing
   the correct and incorrect predictions of the model.
  """
  all_data = train_set + test_set
  model_factory = ModelFactory(all_data, headers, response_header)
  model = model_factory.build(train_set)

  # Don't audit the response feature.
  features_to_ignore.append(response_header)

  # Translate the headers into indexes for the auditor.
  feature_indexes_to_ignore = [headers.index(f) for f in features_to_ignore]

  # Perform the Gradient Feature Audit and dump the audit results into files.
  auditor = GradientFeatureAuditor(model, headers, train_set, all_data, #TODO
                                   features_to_ignore=feature_indexes_to_ignore)
  audit_filenames = auditor.audit()

  # Graph the audit files.
  for audit_filename in audit_filenames:
    audit_image_filename = audit_filename + ".png"
    graph_audit(audit_filename, graph_measurers, audit_image_filename)

  ranked_features = rank_audit_files(audit_filenames, rank_measurer)
  print ranked_features

  ranked_graph_filename = "{}/{}.png".format(auditor.OUTPUT_DIR, rank_measurer.__name__)
  graph_audits(audit_filenames, rank_measurer, ranked_graph_filename)

if __name__=="__main__":
  run()
