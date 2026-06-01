Attribute VB_Name = "Module3"
Option Explicit

'==============================================================================
' MODULO: Bond Pricing & Duration
'------------------------------------------------------------------------------
' Contiene 3 funzioni finanziarie per bond a cedola fissa, usabili come
' formule custom (UDF) nelle celle Excel:
'   - BondPrice          : prezzo del bond (somma CF attualizzati)
'   - DurationMacaulay   : duration di Macaulay (media pesata dei tempi)
'   - DurationModificata : duration modificata (sensibilita' al tasso)
'
' PATTERN: composizione di funzioni
'   DurationMacaulay   chiama BondPrice
'   DurationModificata chiama DurationMacaulay
'
' CONVENZIONI:
'   - cedola e ytm sono tassi annuali in formato decimale (es. 0.05 = 5%)
'   - maturita in anni interi
'   - valNominale nella valuta del bond
'   - Cedola annuale, capitalizzazione annuale
'==============================================================================


'==============================================================================
' FUNCTION: BondPrice
'------------------------------------------------------------------------------
' Calcola il prezzo di un bond a cedola fissa come somma dei flussi di cassa
' attualizzati:
'
'   P = sum_{t=1..T} [ C / (1+y)^t ] + N / (1+y)^T
'
' dove:
'   C = cedola * N (importo cedolare annuo)
'   N = valore nominale
'   y = YTM
'   T = maturita in anni
'==============================================================================
Function BondPrice(cedola As Double, ytm As Double, _
                   maturita As Long, valNominale As Double) As Double

    Dim counter As Long
    Dim Prezzo As Double

    For counter = 1 To maturita
        ' Cedola attualizzata
        Prezzo = Prezzo + cedola * valNominale / (1 + ytm) ^ counter

        ' Alla scadenza si aggiunge anche il rimborso del nominale
        If counter = maturita Then
            Prezzo = Prezzo + valNominale / (1 + ytm) ^ counter
        End If
    Next counter

    BondPrice = Prezzo
End Function


'==============================================================================
' FUNCTION: DurationMacaulay
'------------------------------------------------------------------------------
' Calcola la Duration di Macaulay: media pesata dei tempi dei flussi di cassa,
' con pesi pari al valore attuale di ciascun flusso diviso il prezzo del bond:
'
'   D_Mac = ( sum_{t=1..T} [ t * CF_t / (1+y)^t ] ) / P
'
' dove:
'   CF_t = cedola * N            per t < T
'   CF_T = cedola * N + N        a scadenza
'   P    = BondPrice (richiamato internamente - composition)
'
' PROPRIETA' UTILI:
'   - Zero coupon (cedola=0)   =>  D_Mac = maturita
'   - Cedola piu' alta         =>  D_Mac piu' bassa (a parita' di maturita')
'   - Maturita' piu' alta      =>  D_Mac piu' alta
'==============================================================================
Function DurationMacaulay(cedola As Double, ytm As Double, _
                          maturita As Long, valNominale As Double) As Double

    Dim counter As Long
    Dim Prezzo As Double, Numeratore As Double

    ' Numeratore: somma dei flussi pesati per il tempo t
    For counter = 1 To maturita
        Numeratore = Numeratore + counter * cedola * valNominale / (1 + ytm) ^ counter

        ' Alla scadenza si aggiunge anche il nominale (pesato per maturita)
        If counter = maturita Then
            Numeratore = Numeratore + counter * valNominale / (1 + ytm) ^ counter
        End If
    Next counter

    ' Denominatore: prezzo del bond (riuso di BondPrice - composition)
    Prezzo = BondPrice(cedola, ytm, maturita, valNominale)

    DurationMacaulay = Numeratore / Prezzo
End Function


'==============================================================================
' FUNCTION: DurationModificata
'------------------------------------------------------------------------------
' Calcola la Duration Modificata: misura la sensibilita' del prezzo del bond
' a piccole variazioni dello YTM (approssimazione del primo ordine).
'
'   D_Mod = D_Mac / (1 + y)
'
' INTERPRETAZIONE:
'   Una variazione dello YTM di +1 bp (= 0.01%) produce una variazione
'   approssimata del prezzo pari a:   dP/P ˜ -D_Mod * 0.0001
'==============================================================================
Function DurationModificata(cedola As Double, ytm As Double, _
                            maturita As Long, valNominale As Double) As Double

    Dim DMac As Double

    ' Riuso di DurationMacaulay (composition) - niente codice duplicato
    DMac = DurationMacaulay(cedola, ytm, maturita, valNominale)

    DurationModificata = DMac / (1 + ytm)
End Function

