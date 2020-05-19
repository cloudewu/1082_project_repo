**All bert training code is from [Google Research Github](https://github.com/google-research/bert)! Thanks google. :)**
 * [Model files](https://drive.google.com/open?id=1-5iqhd5JUcMoZ5cDcYRtCXJHvJKPuJHM)

Testsuit用法
=============
用以直接讀取資料夾input，並產生每個query的embedding與cluster結果  
```
usage: testsuit.py [-h] [-voc VOC_FILE] [-cf CONFIG_FILE]        
                   [-m {0,3000,7000} [{0,3000,7000} ...]]        
                   [-l LAYERS [LAYERS ...]] [-seq MAX_SEQ_LENGTH]
                   [-b BATCH_SIZE] [-sp] [-se] [-sg] [-sc] [-d]  
                   input_dir model_dir [work_dir] [log_dir]

positional arguments:
  input_dir             Where to find all files
  model_dir             Where to find model configs
  work_dir              Where to place output and temp files
  log_dir               Where to store logs
```
範例：  
1. 使用model/下的設定處理data/0519內的json資料:
    `python testsuit.py data/0519 model/`
2. 指定output與log位置到work/和work/log:
    `python testsuit.py data/0519 model/ work work/log`
3. 利用-sp, -se, -sg, -sc可跳過資料preprocessing、embedding、抓groundtruth或cluster動作，可用來重跑特定步驟
4. 可利用`python testsuit.py data/0519 model/ work -sp -se -sg -sc`快速檢視output資料夾結構
5. 更多參數相關說明請參考`python testsuit.py -h`


Cluster處理流程
=============
1. 下載[Model files](https://drive.google.com/open?id=1-5iqhd5JUcMoZ5cDcYRtCXJHvJKPuJHM)（5/15-16 fine-tune檔案）
2. 利用`python util/extract.py --oneline`製作input.txt
3. 把input檔餵進`extract_features.py`取得embedding.jsonl (max_seq可進行調整，為了把content吃進去我都下128)
4. `python cluster.py input.txt embedding.jsonl output.json --alg=<kmean|ap>`取得分群資料


Bert pretrain流程
=============
1. 下載pretrain檔
2. 將data進行前處理（參照[util/extract.py](#extractpy)）
3. 製作input data，ref: [Bert/create_pretraining_data.py](https://github.com/google-research/bert#pre-training-with-bert)  
max_seq_length跟batch_size視自己machine的能力進行調整
```
python create_pretraining_data.py --input_file=<input> --output_file=<out>.tfrecord --vocab_file=<bert_model>\vocab.txt --do_lower_case=False --max_seq_length=<int>
```
4. 丟進Bert進行pretrain，ref同上  
max_seq_length跟batch_size一樣視自己machine的能力進行調整  
建議Step先調小進行debug再正式開train
```
python run_pretraining.py --input_file=data\<input>.tfrecord --output_dir=<out> --do_train=True --do_eval=True --bert_config_file=<model>\bert_config.json --init_checkpoint=<model>\bert_model.ckpt --train_batch_size=<int> --max_seq_length=<int> --num_train_steps=<int> --num_warmup_steps=<int>
```

`data/` and `util/`
=============

Data
-------------
檔案儲存區
 * `.json`: colab載下來的原始檔
 * `.txt`: 用extract.py處理過的純文字檔

util/extract.py
-------------
讀取從COLAB下直接載下來的.json檔，並抓取出乾淨的news content。  
不下-p則會取得原始新聞內容（稍微加了分行增進易讀性）  
多下-p或--preprocess參數可以取得**能直接餵進BERT/create_pretraining_data.py的raw檔案**，此檔案會經過經過一些前處理：  
 * 移除'...'
 * 移除原始顯示用換行，並利用\[：；。？！\.\]符號重新進行有意義斷行
 * 刪減多餘空白
也可自行到`preprocess()`中定義前處理流程  
```
usage: extract.py [-h] [-to] [-o] [-p] input [output]

positional arguments:
  input             json file contain news titles and contents
  output            output path to write counting result

optional arguments:
  -h, --help        show this help message and exit
  -to, --titleonly  Ouput news title only
  -o, --oneline     Ouput one result in one line, seperate title and content
                    with tab
  -p, --preprocess  Preprocess data into BERT-frendly pretrained format
```

util\get_groundtruth.py
-------------
讀取複數關鍵字的embedding，並自動分析Ground該news的群組。  
用法： `python get_groundtruth.py 川普_林志玲 embedding.jsonl`  
```
usage: get_groundtruth.py [-h] [-d] query input_file [output_file]

positional arguments:
  query        Search engine input
  input_file   news embedding file
  output_file  output location

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  debug mode
```


util/workspace.ipynb
-------------
工作檔，內有brute-force/ckiptagger完整處理流程與中間檔的展示  
**Notes**  
要跑brute-force的話不需dependency，  
但要跑後半段ckiptagger的code需先install [ckiptagger](https://github.com/ckiplab/ckiptagger) package,   
並且根據repo內的readme下載WS需要的model後才能run起來 

util/process.py
-------------
workspace的打包檔，input直接丟進去可以一次性分析json並輸出ngram count  
```
usage: process.py [-h] input [output]

positional arguments:
  input       json file contain news titles and contents
  output      output path to write counting result

optional arguments:
  -h, --help  show this help message and exit
```

util/convert.py
-------------
將force-ASCII的json檔案轉換為UTF-8顯示json檔  
```
usage: convert.py [-h] input [output]

positional arguments:
  input       json file with forced-ASCII content
  output      output path to write UTF-8 result

optional arguments:
  -h, --help  show this help message and exit
```
