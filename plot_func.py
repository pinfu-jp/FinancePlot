import matplotlib.pyplot as plt


def plot_cross_point(df, sma_name, lma_name):
    """
    短期移動平均線と長期移動平均線の交差位置をプロット
    """

    # SMA と LMA が交差するインデックスを見つける
    crossing_indices = df.index[df[sma_name] * df[lma_name] < 0]

    # 交差点に印をつける
    for index in crossing_indices:
        divergence_sma = df.loc[index, sma_name]
        divergence_lma = df.loc[index, lma_name]
        
        if divergence_sma > 0 and divergence_lma < 0:
            color = 'red'
        elif divergence_sma < 0 and divergence_lma > 0:
            color = 'blue'
        else:
            continue
        
        plt.scatter(index, df.loc[index, sma_name], color=color, marker='o', s=3)
