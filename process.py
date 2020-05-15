import argparse

# data processing #
def load_json(path):
    import json
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

'''
@param path: input data path
@return (titles, contents): list of all titles and contents
'''
def get_data(path):
    data = load_json(path)['result']
    titles = [news['title'] for news in data]
    contents = [news['content'] for news in data]

    return titles, contents

'''
Write counter value to file
'''
def write_counter(counter, filename):
    with open(filename, 'w+', encoding='utf-8') as f:
        N = sum(counter.values())
        for word, count in counter.most_common():
            f.write('{}\t{}\t{:7.4f}%\n'.format(word, count, count/N*100))

# utility functions #
'''
Filter out punctuations from text
@param seg: list of word segment
'''
def filter_punc(seg):
    import re
    return [w for w in seg if re.sub(r'[^\w]', '', w) != '']

'''
@param sentences: double-iterable list of gram or words. (ex. [['I', 'like', 'potatoes'], ['She', 'is', 'beautiful']] or [['我喜歡晴天'], ['蛋餅很好吃']])
'''
def ngram(sentences, n):
    grams = []
    for sent in sentences:
        grams.extend([sent[i:i+n] for i in range(len(sent)-n+1)])
    return grams

'''
get a collection of combinations from 2gram to ngram
'''
def get_all_gram(sentences, n):
    grams = [w for sent in sentences for w in sent]
    for i in range(2, n+1):
        grams += [''.join(gram) for gram in ngram(sentences, i)]
    return grams

# main #
def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', nargs=1, type=str, metavar='input', help='json file contain news titles and contents')
    parser.add_argument('output_file', nargs='?', default='result.out', type=str, metavar='output' ,help='output path to write counting result')
    args = parser.parse_args()

    return args.input_file[0], args.output_file

def count(in_file, out_file):
    from ckiptagger import WS
    from collections import Counter

    titles, contents = get_data(in_file)
    assert len(titles) == len(contents)
    corpus = [' '.join((titles[i], contents[i])) for i in range(len(titles))]

    ws = WS('./data')
    word_seg = [filter_punc(sent) for sent in ws(corpus)]
    allgram = get_all_gram(word_seg, 3)
    counter = Counter(allgram)
    
    write_counter(counter, out_file)

if __name__=='__main__':
    fin, fout = parse_arg()
    count(fin, fout)
