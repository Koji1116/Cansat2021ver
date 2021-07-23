# Other
## Other.py
- saveLog(path, *data): 引数で指定されたデータをログに書き込む関数  
	引数　：path、保存したいデータ（複数入力可）  
	戻り値：なし  
	  
	例えば、"log.txt"にdata1, data2を保存したい場合は  
		saveLog("log.txt", data1, data2)  
- fileName(f): 存在しないファイルパスを生成する関数  
	引数　：ベースファイル名、拡張子（"."はいらない)  
	戻り値：ファイルパス  
	  
	例えば、"log1.txt"、"log2.txt"というログが存在する場合、  
		f = fileName("log", "txt")  
	としたとき、fは"log3.txt"となる  	
- phaseCheck(path): フェーズ進行の確認  
	引数　：ファイルパス  
	戻り値：段階（0以上の整数）  
