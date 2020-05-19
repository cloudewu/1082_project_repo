# This file load news json data and extract titles and content to readable format #

import argparse
import json

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', nargs=1, type=str, metavar='input', help='json file contain news titles and contents')
    parser.add_argument('output_file', nargs='?', default='result.txt', type=str, metavar='output' ,help='output path to write counting result')
    parser.add_argument('-to', '--titleonly', action='store_true', help='Ouput news title only')
    parser.add_argument('-i', '--index', action='store_true', help='Add news unique index number')
    parser.add_argument('-o', '--oneline', action='store_true', help='Ouput one result in one line, seperate title and content with tab')
    parser.add_argument('-p', '--preprocess', action='store_true', help='Preprocess data into BERT-frendly pretrained format')

    return parser.parse_args()

def preprocess(content):
    import re
    # remove '\n' and '...'
    s = re.sub(r"(\n)|(\.{3})", "", content)
    # seperate lines with punc detection
    s = re.sub(r"([：；。？！\.])(.)", r"\1\n\2", s)
    # strip spaces
    s = re.sub(r"[ ]+", " ", s).strip()
    s = re.sub(r"( )*(\n)+( )*", r"\n", s)
    return s

if __name__ == '__main__':
    args = parse_args()
    fin, fout = args.input_file[0], args.output_file
    with open(fin, 'r', encoding='utf-8') as f:
        data = json.load(f)['result']
        
    with open(fout, 'w+', encoding='utf-8') as f:
        for idx, news in enumerate(data):
            if args.index:
                f.write('{}\t'.format(idx))
            
            if args.titleonly:
                f.write('{}\n'.format(news['title']))
            elif args.oneline:
                content = preprocess(news['content']).replace('\n', '').replace('\t', ' ')
                f.write('{}\t{}\n'.format(news['title'], content))
            elif args.preprocess:
                f.write('{}\n'.format(news['title']))
                f.write('{}\n\n'.format(preprocess(news['content'])))
            else:
                f.write('{}\n-\n{}\n'.format(news['title'], news['content']))
                f.write('-------------\n\n')