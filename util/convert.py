import argparse
import json

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', nargs=1, type=str, metavar='input', help='json file with forced-ASCII content')
    parser.add_argument('output_file', nargs='?', default='result.txt', type=str, metavar='output' ,help='output path to write UTF-8 result')

    return parser.parse_args()
 
def main():
    args = parse_args()
    fin, fout = args.input_file[0], args.output_file
    
    with open(fin, "r", encoding='utf-8') as f:
        data = f.read().splitlines()

    results = []
    for line in data:
        result = {
            'title': line,
            'content': 'content'
        }
        results.append(result)

    output = {
        'result': results
    }

    out = open(fout, 'w+', encoding='utf-8')
    json.dump(output, out, ensure_ascii=False)
    out.close()

if __name__ == '__main__':
    main()