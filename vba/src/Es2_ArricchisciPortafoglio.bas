Attribute VB_Name = "Module2"
Option Explicit

'==============================================================================
' SUB: ArricchisciPortafoglio
'------------------------------------------------------------------------------
' SCOPO:
'   Per ogni strumento del portafoglio (Sheet1), recupera nome, settore e
'   rating dal foglio Anagrafica via lookup ticker, e classifica il rating
'   con codifica colore (verde/giallo/arancio/rosso/grigio) seguendo le
'   categorie del rischio creditizio.
'
' OUTPUT:
'   - Colonne Nome / Settore / Rating popolate sul foglio portafoglio
'   - Cella Rating colorata in base alla categoria di merito creditizio
'   - Cella Ticker colorata in giallo se non trovato in Anagrafica
'   - Mini-tabella riepilogo conteggi per categoria a destra del portafoglio
'
' PATTERN CHIAVE:
'   - Match + Cells per lookup multi-colonna (1 ricerca, 3 letture)
'     anziche' 3 VLookup distinti
'   - Application.Match + IsError per gestione robusta dei ticker mancanti
'   - Select Case per classificazione rating multi-livello
'==============================================================================
Sub ArricchisciPortafoglio()

    '--------------------------------------------------------------------------
    ' DICHIARAZIONE VARIABILI
    '--------------------------------------------------------------------------
    Dim counter As Long
    Dim UltimaRiga As Long, UltimaRigaAnag As Long
    Dim posTick As Long, posName As Long, posSect As Long, posRate As Long
    Dim posTickAnag As Long, posNameAnag As Long, posSectAnag As Long, posRateAnag As Long
    Dim ws As Worksheet, wsAnag As Worksheet
    Dim tickerName As String
    Dim nAplus As Long, nBBB As Long, nBB As Long, nHR As Long, nNV As Long
    Dim rigaAnag As Variant

    '--------------------------------------------------------------------------
    ' RIFERIMENTI FOGLI + POSIZIONI COLONNE (lookup dinamico via Match)
    '--------------------------------------------------------------------------
    ' Foglio portafoglio (Sheet1)
    Set ws = ThisWorkbook.Sheets("Sheet1")
    UltimaRiga = ws.Cells(ws.Rows.Count, 2).End(xlUp).Row
    posTick = Application.Match("A (Ticker)", ws.Range("2:2"), 0)
    posName = Application.Match("G (Nome)", ws.Range("2:2"), 0)
    posSect = Application.Match("H (Settore)", ws.Range("2:2"), 0)
    posRate = Application.Match("I (Rating)", ws.Range("2:2"), 0)

    ' Foglio Anagrafica (tabella di lookup)
    Set wsAnag = ThisWorkbook.Sheets("Anagrafica")
    UltimaRigaAnag = wsAnag.Cells(wsAnag.Rows.Count, 2).End(xlUp).Row
    posTickAnag = Application.Match("A (Ticker)", wsAnag.Range("2:2"), 0)
    posNameAnag = Application.Match("B (Nome)", wsAnag.Range("2:2"), 0)
    posSectAnag = Application.Match("C (Settore)", wsAnag.Range("2:2"), 0)
    posRateAnag = Application.Match("D (Rating)", wsAnag.Range("2:2"), 0)

    '--------------------------------------------------------------------------
    ' LOOP PRINCIPALE: lookup + popolamento + classificazione rating
    '   Si parte da riga 4 perche' righe 2-3 sono header (label + nome colonna)
    '--------------------------------------------------------------------------
    For counter = 4 To UltimaRiga
        tickerName = ws.Cells(counter, posTick).Value

        ' Ricerca posizione del ticker in Anagrafica (1 Match per riga)
        rigaAnag = Application.Match(tickerName, wsAnag.Columns(posTickAnag), 0)

        If IsError(rigaAnag) Then
            ' Ticker non presente in Anagrafica -> N/D + ticker giallo
            ws.Cells(counter, posName).Value = "N/D"
            ws.Cells(counter, posSect).Value = "N/D"
            ws.Cells(counter, posRate).Value = "N/D"
            ws.Cells(counter, posTick).Interior.Color = RGB(255, 235, 156)
        Else
            ' Ticker trovato -> copia Nome / Settore / Rating dalla riga matched
            ws.Cells(counter, posName).Value = wsAnag.Cells(rigaAnag, posNameAnag).Value
            ws.Cells(counter, posSect).Value = wsAnag.Cells(rigaAnag, posSectAnag).Value
            ws.Cells(counter, posRate).Value = wsAnag.Cells(rigaAnag, posRateAnag).Value
        End If

        '----- Classificazione rating: codifica colore + counter per categoria
        Select Case ws.Cells(counter, posRate).Value
            Case "AAA", "AA", "A"
                ' Investment Grade alto -> verde chiaro
                ws.Cells(counter, posRate).Interior.Color = RGB(198, 239, 206)
                nAplus = nAplus + 1
            Case "BBB"
                ' Investment Grade basso -> giallo chiaro
                ws.Cells(counter, posRate).Interior.Color = RGB(255, 235, 156)
                nBBB = nBBB + 1
            Case "BB", "B"
                ' Speculative -> arancio chiaro
                ws.Cells(counter, posRate).Interior.Color = RGB(255, 199, 132)
                nBB = nBB + 1
            Case "CCC", "CC", "C", "D"
                ' High Risk / Default -> rosso chiaro
                ws.Cells(counter, posRate).Interior.Color = RGB(255, 199, 206)
                nHR = nHR + 1
            Case Else
                ' N/D o valori non riconosciuti -> grigio
                ws.Cells(counter, posRate).Interior.Color = RGB(217, 217, 217)
                nNV = nNV + 1
        End Select
    Next counter

    '--------------------------------------------------------------------------
    ' MINI-TABELLA RIEPILOGO CONTEGGI (a destra della colonna Rating)
    '--------------------------------------------------------------------------
    ' Colonna etichette categorie
    With ws.Cells(2, posRate + 1)
        .Value = "Rating"
        .Font.Bold = True
    End With
    ws.Cells(3, posRate + 1).Value = "Investment Grade Alto (A+)"
    ws.Cells(4, posRate + 1).Value = "Investment Grade Basso (BBB)"
    ws.Cells(5, posRate + 1).Value = "Speculative (BB/B)"
    ws.Cells(6, posRate + 1).Value = "High Risk / Default"
    ws.Cells(7, posRate + 1).Value = "N/D"

    ' Colonna conteggi per categoria
    With ws.Cells(2, posRate + 2)
        .Value = "Count"
        .Font.Bold = True
    End With
    ws.Cells(3, posRate + 2).Value = nAplus
    ws.Cells(4, posRate + 2).Value = nBBB
    ws.Cells(5, posRate + 2).Value = nBB
    ws.Cells(6, posRate + 2).Value = nHR
    ws.Cells(7, posRate + 2).Value = nNV

    '--------------------------------------------------------------------------
    ' MESSAGGIO FINALE
    '   UltimaRiga - 3 = numero strumenti (sottratte le 3 righe di header)
    '--------------------------------------------------------------------------
    MsgBox "Anagrafica aggiornata per " & (UltimaRiga - 3) & " strumenti."

End Sub
