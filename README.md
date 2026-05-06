# Merge-Brokerage-CSVs
Imports Vanguard and Fidelity assets in the form of csv files, prompts user for additional cash holdings, lists all imported assets together in a new file, and determines balance of stocks vs bonds vs cash.

Usage: mergebroker.py vanguardfile fidelityfile
  e.g: mergebroker.py OfxDownload.csv Portfolio_Positions_Jan-16-2026.csv

NOTE: both arguments must be CSV files from their respective brokerages. As of this writing, to download these:
  On vanguard.com, go to Holdings > Download Center > specify CSV, and use any date range (dated transactions will be ignored)
  On fidelity.com, go into Accounts > Positions tab > open the 3-dot menu > select Download

Requires the AssetClassLookupTable.csv file in order to determine asset classes for each symbol (e.g. VTSAX = US Stock). You can add your own stock/bond symbols to AssetClassLookupTable.csv. If the scripts finds a symbol it cannot identify using AssetClassLookupTable.csv, it will prompt you to type in the asset class and subclass.
