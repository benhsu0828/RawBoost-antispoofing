import argparse
import sys
import os
import numpy as np
import torch
from torch import nn
from torch import Tensor
from torch.utils.data import DataLoader
import yaml
from mydata_utils_rawboost import genSpoof_list,gen_ourdata_list_split,Dataset_ASVspoof2019_train,Dataset_ASVspoof2021_eval,Dataset_ourdata_train,Dataset_ourdata_eval
from model import RawNet
from tensorboardX import SummaryWriter
from core_scripts.startup_config import set_random_seed

__author__ = "Hemlata Tak"
__email__ = "tak@eurecom.fr"



def evaluate_accuracy(dev_loader, model, device):
    num_correct = 0.0
    num_total = 0.0
    model.eval()
    for batch_x, batch_y in dev_loader:
        
        batch_size = batch_x.size(0)
        num_total += batch_size
        batch_x = batch_x.to(device)
        batch_y = batch_y.view(-1).type(torch.int64).to(device)
        batch_out = model(batch_x)
        _, batch_pred = batch_out.max(dim=1)
        num_correct += (batch_pred == batch_y).sum(dim=0).item()
    return 100 * (num_correct / num_total)


def produce_evaluation_file(dataset, model, device, save_path):
    data_loader = DataLoader(dataset, batch_size=128, shuffle=False, drop_last=False)
    model.eval()
    
    for batch_x,utt_id in data_loader:
        fname_list = []
        score_list = []  
        batch_size = batch_x.size(0)
        batch_x = batch_x.to(device)
        batch_out = model(batch_x,is_test=True)
        batch_score = (batch_out[:, 1]
                       ).data.cpu().numpy().ravel()
        # add outputs
        fname_list.extend(utt_id)
        score_list.extend(batch_score.tolist())
        
        with open(save_path, 'a+') as fh:
            for f, cm in zip(fname_list,score_list):
                fh.write('{} {}\n'.format(f, cm))
        fh.close()   
    print('Scores saved to {}'.format(save_path))

def train_epoch(train_loader, model, lr,optim, device):
    running_loss = 0
    num_correct = 0.0
    num_total = 0.0
    ii = 0
    model.train()

    #set objective (Loss) functions
    weight = torch.FloatTensor([0.1, 0.9]).to(device)
    criterion = nn.CrossEntropyLoss(weight=weight)
    
    for batch_x, batch_y in train_loader:
       
        batch_size = batch_x.size(0)
        num_total += batch_size
        ii += 1
        batch_x = batch_x.to(device)
        batch_y = batch_y.view(-1).type(torch.int64).to(device)
        batch_out = model(batch_x)
        batch_loss = criterion(batch_out, batch_y)
        _, batch_pred = batch_out.max(dim=1)
        num_correct += (batch_pred == batch_y).sum(dim=0).item()
        running_loss += (batch_loss.item() * batch_size)
        if ii % 10 == 0:
            sys.stdout.write('\r \t {:.2f}'.format(
                (num_correct/num_total)*100))
        optim.zero_grad()
        batch_loss.backward()
        optim.step()
       
    running_loss /= num_total
    train_accuracy = (num_correct/num_total)*100
    return running_loss, train_accuracy

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ASVspoof2021 baseline system')
    # Dataset
    #parser.add_argument('--database_path', type=str, default='C:/Users/bente/Desktop/dataset/release_in_the_wild/', help='Change this to user\'s full directory address of LA database (ASVspoof2019- for training & development (used as validation), ASVspoof2021 for evaluation scores). We assume that all three ASVspoof 2019 LA train, LA dev and ASVspoof2021 LA eval data folders are in the same database_path directory.')
    parser.add_argument('--database_path', type=str, default='C:\\Users\\bente\\Desktop\\dataset\\派蒙\\flac', help='')
    '''
    % database_path/
    %      |- ASVspoof2021_LA_eval/flac
    %      |- ASVspoof2019_LA_train/flac
    %      |- ASVspoof2019_LA_dev/flac
    '''

    parser.add_argument('--protocols_path', type=str, default='C:/Users/bente/Desktop/dataset/in_the_wild_metadata/meta_eval.csv', help='Change with path to user\'s LA database protocols directory address')
    '''
    % protocols_path/
    %   |- ASVspoof_LA_cm_protocols
    %      |- ASVspoof2021.LA.cm.eval.trl.txt
    %      |- ASVspoof2019.LA.cm.dev.trl.txt 
    %      |- ASVspoof2019.LA.cm.train.trn.txt 
    '''

    # Hyperparameters
    parser.add_argument('--batch_size', type=int, default=128)
    parser.add_argument('--num_epochs', type=int, default=100)
    parser.add_argument('--lr', type=float, default=0.0001)
    parser.add_argument('--weight_decay', type=float, default=0.0001)
    parser.add_argument('--loss', type=str, default='weighted_CCE')
    # model
    parser.add_argument('--seed', type=int, default=1234, 
                        help='random seed (default: 1234)')
    
    parser.add_argument('--model_path', type=str,
                        default=None, help='Model checkpoint')
    parser.add_argument('--comment', type=str, default=None,
                        help='Comment to describe the saved model')
    # Auxiliary arguments
    parser.add_argument('--track', type=str, default='LA',choices=['LA', 'PA','DF'], help='LA/PA/DF')
    parser.add_argument('--eval_output', type=str, default=None,
                        help='Path to save the evaluation result')
    parser.add_argument('--eval', action='store_true', default=False,
                        help='eval mode')
    parser.add_argument('--is_eval', action='store_true', default=False,help='eval database')
    parser.add_argument('--eval_part', type=int, default=0)
    # backend options
    parser.add_argument('--cudnn-deterministic-toggle', action='store_false', \
                        default=True, 
                        help='use cudnn-deterministic? (default true)')    
    
    parser.add_argument('--cudnn-benchmark-toggle', action='store_true', \
                        default=False, 
                        help='use cudnn-benchmark? (default false)') 

    ##===================================================Rawboost data augmentation parameters======================================================================#

    parser.add_argument('--algo', type=int, default=4, 
                    help='Rawboost algos discriptions. 0: No augmentation 1: LnL_convolutive_noise, 2: ISD_additive_noise, 3: SSI_additive_noise, 4: series algo (1+2+3), \
                          5: series algo (1+2), 6: series algo (1+3), 7: series algo(2+3), 8: parallel algo(1,2) .[default=0]')

    # LnL_convolutive_noise parameters 
    parser.add_argument('--nBands', type=int, default=5, 
                    help='number of notch filters.The higher the number of bands, the more aggresive the distortions is.[default=5]')
    parser.add_argument('--minF', type=int, default=20, 
                    help='minimum centre frequency [Hz] of notch filter.[default=20] ')
    parser.add_argument('--maxF', type=int, default=8000, 
                    help='maximum centre frequency [Hz] (<sr/2)  of notch filter.[default=8000]')
    parser.add_argument('--minBW', type=int, default=100, 
                    help='minimum width [Hz] of filter.[default=100] ')
    parser.add_argument('--maxBW', type=int, default=1000, 
                    help='maximum width [Hz] of filter.[default=1000] ')
    parser.add_argument('--minCoeff', type=int, default=10, 
                    help='minimum filter coefficients. More the filter coefficients more ideal the filter slope.[default=10]')
    parser.add_argument('--maxCoeff', type=int, default=100, 
                    help='maximum filter coefficients. More the filter coefficients more ideal the filter slope.[default=100]')
    parser.add_argument('--minG', type=int, default=0, 
                    help='minimum gain factor of linear component.[default=0]')
    parser.add_argument('--maxG', type=int, default=0, 
                    help='maximum gain factor of linear component.[default=0]')
    parser.add_argument('--minBiasLinNonLin', type=int, default=5, 
                    help=' minimum gain difference between linear and non-linear components.[default=5]')
    parser.add_argument('--maxBiasLinNonLin', type=int, default=20, 
                    help=' maximum gain difference between linear and non-linear components.[default=20]')
    parser.add_argument('--N_f', type=int, default=5, 
                    help='order of the (non-)linearity where N_f=1 refers only to linear components.[default=5]')

    # ISD_additive_noise parameters
    parser.add_argument('--P', type=int, default=10, 
                    help='Maximum number of uniformly distributed samples in [%].[defaul=10]')
    parser.add_argument('--g_sd', type=int, default=2, 
                    help='gain parameters > 0. [default=2]')

    # SSI_additive_noise parameters
    parser.add_argument('--SNRmin', type=int, default=10, 
                    help='Minimum SNR value for coloured additive noise.[defaul=10]')
    parser.add_argument('--SNRmax', type=int, default=40, 
                    help='Maximum SNR value for coloured additive noise.[defaul=40]')
    
    ##===================================================Rawboost data augmentation ======================================================================#


    dir_yaml = os.path.splitext('model_config_RawNet')[0] + '.yaml'

    with open(dir_yaml, 'r') as f_yaml:
            parser1 = yaml.load(f_yaml)

    if not os.path.exists('models'):
        os.mkdir('models')
    args = parser.parse_args()
 
    #make experiment reproducible
    set_random_seed(args.seed, args)
    
    track = args.track

    assert track in ['LA', 'PA','DF'], 'Invalid track given'

    #database
    prefix      = 'ASVspoof_{}'.format(track)
    prefix_2019 = 'ASVspoof2019.{}'.format(track)
    prefix_2021 = 'ASVspoof2021.{}'.format(track)
    
    #define model saving path
    model_tag = 'model_{}_{}_{}_{}_{}'.format(
        track, args.loss, args.num_epochs, args.batch_size, args.lr)
    if args.comment:
        model_tag = model_tag + '_{}'.format(args.comment)
    model_save_path = os.path.join('models', model_tag)

    #set model save directory
    if not os.path.exists(model_save_path):
        os.mkdir(model_save_path)
    
    #GPU device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'                  
    print('Device: {}'.format(device))
    
    #model 
    model = RawNet(parser1['model'], device)
    nb_params = sum([param.view(-1).size()[0] for param in model.parameters()])
    model =(model).to(device)
    
    #set Adam optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr,weight_decay=args.weight_decay)
    
    if args.model_path:
        model.load_state_dict(torch.load(args.model_path,map_location=device))
        print('Model loaded : {}'.format(args.model_path))

    #evaluation 
    if args.eval:
        d_label_eval,file_eval = gen_ourdata_list_split( dir_meta =  os.path.join(args.protocols_path),is_test=True)
        print('no. of eval trials',len(file_eval))
        eval_set=Dataset_ourdata_eval(list_IDs = file_eval,base_dir = os.path.join(args.database_path))
        produce_evaluation_file(eval_set, model, device, args.eval_output)
        sys.exit(0)

     
    # define train dataloader

    d_label_trn,file_train = gen_ourdata_list_split( dir_meta =  os.path.join(args.protocols_path),is_train=True)
    print('no. of training trials',len(file_train))
    train_set=Dataset_ourdata_train(args,
                                    list_IDs = file_train,
                                    labels = d_label_trn,
                                    base_dir =args.database_path,
                                    algo=args.algo)
    train_loader = DataLoader(train_set, batch_size=args.batch_size,num_workers=8, shuffle=True,drop_last = True)
    
    del train_set,d_label_trn
    

    # define validation dataloader

    d_label_dev,file_dev = gen_ourdata_list_split( dir_meta =  os.path.join(args.protocols_path),is_val=True)
    print('no. of validation trials',len(file_dev))

    dev_set = Dataset_ourdata_train(args,list_IDs = file_dev,
		labels = d_label_dev,
		base_dir = os.path.join(args.database_path),algo=args.algo)
    dev_loader = DataLoader(dev_set, batch_size=args.batch_size,num_workers=8, shuffle=False)
    del dev_set,d_label_dev

    # Training and validation 
    num_epochs = args.num_epochs
    writer = SummaryWriter('logs/{}'.format(model_tag))
    best_acc = 99
    for epoch in range(num_epochs):
        running_loss, train_accuracy = train_epoch(train_loader,model, args.lr,optimizer, device)
        valid_accuracy = evaluate_accuracy(dev_loader, model, device)
        writer.add_scalar('train_accuracy', train_accuracy, epoch)
        writer.add_scalar('valid_accuracy', valid_accuracy, epoch)
        writer.add_scalar('loss', running_loss, epoch)
        print('\n{} - {} - {:.2f} - {:.2f}'.format(epoch,
                                                   running_loss, train_accuracy, valid_accuracy))
        
        if valid_accuracy > best_acc:
            print('best model find at epoch', epoch)
        best_acc = max(valid_accuracy, best_acc)
        # torch.save(model.state_dict(), os.path.join(model_save_path, 'epoch_{}.pth'.format(epoch)))
        torch.save(model.state_dict(), "./models/Best_pimon_epoch_{}.pth".format(epoch))
