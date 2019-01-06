########################################################################################
# Compare two systems using bootstrap resampling                                       #
#  adapted from https://github.com/neubig/util-scripts/blob/master/paired-bootstrap.py #
#                                                                                      #
# See, e.g. the following paper for references                                         #
#                                                                                      #
# Statistical Significance Tests for Machine Translation Evaluation                    #
# Philipp Koehn                                                                        #
# http://www.aclweb.org/anthology/W04-3250                                             #
#                                                                                      #
########################################################################################

import numpy as np
import nltk

def eval_measure(gold, sys, eval_type='bleu'):
  ''' Evaluation measure
  
  This takes in gold labels and system outputs and evaluates their
  accuracy. It currently supports:
  * Accuracy (acc), percentage of labels that match
  * BLEU score (bleu)
  :param gold: the correct labels
  :param sys: the system outputs
  :param eval_type: The type of evaluation to do (acc, bleu)
  '''
  if eval_type == 'acc':
    return sum([1 if g == s else 0 for g, s in zip(gold, sys)]) / float(len(gold))
  elif eval_type == 'bleu':
    gold_wrap = [[x] for x in gold]
    return nltk.translate.bleu_score.corpus_bleu(gold_wrap, sys)
  else:
    raise NotImplementedError('Unknown eval type in eval_measure: %s' % eval_type)

def sample_and_compare(gold, sys1, sys2, sample_ratio, 
                       ids, wins, sys1_scores, sys2_scores, 
                       eval_type='bleu'):
  # Subsample the gold and system outputs
  np.random.shuffle(ids)
  reduced_ids = ids[:int(len(ids)*sample_ratio)]
  reduced_gold = [gold[i] for i in reduced_ids]
  reduced_sys1 = [sys1[i] for i in reduced_ids]
  reduced_sys2 = [sys2[i] for i in reduced_ids]
  # Calculate accuracy on the reduced sample and save stats
  sys1_score = eval_measure(reduced_gold, reduced_sys1, eval_type=eval_type)
  sys2_score = eval_measure(reduced_gold, reduced_sys2, eval_type=eval_type)
  if sys1_score > sys2_score:
    wins[0] += 1
  elif sys1_score < sys2_score:
    wins[1] += 1
  else:
    wins[2] += 1
  sys1_scores.append(sys1_score)
  sys2_scores.append(sys2_score)

def eval_with_paired_bootstrap(gold, sys1, sys2,
                               num_samples=1000, sample_ratio=0.5,
                               eval_type='bleu'):
  ''' Evaluate with paired boostrap
  This compares two systems, performing a signifiance tests with
  paired bootstrap resampling to compare the accuracy of the two systems.
  
  :param gold: The correct labels
  :param sys1: The output of system 1
  :param sys2: The output of system 2
  :param num_samples: The number of bootstrap samples to take
  :param sample_ratio: The ratio of samples to take every time
  :param eval_type: The type of evaluation to do (acc, bleu)
  '''
  assert(len(gold) == len(sys1))
  assert(len(gold) == len(sys2))
  
  sys1_scores = []
  sys2_scores = []
  wins = [0, 0, 0]
  n = len(gold)
  ids = list(range(n))

  try:
    from tqdm import tqdm
    for _ in tqdm(range(num_samples)):
      sample_and_compare(gold, sys1, sys2, sample_ratio, ids, wins, sys1_scores, sys2_scores, eval_type)
  except ImportError:
    for _ in range(num_samples):
      sample_and_compare(gold, sys1, sys2, sample_ratio, ids, wins, sys1_scores, sys2_scores, eval_type)

  # Print win stats
  wins = [x/float(num_samples) for x in wins]
  print('Win ratio: sys1=%.3f, sys2=%.3f, tie=%.3f' % (wins[0], wins[1], wins[2]))
  if wins[0] > wins[1]:
    print('(sys1 is superior with p value p=%.3f)\n' % (1-wins[0]))
  elif wins[1] > wins[0]:
    print('(sys2 is superior with p value p=%.3f)\n' % (1-wins[1]))

  # Print system stats
  sys1_scores.sort()
  sys2_scores.sort()
  print('sys1 mean=%.3f, median=%.3f, 95%% confidence interval=[%.3f, %.3f]' %
          (np.mean(sys1_scores), np.median(sys1_scores), sys1_scores[int(num_samples * 0.025)], sys1_scores[int(num_samples * 0.975)]))
  print('sys2 mean=%.3f, median=%.3f, 95%% confidence interval=[%.3f, %.3f]' %
          (np.mean(sys2_scores), np.median(sys2_scores), sys2_scores[int(num_samples * 0.025)], sys2_scores[int(num_samples * 0.975)]))

