from eMaxiSlim_func import plot_eMaxiSlim_from_csv_url

web_url = 'https://emaxis.am.mufg.jp/fund/253266.html'
csv_url = 'https://www.am.mufg.jp/fund_file/setteirai/253266.csv?_fsi=D1jqam1T&_gl=1*fmqu6n*_ga*NTQyNzc1NjY1LjE3MDc5NzAyMTc.*_ga_3ZNV996Y9H*MTcxMTExNzA4Mi4xLjEuMTcxMTExNzEwNC4zOC4wLjA.'

plot_eMaxiSlim_from_csv_url(csv_url, web_url)

