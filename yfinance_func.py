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
    SMA_PATTERN_2 = 60
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
    df['Divergence_SMA_PATTERN_1'] = df['Close'] / df['SMA_1'] 
    df['Divergence_SMA_PATTERN_2'] = df['Close'] / df['SMA_2']
    df['Divergence_LMA_PATTERN_1'] = df['Close'] / df['LMA_1']
    # df['Divergence_LMA_PATTERN_2'] = df['Close'] / df['LMA_2']

    # 移動平均のトレイリングストップを下回ったポイントを特定
    under_trailing_stop_points = under_trailing_stop_condition(df, 'Close', 'SMA_2', 3)

    # 日本語を表示できるフォントに設定
    plt.rcParams['font.family'] = 'Meiryo'

    # 乖離のグラフ化
    plt.figure(figsize=(14, 6))

    plt.plot(df.index, df['Divergence_SMA_PATTERN_1'], label=f'終値 / {SMA_PATTERN_1}日移動平均', color='orange', linewidth=1)
    plt.plot(df.index, df['Divergence_SMA_PATTERN_2'], label=f'終値 / {SMA_PATTERN_2}日移動平均', color=(255/255, 110/255, 0/255))
    plt.plot(df.index, df['Divergence_LMA_PATTERN_1'], label=f'終値 / {LMA_PATTERN_1}日移動平均', color='gray', linewidth=1)
    # plt.plot(df.index, df['Divergence_LMA_PATTERN_2'], label=f'終値 / {LMA_PATTERN_2}日移動平均', color=(0.7, 0.7, 0.7), linewidth=1)

    # トレイリングストップを下回ったポイントを強調表示
    plt.scatter(under_trailing_stop_points.index, [1.0] * len(under_trailing_stop_points), label='トレイリングストップ警告', color='red', linewidth=0.5)

    plt.axhline(y=1.0, color='blue', linestyle='-')  # 基準線

    plot_cross_point(df, 'Divergence_SMA_PATTERN_1', 'Divergence_LMA_PATTERN_1')

    plt.title(f'{name} 終値と移動平均線の乖離')
    plt.xlabel('日付')
    plt.ylabel('乖離', rotation='vertical')
    plt.legend()    # 凡例を表示

    # 引用元をプロットに追加
    url_text = "データ引用元:Yahoo! Finance's API (https://pypi.org/project/yfinance/)"
    plt.text(0.5, -0.12, url_text, ha='center', va='center', transform=plt.gca().transAxes, fontsize=8, color='gray')

    plt.show()


# トレイリングストップを下回った日付
def under_trailing_stop_condition(df, target_column, sma_column, percentage):
    condition = (df[target_column] <= df[sma_column] * (1 + percentage / 100)) & (df[target_column] > df[sma_column])
    return df[condition]