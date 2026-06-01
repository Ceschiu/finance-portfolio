Attribute VB_Name = "Module5"
Option Explicit

'==============================================================================
' SUB: AnalizzaPortafoglio
'------------------------------------------------------------------------------
' SCOPO:
'   Analizza un portafoglio di N strumenti (testato su 1000) e produce un
'   report completo:
'     - Calcola P&L per ogni strumento
'     - Identifica Top 5 winners e Top 5 losers
'     - Aggrega P&L per settore (via Dictionary)
'     - Genera report sul foglio "Report"
'     - Misura tempo totale di esecuzione
'
' PATTERN CHIAVE:
'   - Range-to-array per caricamento dati (1 I/O per colonna)
'   - Bulk write del P&L sul foglio (1 sola operazione di scrittura)
'   - Dictionary per aggregazione settore (lookup O(1))
'   - WorksheetFunction.Large/Small per top/bottom 5
'==============================================================================
Sub AnalizzaPortafoglio()

    '--------------------------------------------------------------------------
    ' SETUP: error handler + ottimizzazioni performance + timer
    '--------------------------------------------------------------------------
    On Error GoTo ErrHandler

    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    Application.EnableEvents = False
    Application.DisplayAlerts = False

    Dim tStart As Double
    tStart = Timer

    '--------------------------------------------------------------------------
    ' RIFERIMENTI AI FOGLI
    '--------------------------------------------------------------------------
    Dim ws As Worksheet
    Dim wsReport As Worksheet
    Set ws = ThisWorkbook.Worksheets("PortafoglioPro")
    Set wsReport = ThisWorkbook.Worksheets("Report")

    '--------------------------------------------------------------------------
    ' RILEVAMENTO DIMENSIONI E POSIZIONI COLONNE (lookup dinamico via Match)
    '--------------------------------------------------------------------------
    Dim UltimaRiga As Long
    UltimaRiga = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row

    Dim posTick As Long, posSect As Long, posQty As Long
    Dim posAcq As Long, posCorr As Long, posPnL As Long

    posTick = Application.Match("Ticker", ws.Range("1:1"), 0)
    posSect = Application.Match("Settore", ws.Range("1:1"), 0)
    posQty = Application.Match("Quantita", ws.Range("1:1"), 0)
    posAcq = Application.Match("Prezzo Acquisto", ws.Range("1:1"), 0)
    posCorr = Application.Match("Prezzo Corrente", ws.Range("1:1"), 0)
    posPnL = Application.Match("P&L", ws.Range("1:1"), 0)

    '--------------------------------------------------------------------------
    ' CARICAMENTO DATI IN MEMORIA (range-to-array)
    ' 5 letture I/O totali, indipendenti dalla dimensione del dataset
    '--------------------------------------------------------------------------
    Dim quantita() As Variant, PrezzoAcq() As Variant, PrezzoCorr() As Variant
    Dim Settore() As Variant, Ticker() As Variant

    ReDim quantita(1 To UltimaRiga - 1)
    ReDim PrezzoAcq(1 To UltimaRiga - 1)
    ReDim PrezzoCorr(1 To UltimaRiga - 1)
    ReDim Settore(1 To UltimaRiga - 1)
    ReDim Ticker(1 To UltimaRiga - 1)

    quantita = ws.Range(ws.Cells(2, posQty), ws.Cells(UltimaRiga, posQty)).Value
    PrezzoAcq = ws.Range(ws.Cells(2, posAcq), ws.Cells(UltimaRiga, posAcq)).Value
    PrezzoCorr = ws.Range(ws.Cells(2, posCorr), ws.Cells(UltimaRiga, posCorr)).Value
    Settore = ws.Range(ws.Cells(2, posSect), ws.Cells(UltimaRiga, posSect)).Value
    Ticker = ws.Range(ws.Cells(2, posTick), ws.Cells(UltimaRiga, posTick)).Value

    '--------------------------------------------------------------------------
    ' STRUTTURE DI OUTPUT
    '   - PnL: matrice di output per il bulk write
    '   - ListaSettori: settori unici (per dimensionamento)
    '   - dictSet: hash map per aggregazione P&L per settore (O(1) lookup)
    '--------------------------------------------------------------------------
    Dim ListaSettori() As Variant, PnLSettori() As Variant, PnL() As Variant
    ListaSettori = Application.WorksheetFunction.Unique(Settore)
    ReDim PnLSettori(1 To UBound(ListaSettori), 1 To 1)
    ReDim PnL(1 To UBound(quantita), 1 To 1)

    Dim dictSet As Object
    Set dictSet = CreateObject("Scripting.Dictionary")

    '--------------------------------------------------------------------------
    ' LOOP PRINCIPALE: calcolo P&L per strumento + aggregazione settori
    '--------------------------------------------------------------------------
    Dim i As Long, j As Long, tot As Double, s As String

    For i = 1 To UBound(quantita, 1)
        ' Calcolo P&L del singolo strumento
        PnL(i, 1) = quantita(i, 1) * (PrezzoCorr(i, 1) - PrezzoAcq(i, 1))
        tot = tot + PnL(i, 1)

        ' Aggregazione P&L per settore via Dictionary
        s = Settore(i, 1)
        If dictSet.Exists(s) Then
            dictSet(s) = dictSet(s) + PnL(i, 1)
        Else
            dictSet.Add s, PnL(i, 1)
        End If
    Next i

    '--------------------------------------------------------------------------
    ' BULK WRITE: scrive tutto il vettore P&L sul foglio in 1 sola operazione
    '--------------------------------------------------------------------------
    ws.Range(ws.Cells(2, posPnL), ws.Cells(UltimaRiga, posPnL)).Value = PnL

    '--------------------------------------------------------------------------
    ' REPORT - SEZIONE 1: intestazione + statistiche generali
    '--------------------------------------------------------------------------
    With wsReport.Range("A1")
        .Value = "PORTFOLIO ANALYTICS REPORT"
        .Font.Size = 14
        .Font.Bold = True
    End With
    wsReport.Range("A2").Value = "Strumenti aggiornati: " & UltimaRiga - 1
    wsReport.Range("A3").Value = "P&L totale portafoglio: " & Format(tot, "#,##0.00") & " Euro"
    wsReport.Range("A4").Value = "Data esecuzione: " & Format(Now, "dd/mm/yyyy hh:mm:ss")

    '--------------------------------------------------------------------------
    ' REPORT - SEZIONE 2: Top 5 Winners e Top 5 Losers
    ' Usa Large/Small per trovare i k-esimi valori, poi Match per ticker
    '--------------------------------------------------------------------------
    wsReport.Range("A6").Value = "Top 5 winners"
    wsReport.Range("B6").Value = "P&L"
    wsReport.Range("A13").Value = "Top 5 losers"
    wsReport.Range("B13").Value = "P&L"

    Dim posRiga As Variant

    ' Top 5 winners (Large = k-esimo valore piu' grande)
    For i = 1 To 5
        wsReport.Range("A6").Offset(i, 0).Value = Application.WorksheetFunction.Large(PnL, i)
        posRiga = Application.Match(wsReport.Range("A6").Offset(i, 0).Value, PnL, 0)
        wsReport.Range("B6").Offset(i, 0).Value = Ticker(posRiga, 1)
    Next i

    ' Top 5 losers (Small = k-esimo valore piu' piccolo)
    For i = 1 To 5
        wsReport.Range("A13").Offset(i, 0).Value = Application.WorksheetFunction.Small(PnL, i)
        posRiga = Application.Match(wsReport.Range("A13").Offset(i, 0).Value, PnL, 0)
        wsReport.Range("B13").Offset(i, 0).Value = Ticker(posRiga, 1)
    Next i

    '--------------------------------------------------------------------------
    ' REPORT - SEZIONE 3: P&L aggregato per Settore
    ' Legge dal Dictionary popolato nel loop principale
    '--------------------------------------------------------------------------
    wsReport.Range("A20").Value = "P&L per Settore"
    wsReport.Range("B20").Value = "P&L"

    Dim k As Variant, rigaReport As Long
    rigaReport = 21
    For Each k In dictSet.Keys
        wsReport.Cells(rigaReport, 1).Value = k
        wsReport.Cells(rigaReport, 2).Value = dictSet(k)
        rigaReport = rigaReport + 1
    Next k

'==============================================================================
' EXIT POINTS - cleanup garantito sia in caso di successo sia di errore
'==============================================================================
CleanExit:
    ' Ripristino settings Excel
    Application.ScreenUpdating = True
    Application.Calculation = xlCalculationAutomatic
    Application.EnableEvents = True
    Application.DisplayAlerts = True

    ' Timing e messaggio finale
    Dim tempo As Double
    tempo = Timer - tStart
    MsgBox "Completato in " & Format(tempo, "0.00") & " secondi"
    Exit Sub

ErrHandler:
    MsgBox "Errore: " & Err.Description, vbCritical
    Resume CleanExit

End Sub
