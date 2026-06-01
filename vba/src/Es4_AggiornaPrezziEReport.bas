Attribute VB_Name = "Module4"
Option Explicit

'==============================================================================
' SUB: AggiornaPrezziEReport
'------------------------------------------------------------------------------
' SCOPO:
'   Aggiorna i prezzi correnti del portafoglio leggendo da un file Excel
'   esterno (MarketData.xlsx), ricalcola P&L, e genera report aggregato
'   per settore.
'
' WORKFLOW:
'   1. Apre MarketData.xlsx (stessa cartella del file principale)
'   2. Per ogni strumento del portafoglio: cerca ticker in MarketData e
'      aggiorna prezzo corrente se diverso
'   3. Chiama CalcolaPnL per ricalcolare i P&L
'   4. Aggrega P&L per settore nel foglio "Report"
'   5. Chiude MarketData senza salvare
'   6. Misura tempo totale di esecuzione
'
' PATTERN CHIAVE:
'   - File I/O con apertura/chiusura workbook esterno
'   - Path dinamico via ThisWorkbook.Path (no hardcoded paths)
'   - On Error GoTo + CleanExit + chiusura sicura del file in caso di errore
'   - Application.Match + IsError per lookup robusto
'==============================================================================
Sub AggiornaPrezziEReport()

    '--------------------------------------------------------------------------
    ' SETUP: ottimizzazioni performance
    '--------------------------------------------------------------------------
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    Application.EnableEvents = False
    Application.DisplayAlerts = False

    '--------------------------------------------------------------------------
    ' DICHIARAZIONE VARIABILI
    '--------------------------------------------------------------------------
    Dim wbMkt As Workbook
    Dim wsPort As Worksheet, wsMkt As Worksheet, wsReport As Worksheet
    Dim counter As Long, Corretti As Long, NonTrovati As Long, nSettori As Long
    Dim UltimaRiga As Long, UltimaRigaMkt As Long, i As Long
    Dim posCorr As Long, posCorrMkt As Long, posSect As Long, posPnL As Long
    Dim posTick As Long, posTickMkt As Long
    Dim FilePath As String
    Dim pos As Variant, Lista As Variant
    Dim tStart As Double, SommaSect As Double, elapsed As Double

    '--------------------------------------------------------------------------
    ' AVVIO TIMER + ERROR HANDLER
    '--------------------------------------------------------------------------
    tStart = Timer
    On Error GoTo ErrHandler

    '--------------------------------------------------------------------------
    ' APERTURA FILE ESTERNO DI MARKET DATA
    ' Path dinamico relativo alla cartella del file principale
    '--------------------------------------------------------------------------
    FilePath = ThisWorkbook.Path & "\MarketData.xlsx"
    Set wbMkt = Workbooks.Open(FilePath)

    '--------------------------------------------------------------------------
    ' RIFERIMENTI FOGLI + POSIZIONI COLONNE (lookup dinamico via Match)
    '--------------------------------------------------------------------------
    ' Foglio del portafoglio (file principale)
    Set wsPort = ThisWorkbook.Sheets("Sheet1")
    UltimaRiga = wsPort.Cells(wsPort.Rows.Count, 2).End(xlUp).Row
    posTick = Application.Match("A (Ticker)", wsPort.Range("2:2"), 0)
    posCorr = Application.WorksheetFunction.Match("D (Prezzo Corrente)", wsPort.Range("2:2"), 0)

    ' Foglio Market Data (file esterno)
    Set wsMkt = wbMkt.Sheets("Prices")
    UltimaRigaMkt = wsMkt.Cells(wsMkt.Rows.Count, 1).End(xlUp).Row
    posTickMkt = Application.Match("Ticker", wsMkt.Range("2:2"), 0)
    posCorrMkt = Application.WorksheetFunction.Match("Last Price", wsMkt.Range("2:2"), 0)

    '--------------------------------------------------------------------------
    ' LOOP DI AGGIORNAMENTO PREZZI
    ' Per ogni strumento: cerca il ticker in MarketData con Match
    '   - Se non trovato: incrementa counter "non trovati"
    '   - Se trovato e prezzo diverso: aggiorna e incrementa "aggiornati"
    '--------------------------------------------------------------------------
    For counter = 4 To UltimaRiga
        pos = Application.Match(wsPort.Cells(counter, posTick), wsMkt.Columns(posTickMkt), 0)

        If IsError(pos) Then
            NonTrovati = NonTrovati + 1
        ElseIf wsPort.Cells(counter, posCorr).Value <> wsMkt.Cells(pos, posCorrMkt).Value Then
            Corretti = Corretti + 1
            wsPort.Cells(counter, posCorr).Value = wsMkt.Cells(pos, posCorrMkt).Value
        End If
    Next counter

    '--------------------------------------------------------------------------
    ' RICALCOLO P&L (chiama macro esistente)
    '--------------------------------------------------------------------------
    Call CalcolaPnL

    '--------------------------------------------------------------------------
    ' REPORT - SEZIONE 1: intestazione e statistiche generali
    '--------------------------------------------------------------------------
    Set wsReport = ThisWorkbook.Worksheets("Report")

    With wsReport.Range("A1")
        .Value = "REPORT AGGIORNAMENTO PORTAFOGLIO"
        .Font.Size = 14
        .Font.Bold = True
    End With
    wsReport.Range("A2").Value = "Data esecuzione: " & Format(Now, "dd/mm/yyyy hh:mm:ss")
    wsReport.Range("A3").Value = "Strumenti aggiornati: " & Corretti
    wsReport.Range("A4").Value = "Strumenti non trovati: " & NonTrovati

    With wsReport.Range("A6")
        .Value = "Settore"
        .Font.Bold = True
    End With
    With wsReport.Range("B6")
        .Value = "P&L Totale"
        .Font.Bold = True
    End With

    '--------------------------------------------------------------------------
    ' REPORT - SEZIONE 2: P&L aggregato per Settore
    ' Estrae settori unici con Unique, somma con loop annidato sui dati
    '--------------------------------------------------------------------------
    posSect = Application.Match("H (Settore)", wsPort.Range("2:2"), 0)
    posPnL = Application.Match("E (P&L)", wsPort.Range("2:2"), 0)

    Lista = Application.WorksheetFunction.Unique( _
        wsPort.Range(wsPort.Cells(4, posSect), wsPort.Cells(UltimaRiga, posSect)))

    For i = 1 To UBound(Lista, 1)
        SommaSect = 0
        For counter = 4 To UltimaRiga
            If wsPort.Cells(counter, posSect).Value = Lista(i, 1) Then
                SommaSect = SommaSect + wsPort.Cells(counter, posPnL).Value
            End If
        Next counter

        wsReport.Range("A7").Offset(i - 1, 0).Value = Lista(i, 1)
        wsReport.Range("B7").Offset(i - 1, 0).Value = SommaSect
    Next i

    '--------------------------------------------------------------------------
    ' CHIUSURA FILE ESTERNO (senza salvare modifiche)
    '--------------------------------------------------------------------------
    wbMkt.Close SaveChanges:=False

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
    elapsed = Timer - tStart
    MsgBox "Macro completata in " & Format(elapsed, "0.00") & "s. " & _
           "Aggiornati " & Corretti & " strumenti, non trovati " & NonTrovati & " strumenti"
    Exit Sub

ErrHandler:
    MsgBox "Errore: " & Err.Description, vbCritical
    ' Garanzia di chiusura file esterno anche in caso di errore
    If Not wbMkt Is Nothing Then
        wbMkt.Close SaveChanges:=False
    End If
    Resume CleanExit

End Sub

