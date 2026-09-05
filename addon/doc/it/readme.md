# Modalità riposo automatica

[English](../en/readme.md) | [Čeština](../cs/readme.md) | [Deutsch](../de/readme.md) | **Italiano** | [Slovenčina](../sk/readme.md)

* Autore: Lukáš Hosnedl
* Versione minima di NVDA: 2026.1
* Ultima versione di NVDA testata: 2027.1

**Creato da un'intelligenza artificiale, progettato e collaudato a fondo da esseri umani.**

## Descrizione

Se vi è mai capitato di dover attivare spesso la modalità riposo di NVDA per una determinata applicazione o per più applicazioni, questo add-on fa per voi.
Permette a NVDA di ricordare le applicazioni che volete usare con la modalità riposo, così non dovrete più attivarla manualmente.

Molte applicazioni pensate per i non vedenti dispongono di una sintesi vocale propria, oppure inviano i loro messaggi direttamente agli screen reader. In queste applicazioni lo screen reader non ha bisogno di monitorare di continuo le loro finestre alla ricerca di cambiamenti, dato che non legge nulla di sua iniziativa. Attivare la modalità riposo in queste applicazioni può quindi essere utile: garantisce che nessun annuncio vada perso perché NVDA vi ha parlato sopra, ad esempio leggendo una notifica in arrivo, e che nessuna voce aggiuntiva dello screen reader interrompa mai il funzionamento dell'applicazione.

Tenete però presente che, quando la modalità riposo è attiva, NVDA non elabora i propri comandi e non vi risponde. Per usarli dovrete disattivarla di nuovo, oppure passare temporaneamente a un'altra applicazione.

Un altro possibile problema con le applicazioni dotate di sintesi propria o che comunicano direttamente con gli screen reader sono le opzioni **I caratteri digitati interrompono la voce** e **Il tasto invio interrompe la voce**, che si trovano nelle impostazioni della tastiera di NVDA. Se una delle due è attivata, premete un tasto che ne innesca il comportamento e non avete messo NVDA in riposo per quell'applicazione, le vostre pressioni di tasti di fatto troncano la voce dello screen reader. Il risultato può essere che vi sfugga un messaggio che avreste voluto sentire. Una possibile soluzione è disattivare manualmente l'interruzione della voce durante la digitazione per quella specifica applicazione, oppure creare un profilo di configurazione dedicato.

La modalità riposo integrata in NVDA, unita a questo add-on, elimina però del tutto e definitivamente ogni scomodità del genere, perché quando NVDA è in riposo le pressioni dei tasti non interrompono affatto la voce, compresa quella generata direttamente dall'applicazione.

## Utilizzo

Questo add-on non ha bisogno di comandi propri. Una volta che un'applicazione si trova nell'[elenco delle applicazioni da mettere in riposo](#impostazioni), basta passare a essa: NVDA rileva la nuova finestra in primo piano, riconosce l'applicazione e va in riposo per lei.

L'add-on non disattiva mai la modalità riposo. Essa si comporta come si è sempre comportata: resta attiva finché non la disattivate con NVDA+maiusc+S (impostazione predefinita, con il layout della tastiera laptop NVDA+maiusc+Z), finché l'applicazione non viene chiusa, finché non la rimuovete dall'elenco delle applicazioni da mettere in riposo, oppure finché non passate a un'altra applicazione.

## Impostazioni

L'add-on aggiunge la categoria **Modalità riposo automatica** alla finestra Impostazioni di NVDA (menu NVDA, Preferenze, Impostazioni). Contiene:

* **Applicazioni da mettere in riposo** – l'elenco delle applicazioni per le quali volete che NVDA vada in riposo. È vuoto per impostazione predefinita.
* **Rimuovi** – rimuove dall'elenco l'applicazione che ha il focus, così NVDA non andrà più in riposo per essa. Se avete selezionato più applicazioni insieme, il pulsante diventa **Rimuovi selezionate** e le toglie tutte in una volta.
* **Applicazioni disponibili** – tutte le applicazioni dotate di finestra che sono in esecuzione in questo momento e non sono ancora nell'elenco per il riposo automatico.
* **Aggiungi** – inserisce l'applicazione che ha il focus nell'elenco delle applicazioni disponibili nell'elenco delle applicazioni da mettere in riposo. Se ne avete selezionate più di una, il pulsante diventa **Aggiungi selezionate** e le inserisce tutte in una volta. Un'applicazione aggiunta scompare da **Applicazioni disponibili** e vi ricompare non appena la rimuovete da **Applicazioni da mettere in riposo**.
* **Aggiungi all'elenco le applicazioni messe in riposo manualmente** – disattivata per impostazione predefinita. Quando è attiva, ogni applicazione che mettete in riposo a mano con NVDA+maiusc+S (impostazione predefinita, con il layout della tastiera laptop NVDA+maiusc+Z) viene aggiunta all'elenco per il riposo automatico, e da quel momento andrà in riposo da sola.
* **Rimuovi dall'elenco le applicazioni riattivate manualmente** – disattivata per impostazione predefinita, ed è l'immagine speculare dell'opzione precedente. Quando è attiva, riattivare a mano un'applicazione con NVDA+maiusc+S (impostazione predefinita, con il layout della tastiera laptop NVDA+maiusc+Z) la toglie immediatamente dall'elenco delle applicazioni da mettere in riposo, così NVDA non andrà più in riposo automaticamente per essa.

Le due caselle di controllo sono indipendenti tra loro. Ciascuna può essere attiva senza l'altra, e tenerle attive entrambe ha perfettamente senso: l'elenco segue allora il vostro uso di NVDA+maiusc+S (impostazione predefinita, con il layout della tastiera laptop NVDA+maiusc+Z) in entrambe le direzioni, crescendo man mano che silenziate le applicazioni e riducendosi man mano che tornate a farle parlare.

Nulla viene modificato finché non premete OK o Applica; Annulla lascia le vostre impostazioni esattamente com'erano.

Ciò che viene memorizzato e confrontato è il nome con cui NVDA conosce l'applicazione, cioè il nome del file eseguibile senza estensione – `firefox`, `notepad`, `explorer` e così via. Aggiungere un'applicazione all'elenco per il riposo automatico vale per l'intera applicazione, non solo per quell'unica finestra il cui titolo viene mostrato in quel momento.

L'add-on rispetta i profili di configurazione, quindi le vostre impostazioni vengono salvate per ciascuno di essi separatamente.

## Licenza

Questo add-on è coperto dalla GNU General Public License, versione 2. Per i dettagli consultate il file COPYING.txt.

## Contribuire

Se desiderate contribuire allo sviluppo dell'add-on fornendo traduzioni, segnalando problemi o aprendo una pull request, potete [farlo nel suo repository su GitHub](https://github.com/4sensegaming/autosleep-mode). Ogni contributo è benvenuto e apprezzato.

## Registro delle modifiche

### Versione 1.0, 2026/09/05
* Prima versione
