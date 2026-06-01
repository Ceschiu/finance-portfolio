Attribute VB_Name = "Module1"
Option Explicit

'==============================================================================
' SUB: CalcolaPnL
'------------------------------------------------------------------------------
' SCOPO:
'   Calcola il P&L (Profit & Loss) per ogni strumento del portafoglio:
'     P&L = (Prezzo Corrente - Prezzo Acquisto) * Quantita
'   Colora ogni cella P&L in base al segno (verde positivi / rosso negativi)
'   e aggiunge una riga "Totale" in fondo alla tabella.
'
' OUTPUT:
'   - Colonna P&L popolata per ogni strumento, formattata in stile italiano
'   - Sfondo cella P&L colorato per segno (verde / rosso)
'   - Riga "Tot" in fondo con bordo superiore, grassetto e sfondo azzurrino
'   - MsgBox di riepilogo con numero strumenti e totale
'
' PROPRIETA':
'   Macro idempotente: si puo' rilanciare N volte senza creare duplicati,
'   perche' UltimaRiga e' calcolata dalla colonna Ticker (input), non da P&L
'   (output). La riga Totale viene sovrascritta nella stessa posizione.
'==============================================================================
Sub CalcolaPnL()

    '--------------------------------------------------------------------------
    ' DICHIARAZIONE VARIABILI
    '--------------------------------------------------------------------------
    Dim counter As Long
    Dim UltimaRiga As Long
    Dim posQty As Long, posAcq As Long, posCorr As Long, posPnL As Long
    Dim tot As Double
    Dim ws As Worksheet

    '--------------------------------------------------------------------------
    ' RIFERIMENTO FOGLIO + POSIZIONI COLONNE (lookup dinamico via Match)
    '--------------------------------------------------------------------------
    Set ws = ThisWorkbook.Sheets("Sheet1")
    UltimaRiga = ws.Cells(ws.Rows.Count, 2).End(xlUp).Row

    posQty = Application.WorksheetFunction.Match("B (Quantità)", ws.Range("2:2"), 0)
    posAcq = Application.WorksheetFunction.Match("C (Prezzo Acquisto)", ws.Range("2:2"), 0)
    posCorr = Application.WorksheetFunction.Match("D (Prezzo Corrente)", ws.Range("2:2"), 0)
    posPnL = Application.WorksheetFunction.Match("E (P&L)", ws.Range("2:2"), 0)

    tot = 0

    '--------------------------------------------------------------------------
    ' LOOP PRINCIPALE: calcolo P&L + codifica colore + formato + accumulo tot
    '   Si parte da riga 4 perche' righe 2-3 sono header (label + nome colonna)
    '--------------------------------------------------------------------------
    For counter = 4 To UltimaRiga
        ' P&L = (Prezzo Corrente - Prezzo Acquisto) * Quantita
        ws.Cells(counter, posPnL).Value = (ws.Cells(counter, posCorr).Value - ws.Cells(counter, posAcq).Value) * ws.Cells(counter, posQty).Value

        ' Codifica colore in base al segno del P&L
        If ws.Cells(counter, posPnL).Value >= 0 Then
            ws.Cells(counter, posPnL).Interior.Color = RGB(198, 239, 206)   ' verde chiaro
        Else
            ws.Cells(counter, posPnL).Interior.Color = RGB(255, 199, 206)   ' rosso chiaro
        End If

        ' Formato numerico finanza italiana: positivi normali, negativi in rosso
        ws.Cells(counter, posPnL).NumberFormat = "#,##0.00;[Red]-#,##0.00"

        ' Accumulo totale cumulato
        tot = tot + ws.Cells(counter, posPnL).Value
    Next counter

    '--------------------------------------------------------------------------
    ' RIGA TOTALE: valore + etichetta + formattazione professionale
    '--------------------------------------------------------------------------
    ws.Cells(UltimaRiga + 1, posPnL).Value = tot
    ws.Cells(UltimaRiga + 1, posCorr).Value = "Tot"

    ' Formattazione "block" della coppia etichetta+valore con With
    With ws.Cells(UltimaRiga + 1, posPnL - 1).Resize(1, 2)
        .Font.Bold = True
        .Borders(xlEdgeTop).LineStyle = xlContinuous
        .Interior.Color = RGB(217, 225, 242)   ' azzurrino soft
    End With

    ' Formato numerico classico (senza colore per il totale)
    ws.Cells(UltimaRiga + 1, posPnL).NumberFormat = "#,##0.00"

    '--------------------------------------------------------------------------
    ' MESSAGGIO FINALE
    '   UltimaRiga - 3 = numero strumenti (escluse le 3 righe di header)
    '--------------------------------------------------------------------------
    MsgBox "P&L calcolato per " & (UltimaRiga - 3) & " strumenti." & vbNewLine & _
           "Totale: " & Format(tot, "#,##0.00") & " EUR", vbInformation

End Sub

