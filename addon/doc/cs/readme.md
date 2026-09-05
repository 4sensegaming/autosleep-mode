# Automatický režim spánku

[English](../en/readme.md) | **Čeština** | [Deutsch](../de/readme.md) | [Italiano](../it/readme.md) | [Slovenčina](../sk/readme.md)

* Autor: Lukáš Hosnedl
* Minimální verze NVDA: 2026.1
* Poslední testovaná verze NVDA: 2026.2

**Vytvořeno umělou inteligencí, navrženo a důkladně otestováno lidmi.**

## Popis

Pokud jste někdy potřebovali často zapínat režim spánku NVDA pro jednu konkrétní aplikaci nebo pro několik aplikací, je tento doplněk právě pro vás.
Umožní NVDA zapamatovat si aplikace, které chcete používat s režimem spánku, takže už ho nikdy nebudete muset zapínat ručně.

Mnoho aplikací určených pro nevidomé buď samo mluví, nebo své zprávy posílá přímo odečítačům obrazovky. V takových aplikacích odečítač nemusí neustále sledovat jejich okna a hlídat v nich změny, protože sám nic aktivně nečte. Zapnutí režimu spánku v těchto aplikacích proto může být užitečné: máte jistotu, že vám neunikne žádné hlášení jen proto, že ho NVDA přebilo třeba příchozím oznámením, a že provoz aplikace nikdy nepřeruší žádná nadbytečná promluva odečítače.

Mějte ale na paměti, že když je režim spánku zapnutý, NVDA nezpracovává vlastní příkazy a nereaguje na ně. Abyste je mohli použít, musíte režim spánku zase vypnout, nebo se z aplikace dočasně přepnout jinam.

Dalším možným problémem u samoozvučených aplikací a u aplikací, které komunikují přímo s odečítači, jsou volby pro přerušení řeči při stisku klávesy Enter nebo jakékoli klávesy, které najdete v nastavení klávesnice NVDA. Pokud je některá z těchto voleb zapnutá, stisknete klávesu, která danou reakci vyvolá, a NVDA jste pro tuto aplikaci neuspali, svými stisky kláves v podstatě usekáváte řeč odečítače. Může se pak stát, že přeslechnete zprávu, kterou byste slyšet chtěli. Řešením je buď přerušování řeči při psaní pro danou aplikaci ručně vypnout, nebo si pro ni vytvořit konfigurační profil.

Vlastní vestavěný režim spánku NVDA v kombinaci s tímto doplňkem ale všechny tyto starosti odstraní úplně a natrvalo, protože když NVDA spí, stisky kláves řeč nepřerušují vůbec, a to ani řeč, kterou vyvolala přímo samotná aplikace.

## Použití

Doplněk nepotřebuje žádné vlastní klávesové zkratky. Jakmile je aplikace v [seznamu aplikací k uspání](#nastavení), stačí do ní přepnout: NVDA zaznamená nové okno v popředí, aplikaci rozpozná a uspí se pro ni.

Doplněk režim spánku nikdy sám nevypíná. Chová se stejně jako vždycky: trvá, dokud ho nevypnete klávesou NVDA+shift+S (ve výchozím nastavení, v laptopovém rozložení klávesnice NVDA+shift+Z), dokud aplikaci nezavřete, dokud ji neodeberete ze seznamu aplikací k uspání, nebo dokud se z ní nepřepnete jinam.

## Nastavení

Doplněk přidává do dialogu Nastavení NVDA (menu NVDA, Možnosti, Nastavení) kategorii **Automatický režim spánku**. Ta obsahuje tyto volby:

* **Aplikace k uspání** – seznam aplikací, pro které se má NVDA uspávat. Ve výchozím stavu je prázdný.
* **Odstranit** – odebere ze seznamu aplikaci, na které je fokus, takže se pro ni už NVDA nebude uspávat. Pokud máte vybráno několik aplikací najednou, tlačítko se změní na **Odstranit vybrané** a odebere je všechny naráz.
* **Dostupné aplikace** – všechny aplikace, které právě běží, zobrazují viditelné okno a zatím nejsou v seznamu pro automatické uspání.
* **Přidat** – přidá aplikaci, na které je fokus v seznamu dostupných aplikací, do seznamu aplikací k uspání. Pokud jich máte vybráno několik, tlačítko se změní na **Přidat vybrané** a přidá je všechny naráz. Přidaná aplikace z **Dostupných aplikací** zmizí a znovu se v nich objeví, jakmile ji odeberete z **Aplikací k uspání**.
* **Přidávat ručně uspané aplikace do seznamu pro automatické uspání** – ve výchozím stavu vypnuto. Když je zapnuto, každá aplikace, kterou uspíte ručně klávesou NVDA+shift+S (ve výchozím nastavení, v laptopovém rozložení klávesnice NVDA+shift+Z), se přidá do seznamu pro automatické uspání a od té chvíle se bude uspávat sama.
* **Odebírat ručně probuzené aplikace ze seznamu pro automatické uspání** – ve výchozím stavu vypnuto; je to zrcadlový protějšek předchozí volby. Když je zapnuto, probuzení aplikace ručně klávesou NVDA+shift+S (ve výchozím nastavení, v laptopovém rozložení klávesnice NVDA+shift+Z) ji okamžitě odebere ze seznamu aplikací k uspání, takže se pro ni NVDA už automaticky neuspí.

Obě zaškrtávací políčka jsou na sobě nezávislá. Zapnuté může být kterékoli z nich a mít zapnutá obě dává smysl: seznam pak sleduje, jak používáte NVDA+shift+S (ve výchozím nastavení, v laptopovém rozložení klávesnice NVDA+shift+Z), v obou směrech – roste, když aplikace umlčujete, a zmenšuje se, když je zase probouzíte.

Dokud nestisknete OK nebo Použít, nic se nezmění; tlačítko Zrušit ponechá nastavení přesně tak, jak bylo.

Ukládá se a porovnává název, pod kterým aplikaci zná NVDA, tedy název spustitelného souboru bez přípony – `firefox`, `notepad`, `explorer` a tak dále. Přidání aplikace do seznamu pro automatické uspání platí pro celou aplikaci, ne jen pro její jedno konkrétní okno, jehož název se zrovna zobrazuje.

Doplněk respektuje konfigurační profily, takže se vaše nastavení ukládá pro každý z nich samostatně.

## Licence

Tento doplněk je šířen pod licencí GNU General Public License verze 2. Podrobnosti najdete v souboru COPYING.txt.

## Spolupráce

Pokud byste chtěli přispět k vývoji doplňku – ať už překladem, hlášením chyb nebo vytvořením pull requestu – můžete tak učinit v jeho [repozitáři na GitHubu](https://github.com/4sensegaming/autosleep-mode). Veškerou pomoc vítám a vážím si jí.

## Historie změn

### Verze 1.0, 5. září 2026
* První verze