# Automatický režim spánku

[English](../en/readme.md) | [Čeština](../cs/readme.md) | [Deutsch](../de/readme.md) | [Italiano](../it/readme.md) | **Slovenčina**

* Autor: Lukáš Hosnedl
* Minimálna verzia NVDA: 2026.1
* Posledná testovaná verzia NVDA: 2026.2

**Vytvorené umelou inteligenciou, navrhnuté a dôkladne otestované ľuďmi.**

## Popis

Ak ste niekedy potrebovali často zapínať režim spánku NVDA pre jednu konkrétnu aplikáciu alebo pre viacero aplikácií, tento doplnok je práve pre vás.
Umožní NVDA zapamätať si aplikácie, ktoré chcete používať s režimom spánku, takže ho už nikdy nebudete musieť zapínať ručne.

Mnohé aplikácie určené pre nevidiacich buď samy hovoria, alebo svoje správy posielajú priamo čítačom obrazovky. V takýchto aplikáciách čítač nemusí neustále sledovať ich okná a hľadať v nich zmeny, pretože sám nič aktívne nečíta. Zapnutie režimu spánku v týchto aplikáciách preto môže byť užitočné: máte istotu, že vám neunikne žiadne hlásenie len preto, že ho NVDA prehlušilo napríklad prichádzajúcim oznámením, a že chod aplikácie nikdy nepreruší žiadna reč čítača navyše.

Majte však na pamäti, že keď je režim spánku zapnutý, NVDA nespracúva vlastné príkazy a nereaguje na ne. Aby ste ich mohli použiť, musíte režim spánku zase vypnúť, alebo sa z aplikácie dočasne prepnúť inam.

Ďalším možným problémom pri aplikáciách s vlastnou rečou a pri aplikáciách, ktoré komunikujú priamo s čítačmi, sú voľby **prerušiť reč pri písaní** a **Prerušiť reč klávesom Enter**, ktoré nájdete v nastaveniach klávesnice NVDA. Ak je niektorá z týchto volieb zapnutá, stlačíte kláves, ktorý danú reakciu vyvolá, a NVDA ste pre túto aplikáciu neuspali, svojimi stlačeniami klávesov v podstate sekáte reč čítača. Môže sa potom stať, že prepočujete správu, ktorú by ste počuť chceli. Riešením je buď prerušovanie reči pri písaní pre danú aplikáciu ručne vypnúť, alebo si pre ňu vytvoriť konfiguračný profil.

Vlastný vstavaný režim spánku NVDA v kombinácii s týmto doplnkom však všetky tieto starosti odstráni úplne a natrvalo, pretože keď NVDA spí, stlačenia klávesov reč neprerušujú vôbec, a to ani reč, ktorú vyvolala priamo samotná aplikácia.

## Použitie

Doplnok nepotrebuje žiadne vlastné klávesové skratky. Len čo je aplikácia v [zozname aplikácií na uspatie](#nastavenia), stačí do nej prepnúť: NVDA zaznamená nové okno v popredí, aplikáciu rozpozná a uspí sa pre ňu.

Doplnok režim spánku nikdy sám nevypína. Správa sa rovnako ako vždy: trvá, kým ho nevypnete klávesom NVDA+shift+S (predvolene, pri rozložení klávesnice laptop NVDA+shift+Z), kým aplikáciu nezatvoríte, kým ju neodoberiete zo zoznamu aplikácií na uspatie, alebo kým sa z nej neprepnete inam.

## Nastavenia

Doplnok pridáva do dialógu Nastavenia NVDA (menu NVDA, Možnosti, Nastavenia) kategóriu **Automatický režim spánku**. Tá obsahuje tieto voľby:

* **Aplikácie na uspatie** – zoznam aplikácií, pre ktoré sa má NVDA uspávať. Predvolene je prázdny.
* **Odstrániť** – odoberie zo zoznamu aplikáciu, na ktorej je fokus, takže sa pre ňu už NVDA nebude uspávať. Ak máte vybraných viacero aplikácií naraz, tlačidlo sa zmení na **Odstrániť vybrané** a odoberie ich všetky naraz.
* **Dostupné aplikácie** – všetky aplikácie, ktoré práve bežia, zobrazujú viditeľné okno a zatiaľ nie sú v zozname na automatické uspatie.
* **Pridať** – pridá aplikáciu, na ktorej je fokus v zozname dostupných aplikácií, do zoznamu aplikácií na uspatie. Ak ich máte vybraných viacero, tlačidlo sa zmení na **Pridať vybrané** a pridá ich všetky naraz. Pridaná aplikácia z **Dostupných aplikácií** zmizne a znova sa v nich objaví, len čo ju odoberiete z **Aplikácií na uspatie**.
* **Pridávať ručne uspané aplikácie do zoznamu na automatické uspatie** – predvolene vypnuté. Keď je zapnuté, každá aplikácia, ktorú uspíte ručne klávesom NVDA+shift+S (predvolene, pri rozložení klávesnice laptop NVDA+shift+Z), sa pridá do zoznamu na automatické uspatie a od tej chvíle sa bude uspávať sama.
* **Odoberať ručne prebudené aplikácie zo zoznamu na automatické uspatie** – predvolene vypnuté; je to zrkadlový náprotivok predchádzajúcej voľby. Keď je zapnuté, prebudenie aplikácie ručne klávesom NVDA+shift+S (predvolene, pri rozložení klávesnice laptop NVDA+shift+Z) ju okamžite odoberie zo zoznamu aplikácií na uspatie, takže sa pre ňu NVDA už automaticky neuspí.

Obidve začiarkavacie políčka sú od seba nezávislé. Zapnuté môže byť ktorékoľvek z nich a mať zapnuté obidve dáva zmysel: zoznam potom sleduje, ako používate NVDA+shift+S (predvolene, pri rozložení klávesnice laptop NVDA+shift+Z), v obidvoch smeroch – rastie, keď aplikácie umlčujete, a zmenšuje sa, keď ich zase zobudíte.

Kým nestlačíte OK alebo Použiť, nič sa nezmení; tlačidlo Zrušiť ponechá nastavenia presne tak, ako boli.

Ukladá sa a porovnáva názov, pod ktorým aplikáciu pozná NVDA, teda názov spustiteľného súboru bez prípony – `firefox`, `notepad`, `explorer` a tak ďalej. Pridanie aplikácie do zoznamu na automatické uspatie platí pre celú aplikáciu, nielen pre jej jedno konkrétne okno, ktorého názov sa práve zobrazuje.

Doplnok rešpektuje konfiguračné profily, takže sa vaše nastavenia ukladajú pre každý z nich samostatne.

## Licencia

Tento doplnok je šírený pod licenciou GNU General Public License verzia 2. Podrobnosti nájdete v súbore COPYING.txt.

## Spolupráca

Ak chcete prispieť k vývoju doplnku – prekladom, hlásením chýb alebo vytvorením pull requestu – môžete tak urobiť v [jeho repozitári na GitHube](https://github.com/4sensegaming/autosleep-mode). Akákoľvek pomoc je vítaná a cením si ju.

## História zmien

### Verzia 1.0, 5. septembra 2026
* Prvá verzia