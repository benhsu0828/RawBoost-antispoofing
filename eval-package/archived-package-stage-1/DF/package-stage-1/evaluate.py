#!/usr/bin/env python
# """
# Script to compute pooled EER for ASVspoof2021 DF. 

# Usage:
# $: python PATH_TO_SCORE_FILE PATH_TO_GROUDTRUTH_DIR phase
 
#  -PATH_TO_SCORE_FILE: path to the score file 
#  -PATH_TO_GROUNDTRUTH_DIR: path to the directory that has the CM protocol.
#     Please follow README, download the key files, and use ./keys
#  -phase: either progress, eval, or hidden_track

# Example:
# $: python evaluate.py score.txt ./keys eval
# python evaluate.py C:/Users/bente/Desktop/model/RawBoost-antispoofing/InTheWild_eval_CM_scores_file.txt C:/Users/bente/Desktop/model/RawBoost-antispoofing/eval-package/keys/DF/ eval
# """
import sys, os.path
import numpy as np
import pandas
import eval_metrics as em
from glob import glob

# if len(sys.argv) != 4:
#     print("CHECK: invalid input arguments. Please read the instruction below:")
#     print(__doc__)
#     exit(1)

submit_file = sys.argv[1]
truth_dir = sys.argv[2]
phase = sys.argv[3]

# cm_key_file = os.path.join(truth_dir, 'C:\Users\bente\Desktop\model\RawBoost-antispoofing\our_metadata_list_派蒙.csv')
cm_key_file = "C:\\Users\\bente\\Desktop\\model\\RawBoost-antispoofing\\our_metadata_list_派蒙_test.csv"


def eval_to_score_file(score_file, cm_key_file):
    
    cm_data = pandas.read_csv(cm_key_file, sep=',', header=None)
    #print("cm_data: ", cm_data)
    submission_scores = pandas.read_csv(score_file, sep=' ', header=None, skipinitialspace=True)
    if len(submission_scores) != len(cm_data):
        print('CHECK: submission has %d of %d expected trials.' % (len(submission_scores), len(cm_data)))
        exit(1)

    if len(submission_scores.columns) > 2:
        print('CHECK: submission has more columns (%d) than expected (2). Check for leading/ending blank spaces.' % len(submission_scores.columns))
        exit(1)
            
    #cm_scores = submission_scores.merge(cm_data[cm_data[7] == phase], left_on=0, right_on=1, how='inner')  # check here for progress vs eval set
    cm_scores = submission_scores.merge(cm_data, left_on=0, right_on=0, how='inner')  # check here for progress vs eval set
    # print("cm_scores: ", cm_scores)
    bona_cm = cm_scores[cm_scores[2] == 'bonafide']['1_x'].values
    spoof_cm = cm_scores[cm_scores[2] == 'spoof']['1_x'].values
    # print("bona_cm: ", bona_cm)
    # print("spoof_cm: ", spoof_cm)
    eer_cm = em.compute_eer(bona_cm, spoof_cm)[0]
    out_data = "eer: %.2f\n" % (100*eer_cm)
    print(out_data)
    return eer_cm

if __name__ == "__main__":

    if not os.path.isfile(submit_file):
        print("%s doesn't exist" % (submit_file))
        exit(1)
        
    if not os.path.isdir(truth_dir):
        print("%s doesn't exist" % (truth_dir))
        exit(1)

    if phase != 'progress' and phase != 'eval' and phase != 'hidden_track':
        print("phase must be either progress, eval, or hidden_track")
        exit(1)

    _ = eval_to_score_file(submit_file, cm_key_file)
    
        
