import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
import tempfile
from datetime import datetime, timedelta

import matplotlib
matplotlib.use('TkAgg')  # バックエンドをTkAggに設定する


def plot_eMaxiSlim_from_csv_url(csv_url, web_url):
    """
    指定されたCSV URLからeMaxi Slimのデータをダウンロードし、
    短期および長期移動平均の乖離をプロットします。

    eMiaxiSlim の CSVデータ は以下で公開されています
    https://emaxis.am.mufg.jp/lp/slim/pr1/

    Args:
    csv_url (str): データのCSVファイルのURL。
    web_url (str): 参照元のウェブページのURL。
    """

    # 短期移動平均の日数パターン1
    SMA_PATTERN_1 = 20
    # 短期移動平均の日数パターン2
    SMA_PATTERN_2 = 50
    # 長期移動平均の日数パターン1
    LMA_PATTERN_1 = 100
    # 長期移動平均の日数パターン2
    LMA_PATTERN_2 = 200

    # エンコード
    EMAXI_SLIM_ENCODE='cp932'

    # テンポラリファイルを作成
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        # CSVファイルをダウンロード
        response = requests.get(csv_url)

        # テンポラリファイルに内容を書き込む
        tmp_file.write(response.content)
        
        # ファイルパスを保持
        tmp_file_path = tmp_file.name

    print(f'テンポラリファイル:{tmp_file_path}')

    # ファイルを開いて1行目を読み取る
    with open(tmp_file_path, 'r', encoding=EMAXI_SLIM_ENCODE) as file:
        asset_name = file.readline().strip()  # 改行文字を削除するためにstrip()を使用

    # ダウンロードしたCSVファイルをDataFrameとして読み込み
    # CSVファイルの読み込み時に最初の行を無視し、2行目をヘッダーとして使用
    df = pd.read_csv(tmp_file_path, header=1, encoding=EMAXI_SLIM_ENCODE)

    # ｅＭＡＸＩＳ Ｓｌｉｍ 米国株式（Ｓ＆Ｐ５００）
    # 基準日,基準価額(円),基準価額（分配金再投資）(円),分配金（税引前）(円),純資産総額（億円）
    # 2018/07/03,10038,10038,,0.01
    # 2018/07/04,9936,9936,,0.01
    # 2018/07/05,9942,9942,,1.05
    # 2018/07/06,10057,10057,,1.06

    # 移動平均の計算
    df['SMA_1'] = df['基準価額(円)'].rolling(window=SMA_PATTERN_1).mean()
    df['SMA_2'] = df['基準価額(円)'].rolling(window=SMA_PATTERN_2).mean()
    df['LMA_1'] = df['基準価額(円)'].rolling(window=LMA_PATTERN_1).mean()
    df['LMA_2'] = df['基準価額(円)'].rolling(window=LMA_PATTERN_2).mean()

    # 乖離の計算（基準価額 - 移動平均）
    df['Divergence_SMA_1'] = df['SMA_1'] - df['基準価額(円)']
    df['Divergence_SMA_2'] = df['SMA_2'] - df['基準価額(円)']
    df['Divergence_LMA_1'] = df['LMA_1'] - df['基準価額(円)']
    df['Divergence_LMA_2'] = df['LMA_2'] - df['基準価額(円)']

    # '基準日'列を日付の形式に変換
    df['基準日'] = pd.to_datetime(df['基準日'])
    # 各年の最初の日付のインデックスを取得
    first_day_indices = df.groupby(df['基準日'].dt.year)['基準日'].idxmin()
    # 各年の最初の日付のデータのみを抽出
    df_year_starts = df.loc[first_day_indices]

    # 日本語を表示できるフォントに設定
    plt.rcParams['font.family'] = 'Meiryo'

    # 乖離のグラフ化
    plt.figure(figsize=(14, 6))

    plt.plot(df.index, df['Divergence_SMA_1'], label=f'{SMA_PATTERN_1}日移動平均 - 基準価額', color='orange')
    plt.plot(df.index, df['Divergence_SMA_2'], label=f'{SMA_PATTERN_2}日移動平均 - 基準価額', color=(0.5, 0, 0.0, 0.5))
    plt.plot(df.index, df['Divergence_LMA_1'], label=f'{LMA_PATTERN_1}日移動平均 - 基準価額', color='gray', linewidth=1)
    plt.plot(df.index, df['Divergence_LMA_2'], label=f'{LMA_PATTERN_2}日移動平均 - 基準価額', color=(0.7, 0.7, 0.7), linewidth=1)

    plt.axhline(y=0, color='blue', linestyle='-')  # 乖離が0の基準線

    # x軸のラベルと位置を設定
    plt.xticks(df_year_starts.index, df_year_starts['基準日'].dt.strftime('%Y'))

    plt.title(f'{asset_name} 基準価額と移動平均の乖離')
    plt.xlabel('日付')
    plt.ylabel('乖離', rotation='vertical')
    plt.legend()

    # 引用元をプロットに追加
    url_text = f"データ引用元:{asset_name} ({web_url})"
    plt.text(0.5, -0.12, url_text, ha='center', va='center', transform=plt.gca().transAxes, fontsize=8, color='gray')

    plt.show()

