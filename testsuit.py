from subprocess import call
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
        files_path[query] = output_file
    log.close
    return files_path


# command: `python extract_features.py --input_file=INPUT --output_file=OUTPUT --vocab_file=VOCFILE --bert_config_file=CONFIG --init_checkpoint=CHECKPOINT --layers=-1 --max_seq_length=INT --batch_size=INT`
def get_embeddings(input_path, work_dir, voc_path='model/vocab.txt', config_path='model/bert_config.json', ckpt='model/model.ckpt-0', layers=[-1, -2, -3, -4], max_seq_length=128, batch_size=8, skip=False, log_folder='log'):
    print('Getting embeddings...')

    if not os.path.isdir(log_folder):
        os.mkdir(log_folder)
    log_file = os.path.join(log_folder, 'embedding.log')
    
    arguments = []
    arguments.append('--vocab_file=' + voc_path)
    arguments.append('--bert_config_file=' + config_path)
    arguments.append('--init_checkpoint=' + ckpt)
    layers_str = ','.join([str(i) for i in layers])
    arguments.append('--layers=' + layers_str)
    arguments.append('--max_seq_length=' + str(max_seq_length))
    arguments.append('--batch_size=' + str(batch_size))

    output_path = {}
    log = open(log_file, 'w+', encoding='utf-8')
    for query, filepath in input_path.items():
        output_dir = os.path.join(work_dir, query)
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        output_file = os.path.join(output_dir, 'embedding.jsonl')

        print('  {}  -->  {}'.format(filepath, output_file))
        log.write('  {}  -->  {}\n'.format(filepath, output_file))
        
        if not skip:
            log.write(' '.join(['python', '-W ignore', 'extract_features.py', '--input_file=' + filepath, '--output_file=' + output_file] + arguments)+'\n')
            call(['python', '-W ignore', 'extract_features.py', '--input_file=' + filepath, '--output_file=' + output_file] + arguments)
        output_path[query] = output_file
    log.close()
    return output_path

def get_all_embeddings(input_path, work_dir, model_list, model_dir='model', config_path='bert_config.json', ckpt_prefix='model.ckpt-', layers=[-1, -2, -3, -4], max_seq_length=128, batch_size=8, skip=False, log_folder='log'):
    for model in model_list:
        ckpt = os.


def get_clusters(input_path, embed_path, work_dir, model, algorithm, n=None, skip=False, log_folder='log'):
    if not os.path.isdir(log_folder):
        os.mkdir(log_folder)
    log_file = os.path.join(log_folder, 'cluster.log')
    log = open(log_file, 'w+', encoding='utf-8')

    arguments = []
    filename = model
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
    log.close()
    return

def get_all_clusters(input_path, embed_path, work_dir, model, skip=False, log_folder='log'):
    print('Clustering...')
    for n in range(5, 20+1, 5):
        get_clusters(input_path, embed_path, work_dir, model, algorithm='kmean', n=n, skip=skip, log_folder=log_folder)
    get_clusters(input_path, embed_path, work_dir, model, algorithm='ap', skip=skip, log_folder=log_folder)
    return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help="Where to find all files")
    parser.add_argument('work_dir', nargs='?', default='work', help="Where to place output and temp files")
    parser.add_argument('-l', '--log_folder', nargs='?', default='log', type=str, help="log folder")
    parser.add_argument('-sp', '--skip_preprocess', action='store_true', help="skip data preprocessing (will cause error if files not exist)")
    parser.add_argument('-se', '--skip_embedding', action='store_true', help="skip data embedding (will cause error if files not exist)")
    parser.add_argument('-sc', '--skip_clustering', action='store_true', help="skip data clustering (will cause error if files not exist)")
    parser.add_argument('-d', '--debug', action='store_true', help="debug mode")
    args = parser.parse_args()

    if not os.path.isdir(args.work_dir):
        os.mkdir(args.work_dir)
    if not os.path.isdir(args.log_folder):
        os.mkdir(args.log_folder)
    
    files = glob(os.path.join(args.input_dir, '*.json'))
    input_path = get_input_files(files, args.work_dir, skip=args.skip_preprocess, log_folder=args.log_folder)
    embed_path = get_embeddings(input_path, args.work_dir, layers=[-1], skip=args.skip_embedding, log_folder=args.log_folder)
    # get_clusters(input_path, embed_path, args.work_dir, 'ap', skip=args.skip_clustering, log_folder=args.log_folder)
    get_all_clusters(input_path, embed_path, args.work_dir, 'base', skip=args.skip_clustering, log_folder=args.log_folder)

if __name__=='__main__':
    main()