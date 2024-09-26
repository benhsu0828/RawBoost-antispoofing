This is the script to compute pooled EER and min-tDCF for ASVspoof2021 LA scenario. 

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
python evaluate.py C:\Users\bente\Desktop\model\RawNet2_ASVspoof2021\LA\Baseline-RawNet2\eval_CM_scores2.txt ./keys eval
