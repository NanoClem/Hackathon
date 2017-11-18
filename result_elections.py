
import xlrd


book  = xlrd.open_workbook("president_results_2016.xls")
sheet = book.sheet_by_index(0)

col             = 0
tab_etats       = [""]*sheet.nrows
tab_electeurs   = [0]*sheet.nrows
tab_Hilary      = [0.0]*sheet.nrows
tab_Trump       = [0.0]*sheet.nrows


for i in range(sheet.nrows):

    Etats               = sheet.cell(rowx = i, colx = col).value
    tab_etats[i]        = Etats

    nb_electeurs        = sheet.cell(rowx = i, colx = col+1).value
    tab_electeurs[i]    = int(nb_electeurs)

    vote_Hilary         = sheet.cell(rowx = i, colx = col+2).value
    tab_Hilary[i]       = float(vote_Hilary)

    vote_Trump          = sheet.cell(rowx = i, colx = col+3).value
    tab_Trump[i]        = float(vote_Trump)


print(tab_etats[0])
print(tab_electeurs[0])
