# Mines

マインスイーパーから着想を得た難解プログラミング言語。

## 概要

Minesはプログラムがマインスイーパーのゲームプレイを模した操作によって実行される言語である。

## プログラム記述仕様

Minesのプログラムは1つの盤面と1つの操作リストがこの順に改行区切りで記述されたものである。

**盤面**は `.` と `*` からなる長方形のグリッドで表される。
`.` は安全なマス、 `*` は地雷のあるマスを表す。

**操作リスト**は `\n` で区切られた1つ以上の操作からなる。

1つの**操作**は `,` または`;` で区切られた2つの整数、あるいは空行で表される。
盤面の直後及びファイル末尾に書かれた**空行**も操作として数えられる。

**2つの整数**は盤面の左上からの列及び行番号を表し、区切り文字はクリックするマウスボタンを指定する。
`,` は左クリック、 `;` は右クリックを指す。

**列及び行番号**は負数でも盤面の範囲外を指していても良い。
これらはそれぞれ盤面の幅ないし高さで割った非負剰余に変換される。

プログラム中に現れる半角空白及び `\t\r\f\v` の各文字は無視される。
また、`#` から行末までの文字列は無視される。
つまりプログラムは**コメント**を含むことができる。

以下に、幅4高さ3の盤面と4つの操作を持つプログラムの例とそれぞれの操作の意味を示す。

```
.*.* #This is a comment.
...*
.**.
0,0
-1, -1 #Spaces are ignored.

10;-10
```

| 操作 | 意味 |
----|----
| `0,0` | 左上のマスを左クリック |
| `-1,-1` | 右下のマスを左クリック（ `3,2` と同等） |
|  | 何もしない |
| `9;-10`| 左から(9 % 4)番目、上から(-10 % 3)番目のマスを右クリック（ `1;2` と同等） |

## プログラムの処理

Minesのインタプリタは1つの**操作ポインタ(OP)**を持ち、最初は操作リストの一番上を指している。
インタプリタは盤面に対してOPの指す操作を行い、その後OPを1つ進める。
一番下の操作が行われると、OPは一番上の命令に戻り、操作を続行する。

各操作が行われるごとに、その結果及びその操作が行われたマスの状態に応じて**命令**が選ばれ、実行される。

**ゲームオーバー**となる操作をした場合、プログラムは終了せず、盤面が初期状態（マスが空いておらず旗もない状態）に戻りゲームが再開される（OPは初期化されない）。

インタプリタは記憶領域として符号付き整数の**スタック**を1つ持ち、これは命令によって操作される。
スタックの初期状態は空であり、処理系の許す限り無限に値を持ち得る。

各命令の実行後、もしも「それぞれの安全なマス」または「それぞれの地雷マス」が全ゲームプレイを通じて1回以上開かれたことがあれば、プログラムは**終了**する（この挙動は通常のマインスイーパーにおけるゲームクリアと異なる）。

## 操作の振る舞い

**左クリック**はほとんどのマインスイーパーアプリにおけるそれと同じように振る舞う。

開かれていないマスに対する左クリックはそのマスを開ける。
もし地雷を開けばゲームオーバーとなる。

開かれたマスに対する左クリックは盤面に影響を及ぼさないが、何らかの命令が実行され得る。

**右クリック**も多くのマインスイーパーアプリにおけるそれと同じように振る舞う。

開かれていないマスに対する右クリックは旗を立てるか取り除く。

開かれたマスに対する右クリックは、もしマスに書かれた数字がその周囲に立っている旗の数と一致すれば、すべての開かれていない隣接するマスを開こうとする。
もし地雷を開こうとしていればゲームオーバーとなる。
この操作は「Chord」と呼ばれており、アプリによってはChordを長押しや他のマウスボタンに紐付けている場合がある。

いずれのクリックにおいても開かれたマスが空白の場合、その周囲のマスも再帰的に開かれる（旗が立っていた場合旗が取り除かれ開けられる）。

**空行**の操作では何も起こらない（OPは通常通り進む）。

## 命令

マスの数字「0」は空白マス、「9」は地雷マスを表す。

「プッシュ」「ポップ」などはすべてスタックに対する操作を指す。

命令中で最初にポップした値を「p0」、次にポップした値を「p1」とする。

### コマンドエラー

ポップ回数分の値がスタックになかったり0除算をしようとするなどして命令を正しく実行できないことを**コマンドエラー**と呼ぶ。
命令の実行中にコマンドエラーが発生しそうな場合、命令はなかったことにされ、OPが次に進む。
なお、ゲームオーバーはコマンドエラーではない。

ポップ回数が足りない場合以外のコマンドエラーの発生条件は以下の表に示す。

### 開いていないマスを左クリック

#### マスに旗が立っている場合

| 命令名 | ポップ回数 | マスの数字 | 内容 | エラー条件 |
----|----|----|----|----
| noop | 0 | どれでも（判明しないので） | 何もしない | - |

#### マスに旗が立っていない場合

| 命令名 | ポップ回数 | マスの数字 | 内容 | エラー条件 |
----|----|----|----|----
| push(count) | 0 | 0 | このクリックによって開かれたマスの個数（≧1）をスタックにプッシュ | - |
| push(n) | 0 | 1〜8 | マスに書かれた数字をプッシュ | - |
| reset(l) | 0 | 9 | 盤面を初期状態に戻してゲームを再開（スタック及びOPはリセットされない、このマスは開かれたことになる） | - |

### 開いていないマスを右クリック

| 命令名 | ポップ回数 | マスの数字 | 内容 | エラー条件 |
----|----|----|----|----
| swap | 2 | どれでも（判明しないので） | p0をプッシュしてp1をプッシュ | - |

### 開いているマスを左クリック

| 命令名 | ポップ回数 | マスの数字 | 内容 | エラー条件 |
----|----|----|----|----
| pop | 1 | 0 | ポップ | - |
| positive | 1 | 1 | p0が正であれば1、正でなければ0をプッシュ | - |
| dup | 1 | 2 | p0を2回プッシュ | - |
| add | 2 | 3 | (p1 + p0)をプッシュ | - |
| sub | 2 | 4 | (p1 - p0)をプッシュ | - |
| mul | 2 | 5 | (p1 * p0)をプッシュ | - |
| div | 2 | 6 | (p1 / p0)をプッシュ | 0除算 |
| mod | 2 | 7 | (p1 % p0)をプッシュ | 0除算 |
| perform(l) | 2 | 8 | 操作「`p1,p0`」を行う | - |

### 開いているマスを右クリック

#### 新たに1個以上マスが開こうとした場合

| 命令名 | ポップ回数 | 結果 | 内容 | エラー条件 |
----|----|----|----|----
| push(sum) | 0 | 続行 | このクリックによって開かれたマスに書かれた数字の合計をスタックにプッシュ | - |
| reset(r) | スタックの長さ | ゲームオーバー | 盤面及びスタックを初期状態に戻してゲームを再開（OPはリセットされない、どのマスも開かれたことにはならない） | - |

#### それ以外の場合
| 命令名 | ポップ回数 | マスの数字 | 内容 | エラー条件 |
----|----|----|----|----
| push(0) | 0 | 0 | 0をプッシュ | - |
| not | 1 | 1 | p0が0であれば1、0でなければ1をプッシュ | - |
| roll | 2 | 2 | スタックの深さp1までの値をp0回回転させる（詳しくは「rollの詳細」を参照） | p1の絶対値がスタックの長さを超える |
| in(n) | 0 | 3 | 標準入力の先頭から整数としてパースした値を1つ取りプッシュ | パースできない |
| in(c) | 0 | 4 | 標準入力から文字を1つ取りそのUnicode値をプッシュ | 入力が空 |
| out(n) | 1 | 5 | p0を標準出力に出力 | - |
| out(c) | 1 | 6 | Unicode値がp0である文字を標準出力に出力 | p0が有効なUnicode値でない |
| skip | 1 | 7 | OPにp0を加算する（オーバーフローした場合ループする） | - |
| perform(r) | 2 | 8 | 操作「`p1;p0`」を行う | - |

##### rollの詳細

p0, p1をポップした状態でスタックが `1, 2, 3, 4` の場合、深さ3までの値を1回回転させると `1, 4, 2, 3` のようにトップの値が下に埋め込まれる。

回転数が負の場合、例えば-1回転させると `1, 3, 4, 2` のように逆の操作が行われる。

深さが負の場合、例えば1回転させると `2, 3, 1, 4` のようにスタックのボトムから操作される。

## 実装例

こちら ([examples/](examples)) 。

## インタプリタの実行方法

通常はこのようにする。

```
$ python3 minesweeper.py examples/hello.mines
```

入力を取る場合は適宜 `echo` や `cat` を利用しても良い。

```
$ echo -n "meow" | python3 minesweeper.py examples/cat.mines
```

`-d` でデバッグモードを有効にする。

```
$ python3 minesweeper.py examples/hello.mines -d
```

デバッグモードが有効なとき、`f`, `s`, `c`でそれぞれ各コマンド実行後の盤面、スタック、実行されたコマンドを出力する。
また、`l`で指定した操作の回数を超えるとプログラムが強制終了される。

```
$ python3 minesweeper.py examples/hello.mines -dfscl 42
```

## 作者

- **[DNEK](https://github.com/dnek)**

### 関連する制作物

- [pietron](https://github.com/dnek/pietron) - 難解プログラミング言語PietのIDE。Minesの仕様はPietの影響を受けています。

- [UnambiSweeper](https://dnek.app/unambi) - 最後まで論理的に解けるマインスイーパーアプリ。AndroidとiOSに対応しています。

## ライセンス

このプロジェクトにはMITライセンスが供与されています。
詳細は[LICENSE](LICENSE) ファイルを参照してください。