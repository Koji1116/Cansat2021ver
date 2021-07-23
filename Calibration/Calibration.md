# キャリブレーションについて
・九軸センサに搭載されている地磁気センサのずれを調整するために行う操作。<br> 
・マイコンを含めて周囲に磁気を発生させる機器が存在するとずれが起きてしまう。<br> 

・詳細は下記のサイトを参照<br> 
⇒・[ロボティクスにおける地磁気センサの基礎知識](https://myenigma.hatenablog.com/entry/2016/04/10/211919)<br> 
⇒・[磁気センサーの較正一般 (calibration general)](https://www.aichi-mi.com/home/%E9%9B%BB%E5%AD%90%E3%82%B3%E3%83%B3%E3%83%91%E3%82%B9/%E7%A3%81%E6%B0%97%E3%82%BB%E3%83%B3%E3%82%B5%E3%83%BC%E3%81%AE%E8%BC%83%E6%AD%A3%E4%B8%80%E8%88%AC/)

***

# プログラム概要
## calibration.py
・キャリブレーションを行うプログラム

***

# 関数一覧
## ● get_data
九軸センサから加速度センサと地磁気センサの値を読み取るプログラム
### 引数
・なし
### 返り値
・magx , magy , magz : 地磁気センサのx,y,z軸成分 <br> 
・accx , accy , accz : 加速度センサのx,y,z軸成分 <br> 

***

## ● magdata_matrix
x,y,z成分を分けるためにデータを分けるために多次元(n×3)行列にする
### 引数
・なし
### 返り値
・magdata : 地磁気センサの多次元行列 <br>  

***

## ● calculate_offset
オフセット値を計算する
### 引数
・magdata : 地磁気センサの多次元行列。magdata_matrixの戻り値。
### 返り値
・magx_array , magy_array , magz_array : 地磁気センサのx,y,z軸成分をそれぞれ独立した行列に直したもの<br> 
・magx_off , magy_off , magz_off : オフセット値のx,y,z軸成分　<br>  

***

## ● plot_data_2D
地磁気センサから得たデータをxy座標に図示する
### 引数
・magx_array , magy_array : 地磁気センサのx,y軸成分をそれぞれ独立した行列に直したもの。calculate_offsetの戻り値。
### 返り値
・なし

***

## ● plot_data_3D
地磁気センサから得たデータをxyz座標に図示する
### 引数
・magx_array , magy_array , magz_array : calculate_offsetの戻り値 
### 返り値
・なし

***

## ● calculate_angle_2D
地磁気センサが向いている方向が北から何度ずれているかを計算する。z軸方向に九軸センサを動かさなかった場合のみ有効。
### 引数
・magx,magy : 地磁気センサのx,y軸成分。get_dataの戻り値。 <br> 
・magx_off,magy_off : オフセット値のx,y軸成分。calculate_offsetの戻り値。
### 返り値
・θ : 地磁気センサが向いている方向が北から何度ずれているかを角度(degree)で表したもの。

***

## ● calculate_angle_3D
地磁気センサが向いている方向が北から何度ずれているかを計算する。z軸方向に九軸センサを動かした場合にも有効。<br> 
加速度センサの値も必要となる。
### 引数
・accx,accy,accz : 加速度センサのx,y,z軸成分。get_dataの戻り値。 <br> 
・magx,magy,magz : 地磁気センサのx,y,z軸成分。get_dataの戻り値。。 <br> 
・magx_off,magy_off,magz_off : オフセット値のx,y,z軸成分。calculate_offsetの戻り値。 <br> 
### 返り値
・θ : 地磁気センサが向いている方向が北から何度ずれているかを角度(degree)で表したもの

***

## ● calculate_direction
ゴールの座標までの角度(方位角)や距離を求める。<br> 
gps_navigate.py(path : Detection/Run_phase)を用いて計算している。
### 引数
・lon2,lat2 : ゴールの緯度、経度。自由に設定できる。
### 返り値
・direction : gps_navigate.pyの返り値と同じ。ゴールまでの距離、方位角がわかる。辞書型なので注意。

***

## ● rotate_control
ローバーをゴール方向に向かせる
### 引数
・θ : 地磁気センサが向いている方向が北から何度ずれているかを角度(degree)で表したもの。calculate_angle_2D(3D)の戻り値 <br> 
・lon2,lat2 : ゴールの緯度、経度。自由に設定できる。
### 返り値
・なし

***

## ●timer
並列処理をすることで「x秒間プログラムを実行する」ことが可能。
### 引数
・t : 実行したい時間を自由に定義できる
### 返り値
・なし
### 使い方
```
    global cond
    cond = True
    thread = Thread(target = timer,args=([t])) #tに任意の数を入れることで実行した時間を決められる。
    thread.start()
    while cond:
        処理したいプログラム
```
