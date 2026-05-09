# Iron-Art — Kowalstwo Artystyczne Łódź

Statyczna strona pracowni kowalstwa artystycznego Iron-Art (`kowalstwo-artystyczne.com.pl`).

## Struktura

```
.
├── index.html                          # strona główna (PL)
├── *.html                              # podstrony PL (balustrady, meble, sklep, kontakt itd.)
├── en/
│   └── *.html                          # wersja angielska
├── assets/
│   ├── css/                            # style: style.css, galeria, kontakt, sklep, formularze
│   ├── js/                             # jQuery, fancybox, ciasteczka, mail, rozwijane menu
│   ├── images/                         # zdjęcia podzielone na kategorie wyrobów
│   └── shop/                           # zdjęcia produktów ze sklepu
└── favicon.png
```

## Uruchamianie lokalnie

```bash
python -m http.server 8000
```

Strona dostępna pod `http://127.0.0.1:8000/`.

## Edycja

- **Treść stron** — edytuj odpowiedni plik `*.html` w korzeniu (PL) lub w `en/` (EN).
- **Style** — `assets/css/style.css` to główny arkusz, pozostałe są podsekcyjne (galeria, kontakt itd.).
- **Skrypty** — `assets/js/`. Galerie obrazów używają fancyBox 2.x (`assets/js/fancybox/`).
- **Zdjęcia** — wrzucaj do `assets/images/<kategoria>/`. Sklep ma osobny folder `assets/shop/`.

## Uwagi

- Iframe Google Maps oraz YouTube wymagają połączenia z internetem.
- Google Analytics (GA / Tag Manager `UA-109855821-1`) ładowany jest z CDN.
- Czcionki Petrona, Roboto Flex i Roboto Condensed pobierane z Google Fonts.
