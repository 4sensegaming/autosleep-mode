# Automatischer Schlafmodus

[English](../en/readme.md) | [Čeština](../cs/readme.md) | **Deutsch** | [Italiano](../it/readme.md) | [Slovenčina](../sk/readme.md)

* Autor: Lukáš Hosnedl
* Mindestens erforderliche NVDA-Version: 2026.1
* Letzte getestete NVDA-Version: 2027.1

**Erstellt von einer KI, entworfen und gründlich getestet von Menschen.**

## Beschreibung

Wenn Sie den Schlafmodus von NVDA schon einmal für eine bestimmte Anwendung oder für mehrere Anwendungen immer wieder einschalten mussten, dann ist diese Erweiterung genau das Richtige für Sie.
Sie lässt NVDA sich die Anwendungen merken, die Sie mit dem Schlafmodus verwenden möchten, sodass Sie ihn nie wieder von Hand einschalten müssen.

Viele Anwendungen für blinde Menschen bringen entweder eine eigene Sprachausgabe mit oder senden ihre Meldungen direkt an den Screenreader. In diesen Anwendungen muss der Screenreader deren Fenster nicht ständig auf Änderungen überwachen, da er selbst nichts aktiv vorliest. Den Schlafmodus in solchen Anwendungen einzuschalten kann daher hilfreich sein: So geht keine Ansage verloren, weil NVDA gerade zum Beispiel eine eingehende Benachrichtigung darüber gesprochen hat, und keine zusätzliche Sprachausgabe des Screenreaders unterbricht jemals den Ablauf der Anwendung.

Beachten Sie jedoch, dass NVDA bei eingeschaltetem Schlafmodus seine eigenen Befehle nicht verarbeitet und nicht auf sie reagiert. Dazu müssen Sie ihn wieder ausschalten oder vorübergehend zu einer anderen Anwendung wechseln.

Ein weiteres mögliches Problem bei Anwendungen mit eigener Sprachausgabe oder mit direkter Kommunikation zum Screenreader sind die Optionen **Sprachausgabe während der Eingabe unterbrechen** und **Sprachausgabe beim Drücken der Eingabetaste unterbrechen**, die Sie in den Tastatureinstellungen von NVDA finden. Ist eine dieser Optionen eingeschaltet, drücken Sie eine Taste, die das entsprechende Verhalten auslöst, und haben Sie NVDA für diese Anwendung nicht schlafen gelegt, dann schneiden Ihre Tastendrücke die Sprachausgabe des Screenreaders faktisch ab. Dadurch kann es passieren, dass Sie eine Meldung überhören, die Sie eigentlich hören wollten. Eine mögliche Lösung besteht darin, das Unterbrechen der Sprachausgabe für die betreffende Anwendung von Hand auszuschalten oder ein Konfigurationsprofil dafür anzulegen.

Der in NVDA eingebaute Schlafmodus zusammen mit dieser Erweiterung nimmt Ihnen diesen ganzen Aufwand jedoch vollständig und dauerhaft ab, denn bei schlafendem NVDA unterbrechen Tastendrücke die Sprachausgabe überhaupt nicht, auch nicht diejenige, die die Anwendung selbst ausgelöst hat.

## Verwendung

Diese Erweiterung benötigt keine eigenen Tastenbefehle. Sobald eine Anwendung in der [Liste der Anwendungen für den Schlafmodus](#einstellungen) steht, genügt es, zu ihr zu wechseln: NVDA bemerkt das neue Fenster im Vordergrund, erkennt die Anwendung und legt sich für sie schlafen.

Der Schlafmodus wird von der Erweiterung nie wieder ausgeschaltet. Er verhält sich so wie eh und je: Er bleibt bestehen, bis Sie ihn mit NVDA+Umschalt+S ausschalten (Standardbelegung, im Tastatur-Layout Laptop NVDA+Umschalt+Z), bis die Anwendung geschlossen wird, bis Sie sie aus der Liste der Anwendungen für den Schlafmodus entfernen oder bis Sie zu einer anderen Anwendung wechseln.

## Einstellungen

Die Erweiterung fügt dem Dialog Einstellungen von NVDA (NVDA-Menü, Optionen, Einstellungen) die Kategorie **Automatischer Schlafmodus** hinzu. Sie enthält:

* **Anwendungen für den Schlafmodus** – die Liste der Anwendungen, für die sich NVDA schlafen legen soll. Standardmäßig ist sie leer.
* **Entfernen** – entfernt die fokussierte Anwendung aus der Liste, sodass sich NVDA für diese Anwendung nicht mehr schlafen legt. Wenn Sie mehrere Anwendungen auf einmal ausgewählt haben, wird die Schaltfläche zu **Ausgewählte entfernen** und nimmt alle auf einmal heraus.
* **Verfügbare Anwendungen** – alle Anwendungen mit einem eigenen Fenster, die gerade laufen und noch nicht in der Liste für den automatischen Schlafmodus stehen.
* **Hinzufügen** – fügt die in der Liste der verfügbaren Anwendungen fokussierte Anwendung der Liste der Anwendungen für den Schlafmodus hinzu. Wenn Sie mehrere ausgewählt haben, wird die Schaltfläche zu **Ausgewählte hinzufügen** und fügt alle auf einmal hinzu. Eine hinzugefügte Anwendung verschwindet aus **Verfügbare Anwendungen** und taucht dort wieder auf, sobald Sie sie aus **Anwendungen für den Schlafmodus** entfernen.
* **Anwendungen mit manuell eingeschaltetem Schlafmodus zur Liste hinzufügen** – standardmäßig ausgeschaltet. Ist die Option eingeschaltet, dann wird jede Anwendung, die Sie mit NVDA+Umschalt+S (Standardbelegung, im Tastatur-Layout Laptop NVDA+Umschalt+Z) von Hand schlafen legen, der Liste für den automatischen Schlafmodus hinzugefügt und legt sich von da an von selbst schlafen.
* **Manuell aufgeweckte Anwendungen aus der Liste entfernen** – standardmäßig ausgeschaltet und das Gegenstück zur Option darüber. Ist sie eingeschaltet, dann nimmt das Aufwecken einer Anwendung von Hand mit NVDA+Umschalt+S (Standardbelegung, im Tastatur-Layout Laptop NVDA+Umschalt+Z) diese sofort aus der Liste der Anwendungen für den Schlafmodus heraus, sodass sich NVDA für sie nicht mehr automatisch schlafen legt.

Die beiden Kontrollkästchen sind voneinander unabhängig. Jedes von beiden kann ohne das andere eingeschaltet sein, und beide zusammen einzuschalten ist durchaus sinnvoll: Die Liste folgt dann Ihrem Gebrauch von NVDA+Umschalt+S (Standardbelegung, im Tastatur-Layout Laptop NVDA+Umschalt+Z) in beide Richtungen – sie wächst, während Sie Anwendungen zum Schweigen bringen, und schrumpft, während Sie sie wieder sprechen lassen.

Es wird nichts geändert, solange Sie nicht auf OK oder Übernehmen klicken; Abbrechen lässt Ihre Einstellungen genau so, wie sie waren.

Gespeichert und verglichen wird der Name, unter dem NVDA die Anwendung kennt, also der Name der ausführbaren Datei ohne ihre Endung – `firefox`, `notepad`, `explorer` und so weiter. Eine Anwendung in die Liste für den automatischen Schlafmodus aufzunehmen gilt für die gesamte Anwendung, nicht nur für das eine Fenster, dessen Titel gerade angezeigt wird.

Die Erweiterung berücksichtigt Konfigurationsprofile, sodass Ihre Einstellungen für jedes einzelne davon getrennt gespeichert werden.

## Lizenz

Diese Erweiterung unterliegt der GNU General Public License, Version 2. Einzelheiten finden Sie in der Datei COPYING.txt.

## Mitwirken

Wenn Sie zur Entwicklung der Erweiterung beitragen möchten, indem Sie Übersetzungen beisteuern, Fehler melden oder einen Pull Request eröffnen, können Sie [dies im GitHub-Repository der Erweiterung tun](https://github.com/4sensegaming/autosleep-mode). Jeder Beitrag ist willkommen und wird geschätzt.

## Änderungsprotokoll

### Version 1.0, 2026/09/05
* Erste Version
