from subprocess import call
from glob import glob
import os
import argparse

def get_input_files(files, work_dir, skip=False, log_folder='log'):
    print('Preprocessing news files...')

    output_dir = os.path.join(work_dir, 'inputs')
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    if not os.path.isdir(log_folder):
        os.mkdir(log_folder)
    log_file = os.path.join(log_folder, 'preprocess.log')
    log = open(log_file, 'w+', encoding='utf-8')
    
    files_path = {}
    for filename in files:
        basename = os.path.basename(filename).split('.')[0]
        output_file = os.path.join(output_dir, basename+'.txt')
        print('  {}  -->  {}'.format(filename, output_file))
        log.write('{}  -->  {}\n'.format(filename, output_file))

        if not skip:
            call(['python', 'util/extract.py', '-o', filename, output_file])
        files_path[basename] = output_file
    log.close
    return files_path


# command: `python extract_features.py --input_file=INPUT --output_file=OUTPUT --vocab_file=VOCFILE --bert_config_file=CONFIG --init_checkpoint=CHECKPOINT --layers=-1 --max_seq_length=INT --batch_size=INT`
def get_embeddings(input_path, work_dir, voc_path='model/vocab.txt', config_path='model/bert_config.json', checkpoint='model/model.ckpt-0', layers=[-1, -2, -3, -4], max_seq_length=128, batch_size=8, skip=False, log_folder='log'):
    print('Getting embeddings...')

    output_dir = os.path.join(work_dir, 'embeddings')
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    if not os.path.isdir(log_folder):
        os.mkdir(log_folder)
    log_file = os.path.join(log_folder, 'embedding.log')
    
    arguments = []
    arguments.append('--vocab_file=' + voc_path)
    arguments.append('--bert_config_file=' + config_path)
    arguments.append('--init_checkpoint=' + checkpoint)
    layers_str = ','.join([str(i) for i in layers])
    arguments.append('--layers=' + layers_str)
    arguments.append('--max_seq_length=' + str(max_seq_length))
    arguments.append('--batch_size=' + str(batch_size))

    output_path = {}
    log = open(log_file, 'w+', encoding='utf-8')
    for filename, filepath in input_path.items():
        output_file = os.path.join(output_dir, filename+'.jsonl')
        print('  {}  -->  {}'.format(filepath, output_file))
        log.write('{}  -->  {}\n'.format(filename, output_file))
        log.write('python extract_features.py --input_file='+filepath+'--output_file='+output_file+' '.join(arguments)+'\n')
        
        if not skip:
            call(['python', 'extract_features.py', '--input_file=' + filepath, '--output_file=' + output_file] + arguments)
        output_path[filename] = output_file
    log.close()
    return output_path


def get_clusters(input_path, embed_path, work_dir, algorithm, skip=False, log_folder='log'):
    output_dir = os.path.join(work_dir, 'cluster')
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    if not os.path.isdir(log_folder):
        os.mkdir(log_folder)
    log_file = os.path.join(log_folder, 'cluster.log')

    log = open(log_file, 'w+', encoding='utf-8')
    for filename, input_file in input_path.items():
        embed_file = embed_path[filename]
        output_file = os.path.join(output_dir, filename+'.json')
        print('  {}, {}  -->  {}'.format(input_file, embed_file, output_file))
        log.write('{}, {}  -->  {}\n'.format(input_file, embed_file, output_file))
        if not skip:
            call(['python', '-W ignore', 'cluster.py', input_file, embed_file, output_file, '--algorithm='+algorithm])
    log.close()
    return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help="Where to find all files")
    parser.add_argument('work_dir', nargs='?', default='work', help="Where to place output and temp files")
    parser.add_argument('-l', '--log_folder', nargs='?', default='log', type=str, help="log folder")
    parser.add_argument('-sp', '--skip_preprocess', action='store_true', help="skip data preprocessing (will cause error if files not exist)")
    parser.add_argument('-se', '--skip_embedding', action='store_true', help="skip data embedding (will cause error if files not exist)")
    parser.add_argument('-d', '--debug', action='store_true', help="debug mode")
    args = parser.parse_args()

    if not os.path.isdir(args.work_dir):
        os.mkdir(args.work_dir)
    if not os.path.isdir(args.log_folder):
        os.mkdir(args.log_folder)
    
    files = glob(os.path.join(args.input_dir, '*.json'))
    input_path = get_input_files(files, args.work_dir, skip=args.skip_preprocess, log_folder='work\log')
    embed_path = get_embeddings(input_path, args.work_dir, layers=[-1], skip=args.skip_embedding, log_folder='work\log')
    get_clusters(input_path, embed_path, args.work_dir, 'ap')

if __name__=='__main__':
    main()