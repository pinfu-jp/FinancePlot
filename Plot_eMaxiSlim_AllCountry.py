from eMaxiSlim_func import plot_eMaxiSlim_from_csv_url

web_url = 'https://emaxis.am.mufg.jp/fund/253425.html'
csv_url = 'https://www.am.mufg.jp/fund_file/setteirai/253425.csv?_gl=1*1ssgo0m*_ga*NTQyNzc1NjY1LjE3MDc5NzAyMTc.*_ga_3ZNV996Y9H*MTcxMTE2ODYwMS4zLjEuMTcxMTE2OTY0MS41Ni4wLjA.'

plot_eMaxiSlim_from_csv_url(csv_url, web_url)

