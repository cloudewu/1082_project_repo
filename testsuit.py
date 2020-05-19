from subprocess import call
from collections import defaultdict
from glob import glob
import os
import argparse

def get_input_files(files, work_dir, skip=False, log_folder='log'):
    print('Preprocessing news files...')

    if not os.path.isdir(log_folder):
        os.mkdir(log_folder)
    log_file = os.path.join(log_folder, 'preprocess.log')
    log = open(log_file, 'w+', encoding='utf-8')
    
    files_path = {}
    for filename in files:
        query = os.path.basename(filename).split('.')[0]
        output_dir = os.path.join(work_dir, query)
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        
        output_file = os.path.join(output_dir, 'input.txt')
        print('  {}  -->  {}'.format(filename, output_file))
        log.write('{}  -->  {}\n'.format(filename, output_file))

        if not skip:
            call(['python', 'util/extract.py', '-o', filename, output_file])
        elif not os.path.isfile(output_file):
            open(output_file, 'w+').close()   # creat empty file to prevent error
        files_path[query] = output_file
    log.close()
    return files_path


# command: `python extract_features.py --input_file=INPUT --output_file=OUTPUT --vocab_file=VOCFILE --bert_config_file=CONFIG --init_checkpoint=CHECKPOINT --layers=-1 --max_seq_length=INT --batch_size=INT`
def get_embeddings(input_path, work_dir, model, voc_path='model/vocab.txt', config_path='model/bert_config.json', ckpt='model/model.ckpt-0', layers=[-1, -2, -3, -4], max_seq_length=128, batch_size=8, output_path=defaultdict(lambda: defaultdict(str)), skip=False, logger=None, log_folder='log'):
    print('Getting embeddings...')

    if logger is None:
        if not os.path.isdir(log_folder):
            os.mkdir(log_folder)
        log_file = os.path.join(log_folder, 'embedding.log')
        log = open(log_file, 'a+', encoding='utf-8')
    else:
        log = logger
    
    arguments = []
    arguments.append('--vocab_file=' + voc_path)
    arguments.append('--bert_config_file=' + config_path)
    arguments.append('--init_checkpoint=' + ckpt)
    layers_str = ','.join([str(i) for i in layers])
    arguments.append('--layers=' + layers_str)
    arguments.append('--max_seq_length=' + str(max_seq_length))
    arguments.append('--batch_size=' + str(batch_size))

    for query, filepath in input_path.items():
        output_dir = os.path.join(work_dir, query)
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        output_file = os.path.join(output_dir, 'embedding_{}.jsonl'.format(model))

        print('  {}  -->  {}'.format(filepath, output_file))
        log.write('  {}  -->  {}\n'.format(filepath, output_file))
        
        if not skip:
            log.write(' '.join(['python', '-W ignore', 'extract_features.py', '--input_file=' + filepath, '--output_file=' + output_file] + arguments)+'\n')
            call(['python', '-W ignore', 'extract_features.py', '--input_file=' + filepath, '--output_file=' + output_file] + arguments)
        elif not os.path.isfile(output_file):
            open(output_file, 'w+').close()   # creat empty file to prevent error
        output_path[model][query] = output_file
    
    if logger is None:
        log.close()
    return output_path

def get_all_embeddings(input_path, work_dir, model_list=[0,3000,7000], model_dir='model', voc_path='vocab.txt', config_path='bert_config.json', ckpt_prefix='model.ckpt-', layers=[-1,-2,-3,-4], max_seq_length=128, batch_size=8, skip=False, log_folder='log'):
    if not os.path.isdir(log_folder):
        os.mkdir(log_folder)
    log_file = os.path.join(log_folder, 'embedding.log')
    log = open(log_file, 'w+', encoding='utf-8')

    config_file = os.path.join(model_dir, config_path)
    voc_file = os.path.join(model_dir, voc_path)
    output_pathes = defaultdict(lambda: defaultdict(str))
    for model in model_list:
        ckpt_file = os.path.join(model_dir, ckpt_prefix+str(model))
        output_pathes = get_embeddings(input_path, work_dir, model, voc_file, config_file, ckpt_file, layers, max_seq_length, batch_size, output_pathes, skip, log, None)
    log.close()

    return output_pathes


def get_clusters(input_path, embed_path, work_dir, model, algorithm, n=None, skip=False, logger=None, log_folder='log'):
    if logger is None:
        if not os.path.isdir(log_folder):
            os.mkdir(log_folder)
        log_file = os.path.join(log_folder, 'cluster.log')
        log = open(log_file, 'w+', encoding='utf-8')
    else:
        log = logger

    arguments = []
    filename = str(model)
    if algorithm.lower() == 'kmean':
        if n is None:
            print('[ WARN ] Use kmean but n is not specified. Use n=10 as default.')
            log.write('[ WARN ] Use kmean but n is not specified. Use n=10 as default.\n')
            n = 5
        arguments.append('--algorithm=kmean')
        arguments.append('-n='+str(n))
        filename += '_kmean_n' + str(n)
    elif algorithm.lower() in ['ap', 'affinitypropagation']:
        arguments.append('--algorithm=ap')
        filename += '_ap'
    filename += '.json'
        
    for query, input_file in input_path.items():
        embed_file = embed_path[query]
        output_dir = os.path.join(work_dir, query)
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        output_file = os.path.join(output_dir, filename)

        print('  {}, {}  -->  {}'.format(input_file, embed_file, output_file))
        log.write('{}, {}  -->  {}\n'.format(input_file, embed_file, output_file))
        if not skip:
            log.write(' '.join(['python', 'cluster.py', input_file, embed_file, output_file] + arguments)+'\n')
            call(['python', 'cluster.py', input_file, embed_file, output_file] + arguments)
        elif not os.path.isfile(output_file):
            open(output_file, 'w+').close()   # creat empty file to prevent error
    
    if logger is None:
        log.close()
    return

def get_all_clusters(input_path, embed_path, work_dir, skip=False, log_folder='log'):
    print('Clustering...')
    
    if not os.path.isdir(log_folder):
        os.mkdir(log_folder)
    log_file = os.path.join(log_folder, 'cluster.log')
    log = open(log_file, 'w+', encoding='utf-8')

    for model, embedding in embed_path.items():
        for n in range(5, 20+1, 5):
            get_clusters(input_path, embedding, work_dir, model, algorithm='kmean', n=n, skip=skip, logger=log, log_folder=None)
        get_clusters(input_path, embedding, work_dir, model, algorithm='ap', skip=skip, logger=log, log_folder=None)
    return

def get_groundtruth(embed_path, skip=False, logger=None, log_folder='log'):
    print('Extracting groundtruth...')
    if logger is None:
        if not os.path.isdir(log_folder):
            os.mkdir(log_folder)
        log_file = os.path.join(log_folder, 'getlabel.log')
        log = open(log_file, 'w+', encoding='utf-8')
    else:
        log = logger
    
    for query, embed_file in embed_path.items():
        if '_' in query and not skip:
            log.write(' '.join(['python', 'util/get_groundtruth.py', query, embed_file]) + '\n')
            call(['python', 'util/get_groundtruth.py', query, embed_file])
    log.close()
    return

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help="Where to find all files")
    parser.add_argument('model_dir', help="Where to find model configs")
    parser.add_argument('work_dir', nargs='?', default='work', help="Where to place output and temp files")
    parser.add_argument('log_dir', nargs='?', default='log', type=str, help="Where to store logs")
    bert_args = parser.add_argument_group('bert configuration', description='BERT configs. Model folder prefix is not needed.')
    bert_args.add_argument('-voc', '--voc_file', default='vocab.txt', help='tokenize vocabulary file')
    bert_args.add_argument('-cf', '--config_file', default='bert_config.json', help='model config file')
    bert_args.add_argument('-m', '--model_list', nargs='+', default=[0, 3000, 7000], choices=[0, 3000, 7000], type=int, help='checkpoint of which model to use')
    bert_args.add_argument('-l', '--layers', nargs='+', default=[-1], type=int, help='feature layer to use')
    bert_args.add_argument('-seq', '--max_seq_length', default=128, type=int, help='sequence length')
    bert_args.add_argument('-b', '--batch_size', default=16, type=int, help='inference batch size')
    flags = parser.add_argument_group('optional flags')
    flags.add_argument('-sp', '--skip_preprocess', action='store_true', help="skip data preprocessing (will cause error if files not exist)")
    flags.add_argument('-se', '--skip_embedding', action='store_true', help="skip data embedding (will cause error if files not exist)")
    flags.add_argument('-sg', '--skip_groundtruth', action='store_true', help="skip getting groundtruth")
    flags.add_argument('-sc', '--skip_clustering', action='store_true', help="skip data clustering (will cause error if files not exist)")
    flags.add_argument('-d', '--debug', action='store_true', help="debug mode")

    return parser.parse_args()

def main():
    args = parse_args()

    if not os.path.isdir(args.work_dir):
        os.mkdir(args.work_dir)
    if not os.path.isdir(args.log_dir):
        os.mkdir(args.log_dir)
    
    files = glob(os.path.join(args.input_dir, '*.json'))
    input_path = get_input_files(files, args.work_dir, skip=args.skip_preprocess, log_folder=args.log_dir)

    embed_path = get_all_embeddings(input_path, args.work_dir, log_folder=args.log_dir, 
                                    model_dir=args.model_dir, voc_path=args.voc_file, config_path=args.config_file, ckpt_prefix='model.ckpt-', 
                                    model_list=args.model_list, layers=args.layers, max_seq_length=args.max_seq_length, batch_size=args.batch_size, 
                                    skip=args.skip_embedding)

    get_groundtruth(next(iter(embed_path.values())), args.skip_groundtruth, logger=None, log_folder=args.log_dir)
    
    get_all_clusters(input_path, embed_path, args.work_dir, skip=args.skip_clustering, log_folder=args.log_dir)

if __name__=='__main__':
    main()
    