#!/bin/bash

data=/data1/xqzhou/ja-en/Kyoto-data/kftt-data-1.0/data/thumt_data
scripts=/home/xqzhou/tools/compare-mt/scripts

ref=$data/kyoto-test.en
sys=/data1/xqzhou/metric-tool/sig-compression-ja-en/right-compression
sys1=$sys/right-sequence-level.beam5.trans.132.8
sys2=$sys/right-compression
sys1_name=Seq-KD-beam5
sys2_name=our-work
outputs=right-${sys1_name}-${sys2_name}
train_tgt=$data/train.cln.en
ref_labels="$ref.tag"
out_labels="$sys1.tag;$sys2.tag"

python $scripts/postag.py < $sys1 > $sys1.tag
python $scripts/postag.py < $sys2 > $sys2.tag

compare-mt $ref $sys1 $sys2 \
    --compare_scores score_type=bleu,bootstrap=1000 score_type=ribes,bootstrap=1000 score_type=length,bootstrap=1000 \
    --compare_word_accuracies bucket_type=freq,freq_corpus_file=$train_tgt bucket_type=label,ref_labels=$ref_labels,out_labels=$out_labels,label_set=CC+DT+IN+JJ+NN+NNP+NNS+PRP+RB+TO+VB+VBP+VBZ \
    --output_directory $outputs \
    --sys_name $sys1_name $sys2_name 
