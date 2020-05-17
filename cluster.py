import json
import numpy as np
# from sklearn.cluster import AffinityPropagation

def get_input(news_path, embed_path):

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
    
    features = []
    for idx, line in enumerate(lines):
        data = json.loads(line)
        word_embedding = []
        for word in data['features']:
            if word['token'] == '[CLS]':
                for layer in word['layers']:
                    word_embedding.append(layer['values'])
        word_embedding = np.sum(word_embedding, axis=0)
        features.append(word_embedding)
        news_dict[idx]['embedding'] = word_embedding.tolist()
    features = np.vstack([news['embedding'] for news in news_dict.values()])

    return news_dict, features

def cluster_news(news, features, n):
    print('[ INFO ] start clustering...')

    from sklearn.cluster import KMeans
    kmean = KMeans(n)
    kmean.fit(features)

    clusters = [[] for i in range(n)]
    for idx, cluster_id in enumerate(kmean.labels_):
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
    parser.add_argument('-n', type=int, default=5, help='clustering groupt count')
    args = parser.parse_args()

    news, features = get_input(args.news, args.embedding)
    clusters = cluster_news(news, features, args.n)
    dump_json = dump_json(clusters, args.output)

# clusters_arr = []
# for i, cluster in enumerate(clusters):
#     news_info = []
#     for sent_id, emb in cluster:
#         info = {}
#         info['title'] = news[sent_id][0]
#         info['content'] = news[sent_id][1]
#         info['embedding'] = emb.tolist()

#         news_info.append(info)
#     clusters_arr.append(news_info)
# d = {}
# d['result'] = clusters_arr

# outputfile = 'output/cluster_title.txt'

        # output.write("Cluster {}\n".format(i+1))
        # for sentence in cluster:
        #     output.write('\t'+sentence+'\n')
        # output.write("-------\n\n")

# clustering = AffinityPropagation(random_state=5).fit(features)
