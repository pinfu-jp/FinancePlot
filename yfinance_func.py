import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from plot_func import plot_cross_point

def plot_from_yfinance(name, tickers, distance_year = 10):
    """
    Yahoo!ファイナンスからAPI経由で指定された指数データを取得し、
    短期および長期移動平均の乖離をプロットします。

    APIは以下で確認できます
    https://pypi.org/project/yfinance/

    Args:
    name (str): 指数名称。
    tickers (str): API用 指数定義名。
    distance_year (int): 現在日から何年遡るか。
    """

    # 短期移動平均の日数パターン1
    SMA_PATTERN_1 = 20
    # 短期移動平均の日数パターン2
    SMA_PATTERN_2 = 50
    # 長期移動平均の日数パターン1
    LMA_PATTERN_1 = 100
    # 長期移動平均の日数パターン2
    LMA_PATTERN_2 = 200


    # 現在の日付を取得
    current_time = datetime.now()

    # timedeltaオブジェクトを作成して年前の時刻を計算
    years_ago = current_time - timedelta(days=365.25 * distance_year)  # 年数 * 365.25（うるう年を考慮）

    # yfinanceのdownload関数に渡すために、日付を文字列形式に変換
    # 形式は 'YYYY-MM-DD' が必要です
    start_date = years_ago.strftime('%Y-%m-%d')
    end_date = current_time.strftime('%Y-%m-%d')

    # yfinanceを使ってS&P 500のデータを取得（例として2020年のデータを使用）
    df = yf.download(tickers, start=start_date, end=end_date)

    df['SMA_1'] = df['Close'].rolling(window=SMA_PATTERN_1).mean()
    df['SMA_2'] = df['Close'].rolling(window=SMA_PATTERN_2).mean()
    df['LMA_1'] = df['Close'].rolling(window=LMA_PATTERN_1).mean()
    # df['LMA_2'] = df['Close'].rolling(window=LMA_PATTERN_2).mean()

    # 乖離の計算（終値 - SMA_PATTERN）
    df['Divergence_SMA_PATTERN_1'] = df['SMA_1'] - df['Close']
    df['Divergence_SMA_PATTERN_2'] = df['SMA_2'] - df['Close']
    df['Divergence_LMA_PATTERN_1'] = df['LMA_1'] - df['Close']
    # df['Divergence_LMA_PATTERN_2'] = df['LMA_2'] - df['Close']

    # 日本語を表示できるフォントに設定
    plt.rcParams['font.family'] = 'Meiryo'

    # 乖離のグラフ化
    plt.figure(figsize=(14, 6))
    plt.plot(df.index, df['Divergence_SMA_PATTERN_1'], label=f'{SMA_PATTERN_1}日移動平均 - 終値', color='orange')
    plt.plot(df.index, df['Divergence_SMA_PATTERN_2'], label=f'{SMA_PATTERN_2}日移動平均 - 終値', color=(255/255, 210/255, 0/255), linewidth=1)
    plt.plot(df.index, df['Divergence_LMA_PATTERN_1'], label=f'{LMA_PATTERN_1}日移動平均 - 終値', color='gray', linewidth=1)
    # plt.plot(df.index, df['Divergence_LMA_PATTERN_2'], label=f'{LMA_PATTERN_2}日移動平均 - 終値', color=(0.7, 0.7, 0.7), linewidth=1)
    plt.axhline(y=0, color='blue', linestyle='-')  # 0のラインは終値

    plot_cross_point(df, 'Divergence_SMA_PATTERN_1', 'Divergence_LMA_PATTERN_1')

    plt.title(f'{name} 終値と移動平均線の乖離')
    plt.xlabel('日付')
    plt.ylabel('乖離', rotation='vertical')
    plt.legend()    # 凡例を表示

    # 引用元をプロットに追加
    url_text = "データ引用元:Yahoo! Finance's API (https://pypi.org/project/yfinance/)"
    plt.text(0.5, -0.12, url_text, ha='center', va='center', transform=plt.gca().transAxes, fontsize=8, color='gray')

    plt.show()
