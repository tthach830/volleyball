@echo off

rem The specific indices may vary based on your system's date format.
set Month=%date:~4,2%
set Day=%date:~7,2%
set Year=%date:~10,4%

rem Build the formatted date string for the URL
set DateString=%Month%%%2F%Day%%%2F%Year%

rem Define the base URL without the date parameter
set BaseURL="https://casantacruzweb.myvscloud.com/webtrac/web/search.html?Action=Start&SubAction=&_csrf_token=ka63066T0C7226291U38444E5I5Y6T5870594V6K53045G3V576D0A6V5S6M5F086V466O6F046X4C5V6C02064H586I0C024K4X58065I4P6D5R036Y4Y6I67035V4P6C&date="

rem Define the rest of the URL after the date parameter
set EndURL="&keyword=&primarycode=&frheadcount=0&type=Beach+Volleyball+Court&frclass=&keywordoption=Match+One&blockstodisplay=15&features1=&features2=&features3=&features4=&features5=&features6=&features7=&features8=&begintime=12%%3A00+am&subtype=&category=&features=&display=Detail&module=FR&multiselectlist_value=&frwebsearch_buttonsearch=yes"

rem A common user agent string for Google Chrome on Windows
set UserAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"

rem Add the --user-agent option to the command
"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless --disable-gpu --print-to-pdf="C:\Users\%USERNAME%\Desktop\volleyball_courts.pdf" " %BaseURL%%DateString%%EndURL% "


echo Done.