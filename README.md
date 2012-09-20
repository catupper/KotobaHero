KotobaHero
==========

Japanese Word Hero

使用言語:
  python

動作環境:
  python2.x系 pygameが使えること

起動方法:
  python で WordHero_jp.pyを実行。もしくは、KotobaHero（実行ファイル、シェルスクリプト）を実行。

遊び方:
  マウスでクリックしながら文字をなぞる。
  単語ができたらうれしい。


辞書:
  辞書ファイルはdictionary/mydicth
  中身は一行に一単語をひらがなで。
  使えるひらがなは「ゐゑをーゃゅょゎぁぃぅぇぉっ」を除くすべてのひらがな。
  上記のひらがなについては小さいものは大きくし、「ゐゑを」は「いえお」で代用。
  長音は直前の文字の母音を使うようにしている。
  euc_jpでエンコード。
  
  
定数:
  WordHero_jp.py内の書き換えれる定数と意味。
  WIDTH : ウィンドウの幅
  HEIGHT :　ウィンドウの高さ
  BOARD_SIZE : 文字盤（4*4）の大きさ。ひとつのひらがなの大きさではない。  
  PLAY_TIME : 制限時間
  SCORE_TIME : 単語、スコア表示の時間
  LEAST_LEN : 単語の最低文字数
  LONGEST_LEN : すくなくともひとつはこれ以上の長さの単語がある
  LEAST_BONUS : 各ひらがなが使われる回数の下限
　その他色 : RGBのタプルで表現。
　