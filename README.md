Data
-------------
檔案儲存區
 * `.json`: colab載下來的原始檔
 * `.txt`: 用extract.py處理過的純文字檔

extract.py
-------------
讀取從COLAB下直接載下來的.json檔，並抓取出乾淨的news content。  
不下-p則會取得原始新聞內容（稍微加了分行增進易讀性）  
多下-p或--preprocess參數可以取得**能直接餵進BERT/create_pretraining_data.py的raw檔案**，此檔案會經過經過一些前處理：  
 * 移除'...'
 * 移除原始顯示用換行，並利用\[：；。？！\.\]符號重新進行有意義斷行
 * 刪減多餘空白
也可自行到`preprocess()`中定義前處理流程  

**Usage**:  
```
usage: extract.py [-h] [-p] input [output]

positional arguments:
  input             json file contain news titles and contents
  output            output path to write counting result

optional arguments:
  -h, --help        show this help message and exit
  -p, --preprocess  Preprocess data into BERT-frendly format
```

workspace.ipynb
-------------
工作檔，內有brute-force/ckiptagger完整處理流程與中間檔的展示  

**Notes: **  
要跑brute-force的話不需dependency，  
但要跑後半段ckiptagger的code需先install [ckiptagger](https://github.com/ckiplab/ckiptagger) package,   
並且根據repo內的readme下載WS需要的model後才能run起來 

process.py
-------------
workspace的打包檔，input直接丟進去可以一次性分析json並輸出ngram count  
**Usage:**  
```
usage: process.py [-h] input [output]

positional arguments:
  input       json file contain news titles and contents
  output      output path to write counting result

optional arguments:
  -h, --help  show this help message and exit
```

convert.py
-------------
將force-ASCII的json檔案轉換為UTF-8顯示json檔  
**Usage:**  
```
usage: convert.py [-h] input [output]

positional arguments:
  input       json file with forced-ASCII content
  output      output path to write UTF-8 result

optional arguments:
  -h, --help  show this help message and exit
```