from eMaxiSlim_func import plot_eMaxiSlim_from_csv_url

web_url = 'https://emaxis.am.mufg.jp/fund/253214.html'
csv_url = 'https://www.am.mufg.jp/fund_file/setteirai/253214.csv?_gl=1*dt62fw*_ga*NTQyNzc1NjY1LjE3MDc5NzAyMTc.*_ga_3ZNV996Y9H*MTcxMTE5MDQ3MC40LjEuMTcxMTE5MTIxNi41OS4wLjA.'

plot_eMaxiSlim_from_csv_url(csv_url, web_url)

