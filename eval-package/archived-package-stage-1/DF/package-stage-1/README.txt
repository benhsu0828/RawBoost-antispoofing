This is the script to compute pooled EER for ASVspoof2021 DF scenario. 

Dependency:
Python3, Numpy, pandas

Usage:
1. download and untar the ground-truth label files
$: download.sh
The downloaded directory will be named as ./keys

2. run python script
$: python PATH_TO_SCORE_FILE PATH_TO_GROUDTRUTH_DIR phase
 
 -PATH_TO_SCORE_FILE: path to the score file 
 -PATH_TO_GROUNDTRUTH_DIR: path to the directory from step1
    Please use ./keys
 -phase: either progress, eval, or hidden_track

Example:
$: python evaluate.py C:/Users/bente/Desktop/model/RawBoost-antispoofing/'eval_CM_scores_file.txt' ./keys eval
C:/Users/bente/Desktop/model/RawBoost-antispoofing/'eval_CM_scores_file.txt'

python evaluate.py C:/Users/bente/Desktop/model/RawBoost-antispoofing/eval_Ourdata_pimon_score2.txt C:\Users\bente\Desktop\model\RawBoost-antispoofing\eval-package\keys eval 
