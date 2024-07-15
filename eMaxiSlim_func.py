import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
import tempfile
from plot_func import plot_cross_point

# import matplotlib
# matplotlib.use('TkAgg')  # バックエンドをTkAggに設定する


def plot_eMaxiSlim_from_csv_url(csv_url, web_url):
    """
    指定されたCSV URLからeMaxi Slimのデータをダウンロードし、
    各種グラフを出力します。

    eMiaxiSlim の CSVデータ は以下で公開されています
    https://emaxis.am.mufg.jp/lp/slim/pr1/

    Args:
    csv_url (str): データのCSVファイルのURL。
    web_url (str): 参照元のウェブページのURL。
    """

    df, asset_name, tmp_file_path = load_csv(csv_url)

    # 日本語を表示できるフォントに設定
    plt.rcParams['font.family'] = 'Meiryo'

    plot_moving_average_eMaxiSlim(df, asset_name, web_url, plt)

    plot_relative_strength_eMaxiSlim(df, asset_name, web_url, plt)

    os.remove(tmp_file_path)

    plt.show()


def plot_moving_average_eMaxiSlim(df, asset_name, web_url, plt):
    """
    短期および長期移動平均の乖離をプロットします。
    """

    # 短期移動平均の日数パターン1
    SMA_PATTERN_1 = 20
    # 短期移動平均の日数パターン2
    SMA_PATTERN_2 = 50
    # 長期移動平均の日数パターン1
    LMA_PATTERN_1 = 100
    # 長期移動平均の日数パターン2
    LMA_PATTERN_2 = 365

    # 移動平均の計算
    df['SMA_1'] = df['基準価額(円)'].rolling(window=SMA_PATTERN_1).mean()
    df['SMA_2'] = df['基準価額(円)'].rolling(window=SMA_PATTERN_2).mean()
    df['LMA_1'] = df['基準価額(円)'].rolling(window=LMA_PATTERN_1).mean()
    df['LMA_2'] = df['基準価額(円)'].rolling(window=LMA_PATTERN_2).mean()

    # window は 計算に使用するデータの範囲 = 期間 を示す変数

    # 乖離の計算（基準価額 - 移動平均）
    df['Divergence_SMA_1'] = df['基準価額(円)'] / df['SMA_1']
    df['Divergence_SMA_2'] = df['基準価額(円)'] / df['SMA_2']
    df['Divergence_LMA_1'] = df['基準価額(円)'] / df['LMA_1']
    df['Divergence_LMA_2'] = df['基準価額(円)'] / df['LMA_2']

    # '基準日'列を日付の形式に変換
    df['基準日'] = pd.to_datetime(df['基準日'])
    # 各年の最初の日付のインデックスを取得
    first_day_indices = df.groupby(df['基準日'].dt.year)['基準日'].idxmin()
    # 各年の最初の日付のデータのみを抽出
    df_year_starts = df.loc[first_day_indices]

    # 移動平均のトレイリングストップを下回ったポイントを特定
    # under_trailing_stop_points = under_trailing_stop_condition(df, '基準価額(円)', 'SMA_2', 3)

    # 乖離のグラフ化
    fig1 = plt.figure(figsize=(14, 6))

    plt.plot(df.index, df['Divergence_SMA_1'], label=f'基準価額 / {SMA_PATTERN_1}日移動平均', color='orange', linewidth=1)
    plt.plot(df.index, df['Divergence_SMA_2'], label=f'基準価額 / {SMA_PATTERN_2}日移動平均', color=(255/255, 110/255, 0/255))
    plt.plot(df.index, df['Divergence_LMA_1'], label=f'基準価額 / {LMA_PATTERN_1}日移動平均', color='gray', linewidth=1)
    plt.plot(df.index, df['Divergence_LMA_2'], label=f'基準価額 / {LMA_PATTERN_2}日移動平均', color=(0.8, 0.8, 0.8), linewidth=1)

    # トレイリングストップを下回ったポイントを強調表示
    # plt.scatter(under_trailing_stop_points.index, [1.0] * len(under_trailing_stop_points), label='トレイリングストップ警告', color='red', linewidth=0.5)

    plt.axhline(y=1.0, color='blue', linestyle='-')  # 基準線

    plot_cross_point(df, 'Divergence_SMA_1', 'Divergence_LMA_1')

    # x軸のラベルと位置を設定
    plt.xticks(df_year_starts.index, df_year_starts['基準日'].dt.strftime('%Y'))

    plt.title(f'{asset_name} 基準価額と移動平均の乖離')
    plt.xlabel('日付')
    plt.ylabel('乖離', rotation='vertical')
    plt.legend()

    # 引用元をプロットに追加
    url_text = f"データ引用元:{asset_name} ({web_url})"
    plt.text(0.5, -0.12, url_text, ha='center', va='center', transform=plt.gca().transAxes, fontsize=8, color='gray')



def plot_relative_strength_eMaxiSlim(df, asset_name, web_url, plt):
    """
    RSI をプロットします 
    相対力指数（Relative Strength Index、RSI）は、テクニカル分析における重要な指標の一つで、特定の期間内の価格変動を基に、買われ過ぎや売られ過ぎの状態を判断するために用いられます。RSIは0から100までの値を取りますが、通常30以下が「売られ過ぎ」、70以上が「買われ過ぎ」とされます。
    """

    # 14日間という期間は、短期的な価格変動を捉えるのに十分な長さでありながら、過度に反応しすぎない期間です。短すぎるとノイズが多くなり、長すぎるとトレンドが遅れて捉えられます。
    rsl_window = 30
    df['RSL'] = calculate_RSI(df['基準価額(円)'], rsl_window)

    # '基準日'列を日付の形式に変換
    df['基準日'] = pd.to_datetime(df['基準日'])
    # 各年の最初の日付のインデックスを取得
    first_day_indices = df.groupby(df['基準日'].dt.year)['基準日'].idxmin()
    # 各年の最初の日付のデータのみを抽出
    df_year_starts = df.loc[first_day_indices]

    # 日本語を表示できるフォントに設定
    plt.rcParams['font.family'] = 'Meiryo'

    # RSIのグラフ化
    fig2 = plt.figure(figsize=(14, 6))

    plt.plot(df['基準日'], df['RSL'], label=f'価格変動比 {rsl_window}日', color='green', linewidth=1)
    plt.axhline(y=90, color='red', linestyle='--', label='買われ過ぎ')
    plt.axhline(y=70, color='orange', linestyle='--', label='やや買われ過ぎ')
    plt.axhline(y=30, color='green', linestyle='--', label='やや売られ過ぎ')
    plt.axhline(y=10, color='blue', linestyle='--', label='売られ過ぎ')
    plt.legend()
    plt.title(f'{asset_name} 相対力指数 RSL')
    plt.xlabel('日付')
    plt.ylabel('RSI', rotation='vertical')

    # x軸のラベルと位置を設定
    plt.xticks(df_year_starts['基準日'], df_year_starts['基準日'].dt.strftime('%Y'))

    # 引用元をプロットに追加
    url_text = f"データ引用元:{asset_name} ({web_url})"
    plt.text(0.5, -0.12, url_text, ha='center', va='center', transform=plt.gca().transAxes, fontsize=8, color='gray')

    plt.tight_layout()


def load_csv(csv_url):
    '''
    CSVファイルをURLからダウンロードして df 形式に出力
    一時ファイルをテンポラリに作成します
    '''

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

    return df, asset_name, tmp_file_path

# RSIの計算
def calculate_RSI(data, window):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    RS = gain / loss
    RSI = 100 - (100 / (1 + RS))
    return RSI


# トレイリングストップを下回った日付
def under_trailing_stop_condition(df, target_column, sma_column, percentage):
    condition = (df[target_column] <= df[sma_column] * (1 + percentage / 100)) & (df[target_column] > df[sma_column])
    return df[condition]