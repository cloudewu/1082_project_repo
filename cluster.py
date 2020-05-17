import json
import numpy as np

def get_input(news_path, embed_path, debugging=False):

    with open(news_path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')[:-1]    # abandon empty string
    
    news_dict = {}
    for idx, line in enumerate(lines):
        title, content = line.split('\t')
        news_dict[idx] = {}
        news_dict[idx]['title'] = title
        news_dict[idx]['content'] = content
    
    with open(embed_path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')[:-1]    # abandon empty string
    
    if debugging:
        debug = open('output/temp.debug', 'w+', encoding='utf-8')
    features = []
    for idx, line in enumerate(lines):
        data = json.loads(line)
        word_embedding = []
        sent = ''
        for word in data['features']:
            if word['token'] == '[CLS]':
                for layer in word['layers']:
                    word_embedding.append(layer['values'])
            elif word['token'] != '[SEP]':
                sent += word['token']
        word_embedding = np.sum(word_embedding, axis=0)
        features.append(word_embedding)
        news_dict[idx]['embedding'] = word_embedding.tolist()

        if debugging:
            debug.write(sent+'\n')
            debug.write(news_dict[idx]['title']+'\t'+news_dict[idx]['content']+'\n')
            debug.write(str(word_embedding.tolist())+'\n')
    
    features = np.vstack([news['embedding'] for news in news_dict.values()])
    if debugging:
        debug.close()

    return news_dict, features

def cluster_news(news, features, alg, n=None):
    print('[ INFO ] start clustering...')
    if alg.lower() == 'kmean':
        from sklearn.cluster import KMeans
        kmean = KMeans(n)
        kmean.fit(features)
        labels = kmean.labels_
        n_cluster = n
    elif alg.lower() in ['affinitypropagation', 'ap']:
        from sklearn.cluster import AffinityPropagation
        ap = AffinityPropagation(random_state=None)
        ap.fit(features)
        labels = ap.labels_
        n_cluster = max(labels) + 1
    else :
        print('[ ERROR ] Algorithm not supported.')
        return [[]]

    clusters = [[] for i in range(n_cluster)]
    for idx, cluster_id in enumerate(labels):
        clusters[cluster_id].append(news[idx])
    return clusters

def dump_json(clusters, outputfile):
    output_dict = {}
    output_dict['result'] = clusters

    print('[ INFO ] save reault in {}...'.format(outputfile))
    with open(outputfile, "w+", encoding='utf-8') as output:
        json.dump(output_dict, output, ensure_ascii=False)
    return 

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('news', type=str, help='News data file. One new, one line. Sep title and content with tab')
    parser.add_argument('embedding', type=str, help='BERT output embedding file')
    parser.add_argument('output', type=str, default='result.json', help='clustering output file')
    parser.add_argument('-alg', '--algorithm', type=str, default='KMean', help='Clustering algorithm')
    parser.add_argument('-n', type=int, default=5, help='clustering groupt count (available for KMean)')
    parser.add_argument('-d', '--debug', action='store_true', help='debug mode')
    args = parser.parse_args()

    news, features = get_input(args.news, args.embedding, debugging=args.debug)
    clusters = cluster_news(news, features, args.algorithm, n=args.n)
    dump_json = dump_json(clusters, args.output)
