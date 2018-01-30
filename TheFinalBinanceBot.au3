#include <MsgBoxConstants.au3>
#include <ImageSearch2015.au3>


while 1
Call("ManeMeth")
WEnd



global $y = 0, $x = 0, $RefreshFound = 0, $CloseStart = 0, $yellowFound = 0

Func checkForImage()
$RefreshFound=0
$CloseStart = 0

Local $search = _ImageSearch('Complete.PNG', 0, $x, $y, 0)
Local $search2 = _ImageSearch('Refresh.PNG', 0, $x, $y, 0)

;Close found
If $search = 1 Then
$CloseStart = $search
EndIf

;Refresh found
If $search2 = 1 Then
$RefreshFound=$search2
EndIf

EndFunc


Func refresh()
MouseMove(1138, 741, 0)
MouseClick($MOUSE_CLICK_LEFT)
;Refresh tab
    Send("{RCTRL down}")
	Send("{F5}")
	Send("{RCTRL up}")
Sleep(5000)
EndFunc

Func yellowPix()
$yellowFound = 0

$coord = PixelSearch(288,446, 290,573, 0xB9BB1B)
If Not @error Then
    $yellowFound=1;
EndIf

EndFunc



Func reset()
Local $b = 0
MouseMove(180, 243, 0)
MouseClick($MOUSE_CLICK_LEFT)
	While $b <= 20
	Sleep(100)
	Send("{RIGHT}")
	$b = $b + 1
	WEnd
Send("{DOWN}")
EndFunc


Func startOrder()

Local $sText = WinGetTitle("[ACTIVE]")
MouseMove(1138, 741, 0)
MouseClick($MOUSE_CLICK_LEFT)
;Close tab
    Send("{RCTRL down}")
	Send("{w}")
	Send("{RCTRL up}")



if StringInStr($sText, "TRXBTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=TRXBTC")
EndIf
if StringInStr($sText, "ETHBTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=ETHBTC")
EndIf
if StringInStr($sText, "XRPBTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=XRPBTC")
EndIf
if StringInStr($sText, "NEOBTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=NEOBTC")
EndIf
if StringInStr($sText, "BCDBTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=BCDBTC")
EndIf
if StringInStr($sText, "NEBLBTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=NEBLBTC")
EndIf
if StringInStr($sText, "EOSBTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=EOSBTC")
EndIf
if StringInStr($sText, "ADABTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=ADABTC")
EndIf
if StringInStr($sText, "ICXBTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=ICXBTC")
EndIf
if StringInStr($sText, "VENBTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=VENBTC")
EndIf
if StringInStr($sText, "LTCBTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=LTCBTC")
EndIf
if StringInStr($sText, "XLMBTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=XLMBTC")
EndIf
if StringInStr($sText, "XVGBTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=XVGBTC")
EndIf
if StringInStr($sText, "WTCBTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=WTCBTC")
EndIf
if StringInStr($sText, "ELFBTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=ELFBTC")
EndIf
if StringInStr($sText, "POEBTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=POEBTC")
EndIf
if StringInStr($sText, "IOTABTC")=1 Then

ShellExecute("http://localhost/BinanceBot/vendor/baitercel/binance-api-php/bot.php?name=IOTABTC")
EndIf

EndFunc



Func ManeMeth()
Call("checkForImage")
Call("yellowPix")
;if CloseStart and yellow pixel found, we can start an order
If (($CloseStart = 1) And ($yellowFound = 1)) Then
Call("startOrder")
EndIf

If ($RefreshFound=1) Then
Call("refresh")
EndIf

If (($RefreshFound <> 1) And ($CloseStart <> 1) Then
Call("reset")
EndIf

EndFunc



while 1
Call("ManeMeth")
WEnd