RawBoost: A Raw Data Boosting and Augmentation Method applied to Automatic Speaker Verification Anti-Spoofing
===============
This repository contains our implementation of the paper, "RawBoost: A Raw Data Boosting and Augmentation Method applied to Automatic Speaker Verification Anti-Spoofing". This work introduce RawBoost, a data boosting and augmentation method for the design of more reliable spoofing detection solutions which operate directly upon raw waveform inputs ([Paper link here](https://arxiv.org/pdf/2111.04433.pdf)).


## Installation
First, clone the repository locally, create and activate a conda environment, and install the requirements :
```
$ git clone https://github.com/TakHemlata/RawBoost-antispoofing.git
$ conda create --name RawBoost_antispoofing python=3.8.8
$ conda activate RawBoost_antispoofing
$ conda install pytorch torchvision torchaudio cudatoolkit=11.1 -c pytorch -c nvidia

# CUDA 11.1
conda install pytorch==1.8.0 torchvision==0.9.0 torchaudio==0.8.0 cudatoolkit=11.1 -c pytorch -c conda-forge

conda install pytorch==2.3.0 torchvision==0.18.0 torchaudio==2.3.0 pytorch-cuda=12.1 -c pytorch -c nvidia
$ pip install -r requirements.txt
```


## Experiments

### Dataset
Our experiments are performed on the logical access (LA) partition of the ASVspoof 2021 dataset (train on 2019 LA training and evaluate on 2021 LA evaluation database).

### Training
To train the model run:
```
python main.py --track=LA --loss=WCE   --lr=0.0001 --batch_size=128

派盟
python mymain.py --track=LA --loss=WCE --model_path=C:/Users/bente/Desktop/model/RawBoost-antispoofing/pre_trained_model/Best_model.pth  --lr=0.0001 --batch_size=64 --database_path=C:/Users/bente/Desktop/dataset/派蒙/flac/ --protocols_path=C:/Users/bente/Desktop/model/RawBoost-antispoofing/our_metadata_list_派蒙.csv
```
tensorboard --logdir=.\logs
### Testing

To evaluate your own model on LA evaluation dataset:

```
python main.py --track=LA --loss=WCE --is_eval --eval --model_path=./pre_trained_model/Best_model.pth --eval_output=eval_CM_scores_file.txt

ITW
python ITWmain.py --track=LA --loss=WCE --is_eval --eval --model_path=./pre_trained_model/Best_model.pth --eval_output=InTheWild_eval_CM_scores_file.txt --database_path=C:/Users/bente/Desktop/dataset/release_in_the_wild/flac/ --protocols_path=C:/Users/bente/Desktop/dataset/in_the_wild_metadata/ITW_metadata.csv

```
派盟
python mymain.py --track=LA --loss=WCE --is_eval --eval --model_path=C:/Users/bente/Desktop/model/RawBoost-antispoofing/models/Best_pimon_epoch_58.pth --database_path=C:/Users/bente/Desktop/dataset/派蒙/flac/ --protocols_path=C:/Users/bente/Desktop/model/RawBoost-antispoofing/our_metadata_list_派蒙.csv --eval_output=eval_Ourdata_pimon_score2.txt


We also provide a pre-trained models. To use it you can run: 
```
python main.py --track=LA --loss=WCE --is_eval --eval --model_path='Pre_trained_models.pth' --eval_output='RawBoost_eval_CM_scores.txt'
```

This repository is built on our End-to-end RawNet2 CM system (ASVspoof2021 Challenge baseline).
- [ASVspoof 2021 Challenge baseline repo](https://github.com/asvspoof-challenge/2021/tree/main/LA/Baseline-RawNet2)


## Contact
For any query regarding this repository, please contact:
- Hemlata Tak: tak[at]eurecom[dot]fr
- Massimiliano Todisco: todisco[at]eurecom[dot]fr

## Citation
If you use RawBoost code in your research please use the following citation:

```bibtex
@inproceedings{tak2021rawboost,
  title={RawBoost: A Raw Data Boosting and Augmentation Method applied to Automatic Speaker Verification Anti-Spoofing},
  author={Tak, Hemlata and Kamble, Madhu and Patino, Jose and Todisco, Massimiliano and Evans, Nicholas},
  booktitle={IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
  year={2022}
}
```

