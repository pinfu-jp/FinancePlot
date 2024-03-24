from eMaxiSlim_func import plot_eMaxiSlim_from_csv_url

web_url = 'https://emaxis.am.mufg.jp/fund/252653.html'
csv_url = 'https://www.am.mufg.jp/fund_file/setteirai/252653.csv?_gl=1*1n42gnr*_ga*NTQyNzc1NjY1LjE3MDc5NzAyMTc.*_ga_3ZNV996Y9H*MTcxMTE5MDQ3MC40LjEuMTcxMTE5MDg2My41MS4wLjA.'

plot_eMaxiSlim_from_csv_url(csv_url, web_url)

