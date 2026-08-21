# Automatický režim spánku

* Autor: Lukáš Hosnedl
* Poslední testovaná verze NVDA: 2026.3

## Popis

**Vytvořeno umělou inteligencí, navrženo a důkladně otestováno lidmi.**

Některé aplikace mluví samy za sebe. Hry, přehrávače médií a další samoozvučené programy si vytvářejí vlastní řeč a NVDA, které mluví přes ně, je přinejlepším rušivé. NVDA na to už řešení má – režim spánku, ve kterém NVDA v dané aplikaci zcela zmlkne – jenže ho musíte zapnout klávesou NVDA+shift+s pokaždé, když se do té aplikace vrátíte.

Doplněk Automatický režim spánku to udělá za vás. Sestavíte si seznam aplikací, ve kterých má být ticho, a NVDA se od té chvíle uspí ve chvíli, kdy se některá z nich dostane do popředí, a oznámí „Režim spánku zapnut“ přesně tak, jako byste klávesovou zkratku stiskli sami.

## Použití

Není co mačkat. Jakmile je aplikace v seznamu, stačí do ní přepnout: NVDA zaznamená nové okno v popředí, zjistí, že jde o jednu z vašich aplikací, a uspí se pro ni.

Doplněk režim spánku nikdy sám nevypíná. Chová se stejně jako vždycky: trvá, dokud ho nevypnete klávesou NVDA+shift+s nebo dokud aplikaci nezavřete.

## Nastavení

Doplněk přidává do dialogu Nastavení NVDA (menu NVDA, Možnosti, Nastavení) kategorii **Automatický režim spánku**. Obsahuje:

* **Aplikace k uspání** – aplikace, které NVDA uspí. Na začátku je seznam prázdný.
* **Odstranit** – odebere ze seznamu aplikaci, na které právě jste. Pokud jich máte vybráno více, tlačítko se změní na **Odstranit vybrané** a odebere je všechny najednou.
* **Spuštěné aplikace** – aplikace, které právě běží a zatím v seznamu nejsou.
* **Přidat** – přidá do seznamu aplikaci, na které právě jste. Pokud jich máte vybráno více, tlačítko se změní na **Přidat vybrané** a přidá je všechny najednou. Přidaná aplikace ze **Spuštěných aplikací** zmizí a znovu se v nich objeví, jakmile ji z **Aplikací k uspání** odeberete.
* **Přidávat ručně uspané aplikace do seznamu pro automatické uspání** – ve výchozím stavu vypnuto. Když je zapnuto, každá aplikace, kterou uspíte ručně klávesou NVDA+shift+s, se do seznamu přidá a od té chvíle se bude uspávat sama.

V obou seznamech lze vybrat více položek najednou obvyklým způsobem: shift se šipkami výběr rozšiřuje, control se šipkami a mezerník vybírá jednotlivé položky.

Dokud nestisknete OK nebo Použít, nic se nezmění; tlačítko Zrušit ponechá nastavení přesně tak, jak bylo.

## Poznámky

* Aplikace jsou uvedeny pod názvem, pod kterým je zná NVDA, tedy názvem spustitelného souboru bez přípony – `firefox`, `notepad`, `explorer`. Právě ten doplněk porovnává, takže v seznamu vidíte přesně to, co se porovnává.
* Samotné NVDA je ze **Spuštěných aplikací** záměrně vynecháno. Uspání NVDA v jeho vlastních oknech by jen umlčelo jeho vlastní rozhraní.
* Seznam patří k vašemu konfiguračnímu profilu, takže každý profil může mít vlastní sadu aplikací. Stejně jako každé jiné nastavení NVDA se na disk zapíše, když NVDA ukládá konfiguraci, ať už na vyžádání, nebo při ukončení.
* Aplikace, která je v popředí při spuštění NVDA, se rovněž jednou zkontroluje, takže z aplikace, ve které jste už byli, není nutné odejít a vrátit se do ní.

## Licence

Tento doplněk je šířen pod licencí GNU General Public License, verze 2. Podrobnosti najdete v souboru COPYING.txt.
