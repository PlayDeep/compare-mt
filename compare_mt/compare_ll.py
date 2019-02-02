import argparse

# In-package imports
from . import corpus_utils
from . import bucketers
from . import arg_utils
from . import print_utils

def print_word_likelihood_report(ref, ll1, ll2, bucket_type='freq',
                          freq_count_file=None, freq_corpus_file=None,
                          label_corpus=None, label_set=None,
                          case_insensitive=False):
    """
    Print a report comparing the word log likelihood.

    Args:
    ref: the ref of words over which the likelihoods are computed
    ll1: likelihoods corresponding to each word in ref from the sys 1
    ll2: likelihoods corresponding to each word in ref from the sys 2
    bucket_type: A string specifying the way to bucket words together to calculate average likelihood
    freq_corpus_file: When using "freq" as a bucketer, which corpus to use to calculate frequency.
    freq_count_file: An alternative to freq_corpus that uses a count file in "word\tfreq" format.
    label_corpus: When using "label" as bucket type, the corpus containing the labels
                  corresponding to each word in the corpus
    label_set: the permissible set of labels when using "label" as a bucket type
    case_insensitive: A boolean specifying whether to turn on the case insensitive option
    """
    bucketer = bucketers.create_word_bucketer_from_profile(bucket_type=bucket_type,
                                                         freq_count_file=freq_count_file,
                                                         freq_corpus_file=freq_corpus_file,
                                                         label_set=label_set,
                                                         case_insensitive=case_insensitive)

    if type(label_corpus) == str:
        label_corpus = corpus_utils.load_tokens(label_corpus)

    if label_corpus is not None:
        ref = label_corpus

    ll1_out = bucketer.calc_bucketed_likelihoods(ref, ll1)
    ll2_out = bucketer.calc_bucketed_likelihoods(ref, ll2)

    print(f'--- average word log likelihood by {bucketer.name()} bucket')
    for bucket_str, l1, l2 in zip(bucketer.bucket_strs, ll1_out, ll2_out):
        print (bucket_str + "\t", end='')
        if type(l1) == str:
            print (l1 + "\t", end='')
        else:
            print ("%.4f\t" %(l1), end='')

        if type(l2) == str:
            print (l2 + "\t")
        else:
            print ("%.4f" %(l2))
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Program to compare MT results',
    )
    parser.add_argument('--ref-file', type=str, dest='ref_file',
                        help='A path to a reference file over which the likelihoods are being computed/compared')
    parser.add_argument('--ll1-file', type=str, dest='ll1_file',
                        help='A path to file containing log likelihoods for ref-file generated by sys 1')
    parser.add_argument('--ll2-file', type=str, dest='ll2_file',
                        help='A path to file containing log likelihoods for ref-file generated by sys 2')
    parser.add_argument('--compare-word-likelihoods', type=str, dest='compare_word_likelihoods', nargs='*',
                        default=['bucket_type=freq'],
                        help="""
                        Compare word log likelihoods by buckets. Can specify arguments in 'arg1=val1,arg2=val2,...' format.
                        See documentation for 'print_word_likelihood_report' to see which arguments are available.
                        """)

    args = parser.parse_args()

    ref = corpus_utils.load_tokens(args.ref_file)
    ll1, ll2 = [corpus_utils.load_nums(x) for x in (args.ll1_file, args.ll2_file)]

    # Word likelihood analysis
    if args.compare_word_likelihoods:
        print_utils.print_header('Word Likelihood Analysis')
        for profile in args.compare_word_likelihoods:
            kargs = arg_utils.parse_profile(profile)
            print_word_likelihood_report(ref, ll1, ll2, **kargs)
            print()


if __name__ == '__main__':
  main()