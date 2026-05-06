#!/usr/bin/python3

# Import Vanguard and Fidelity assets in the form of csv files, prompt user for additional cash holdings,
#  list all imported assets together in a new file, and determine balance of stocks vs bonds vs cash.
# Usage: mergebroker.py vanguardfile fidelityfile
#   e.g: mergebroker.py OfxDownload.csv Portfolio_Positions_Jan-16-2026.csv
# NOTE: both files must be CSV files from their respective brokerages. As of this writing, to download these:
#  On vanguard.com, go to Holdings > Download Center > specify CSV, and use any date range (dated transactions will be ignored)
#  On fidelity.com, go into Accounts > Positions tab > open the 3-dot menu > select Download
# Requires AssetClassLookupTable.csv to identify asset classes for each symbol (e.g. VTSAX = US Stock)

import pandas # csv grokking tool, had to python3 -m pip install pandas from limited account first
import os
import sys # to parse inputs of Vanguard csv (1st argument) and Fidelity csv files

# General plan
# Start with vanguard csv file
#   add column 'Brokerage' at beginning, all vals = 'Vanguard'
#   add column 'Account Name', all vals = 'Vanguard Brokerage Acct'
#   rename column 'Total Value' to 'Current Value' to match Fidelity's naming convention
#   vanguardcsv.to_csv(tmpfile,columns=['Brokerage','Account Name','Account Number','Symbol', 'Current Value'])
# Repeat steps for Fidelity csv file
# Do some math to count calculate subtotals and percentages

# Start with vanguard csv file
vangfilename = sys.argv[1] # Vanguard file MUST be the 1st argument
#    Import csv file and create DataFrame from it, ignoring bad lines, don't use first column as an index since values aren't unique
vangframe = pandas.read_csv(vangfilename, on_bad_lines='skip', index_col=False) 
#    Add column for Brokerage and set all its values to 'Vanguard'
vangframe['Brokerage'] = 'Vanguard' # add a column for Brokerage e.g. Vanguard vs Fidelity
#    Add column for Account Name (to match the column in Fidelity csv file)
vangframe['Account Name'] = 'Vanguard Brokerage Acct' 
#    rename the value column for consistency with Fidelity file
vangframe.rename(columns = {"Total Value": "Current Value"}, inplace = True) 
#    Create frame from selected columns per https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html
selectedVangframe = vangframe[["Brokerage", "Account Name", "Account Number", "Symbol", "Investment Name", "Current Value"]]
print("\nImported Vanguard data:\n",selectedVangframe)

# Next, process Fidelity csv file
fidfilename = sys.argv[2] # Fidelity filename MUST be the 2nd argument
#    Import csv file and create DataFrame from it, ignoring bad lines, don't use first column as an index since values aren't unique
fidelframe = pandas.read_csv(fidfilename, on_bad_lines = 'skip', index_col=False)
#    Add column for Brokerage
fidelframe['Brokerage'] = 'Fidelity' # add a column for Brokerage e.g. Vanguard vs Fidelity
#    Rename 'Description' column to 'Investment Name' to match Vanguard format
fidelframe.rename(columns = {"Description": "Investment Name"}, inplace = True)
#    Remove text disclaimer at the end and other non-data rows
fidelframe.dropna(subset=['Account Name','Current Value'],inplace=True) # drop rows with missing Account Number or Current Value data, i.e. the text fluff at the end of the file
#    Create frame from selected columns per https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html
selectedFidelframe = fidelframe[["Brokerage", "Account Name", "Account Number", "Symbol", "Investment Name", "Current Value"]]
print("\nImported Fidelity data:\n", selectedFidelframe)

# Concatenate vanguard and Fidelity selected frames per https://pandas.pydata.org/docs/user_guide/merging.html#concat
combinedframe = pandas.concat([selectedVangframe, selectedFidelframe], ignore_index=True)

# Prompt user for additional cash not included in either input file and append that in final row
additionalCash = input("\n\nEnter additional total cash not included in Vanguard or Fidelity files: ")
if not additionalCash: #if input was null i.e. user hit return
  additionalCash = 0 #set default value = 0
additionalCash = float(additionalCash)
cashRow = [{'Brokerage': 'Cash', 'Account Name': 'Additional Cash', 'Account Number': '999999', 'Symbol': 'CASH', 'Investment Name': 'Other cash in CDs HYSA Treasuries etc', 'Current Value': additionalCash}]
cashRowFrame = pandas.DataFrame(cashRow) #create a frame from that row
combinedframe = pandas.concat([combinedframe, cashRowFrame], ignore_index=True) # add the row for additionalCash onto the end of combinedframe

# Using AssetClassLookupTable.csv, identify asset class (stocks, bonds, cash) and asset subclass (US, International) 
#  for each holding, then calculate subtotals and percentages for each

# Create additional columns Investment Class, Investment Subclass
combinedframe['Asset Class'] = 'Unknown' #column 6, starting from 0
combinedframe['Asset Subclass'] = 'Unknown' #column 7, starting from 0

# Read in the Asset Class / Asset Subclass lookup table
assetLookupFrame = pandas.read_csv('AssetClassLookupTable.csv', on_bad_lines = 'skip', index_col="Symbol")
# e.g. assetLookupFrame.loc['VTSAX','Asset Class'] should == 'Stocks'

# Create a subtotals table and initialize it to all zeroes
assetClassList = assetLookupFrame['Asset Class'].unique() # make a list of Asset Classes e.g. 'Stocks', 'Bonds', 'Cash'
assetSubclassList = assetLookupFrame['Asset Subclass'].unique() # make a list of Asset Subclasses e.g. 'US', 'International'
subtotalsFrame = pandas.DataFrame(index=assetClassList, columns=assetSubclassList, dtype=float, data=0)

# Iterate through rows of the combinedframe and set Asset Class and Asset Subclass for each holding
#   based on the assetLookupFrame, and tally subtotals as we go
rows, columns = combinedframe.shape
for i in range(rows):
  combinedSymbol = combinedframe.iloc[i,3]
  try:
    matchingAssetClass = assetLookupFrame.loc[combinedSymbol, 'Asset Class']
    combinedframe.iloc[i,6] = matchingAssetClass
    matchingAssetSubclass = assetLookupFrame.loc[combinedSymbol, 'Asset Subclass']
    combinedframe.iloc[i,7] = matchingAssetSubclass
  except:
    print("\nCan't find Asset Class and/or Subclass for ", combinedSymbol, ". Enter Asset Class and Subclass, or hit enter to classify as unknown.")
    # Prompt user to type in missing Asset Class, Subclass
    matchingAssetClass = input("\nEnter matching class (Stocks, Bonds, Cash) [unknown] ")
    if not matchingAssetClass: #if user just hit return, set to "unknown"
      matchingAssetClass = "unknown"
    combinedframe.iloc[i,6] = matchingAssetClass
    matchingAssetSubclass = input("\nEnter matching subclass (US, International) [unknown] ")
    if not matchingAssetSubclass: #if user just hit return, set to "unknown"
      matchingAssetSubclass = "unknown"
    combinedframe.iloc[i,7] = matchingAssetSubclass
  matchingCurrentValue = combinedframe.iloc[i,5] # get the dollar value of that investment
  if isinstance(matchingCurrentValue, str): # if the dollar total is a string, clean it up and convert it to float
    matchingCurrentValue = matchingCurrentValue.replace("$","") # remove any dollar signs
    matchingCurrentValue = float(matchingCurrentValue)
    combinedframe.iloc[i,5] = matchingCurrentValue # fix the value in the combinedframe as well
  # Add the current value to the subtotal for its Asset Class and Asset Subclass
  subtotalsFrame.loc[matchingAssetClass, matchingAssetSubclass] = subtotalsFrame.loc[matchingAssetClass, matchingAssetSubclass] + matchingCurrentValue 

# Get grand total of all assets
grandTotal = round(sum(combinedframe['Current Value']),2)

# calculate percentages
percentagesFrame = round(subtotalsFrame/grandTotal * 100,2)


# Save and print combined data
combinedcsvfile = open('CombinedVanguardFidelityCash.csv', 'w', newline='')
combinedframe.to_csv(combinedcsvfile) # save combined DataFrame to a new CSV file
print("\n\nCombined data:\n", combinedframe)

# save and print grand total
outstr = "\nGrand Total:,,,,,,{}".format(grandTotal)
combinedcsvfile.write(outstr)
print("Grand total: ", grandTotal)

# save and print subtotals
print("\n\nSubtotals:\n", subtotalsFrame)
combinedcsvfile.write("\n\nSubtotals:\n")
subtotalsFrame.to_csv(combinedcsvfile, float_format='%.2f')

#save and print percentages
print("\nPercentages:\n", percentagesFrame)
combinedcsvfile.write("\n\nPercentages:\n")
percentagesFrame.to_csv(combinedcsvfile)

combinedcsvfile.close()
print("\n\nCombined data has been saved in CombinedVanguardFidelityCash.csv.\n\n")

  
 
