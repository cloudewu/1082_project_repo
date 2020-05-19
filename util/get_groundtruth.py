from collections import defaultdict
import json

def get_groundtruth(query, embed_path, debugging=False):
    with open(embed_path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')[:-1]    # abandon empty string
    
    keywords = query.replace('|','_').split('_')

    if debugging:
        print('Labels: ')
        for i, w in enumerate(keywords):
            print('\t', i, w)
        print()
    
    info = defaultdict(list)
    for news_idx, line in enumerate(lines):
        data = json.loads(line)
        content = ''
        for word in data['features']:
            if word['token'] not in ['[CLS]', '[SEP]']:
                content += word['token']
        
        for label, keyword in enumerate(keywords):
            if keyword in content:
                info[news_idx].append(label)

        if debugging:
            print(content, str(info[news_idx]))
    return info

if __name__=='__main__':
    import os
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('query', help="Search engine input")
    parser.add_argument('input_file', help="news embedding file")
    parser.add_argument('output_file', nargs='?', help="output location")
    parser.add_argument('-d', '--debug', action='store_true', help="debug mode")
    args = parser.parse_args()

    labels = get_groundtruth(args.query, args.input_file, debugging=args.debug)
    if args.output_file is None:
        dirname = os.path.dirname(args.input_file)
        outputfile = os.path.join(dirname, 'groundtruth.json')
        if args.debug:
            print(f'[ DEBUG ] output folder: {dirname}; output file: {outputfile}')
    else:
        outputfile = args.output_file

    with open(outputfile, "w+", encoding='utf-8') as output:
        json.dump(labels, output, ensure_ascii=False)