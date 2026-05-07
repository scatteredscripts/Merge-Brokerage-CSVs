# Merge-Brokerage-CSVs
If you need to pull Vanguard and Fidelity holdings together in a spreadsheet, this script might help you. You will need to download csv files from vanguard.com and fidelity.com. The script imports Vanguard and Fidelity assets from those csv files, and prompts you for additional cash holdings. Finally, it generates a new CombinedVanguardFidelityCash.csv file with holdings from both brokerages, and attempts to determine the balance of stocks vs bonds vs cash.

Usage: mergebroker.py  vanguardfile  fidelityfile

  e.g: mergebroker.py  OfxDownload.csv  Portfolio_Positions_Jan-16-2026.csv

NOTE: both arguments must be CSV files from their respective brokerages. As of this writing, to download these:

  On vanguard.com, go to Holdings > Download Center > specify CSV, and use any date range (dated transactions will be ignored).
  
  On fidelity.com, go into Accounts > Positions tab > open the 3-dot menu > select Download.

Requires the AssetClassLookupTable.csv file (included) in order to determine asset classes (stock vs bond) and subclasses (US vs International) for each symbol. You can add your own stock/bond symbols to AssetClassLookupTable.csv. If the scripts finds a symbol it cannot identify using AssetClassLookupTable.csv, it will prompt you to type in the asset class and subclass.

This script also relies on importing several libraries, including pandas.
