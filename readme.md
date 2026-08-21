# Autosleep Mode

* Author: Lukáš Hosnedl
* Last tested NVDA version: 2026.3

## Description

**Created by AI, designed and thoroughly tested by humans.**

Some applications speak for themselves. Games, media players and other self-voicing software produce their own speech, and NVDA talking over the top of it is at best a distraction. NVDA already has an answer to this — sleep mode, which makes NVDA stay completely quiet inside one application — but you have to switch it on with NVDA+shift+s every single time you go back to that application.

Autosleep Mode does it for you. You list the applications that should be silent, and from then on NVDA puts itself to sleep the moment one of them comes to the foreground, announcing "Sleep mode on" exactly as if you had pressed the keystroke yourself.

## Usage

There is nothing to press. Once an application is on the list, switching to it is all it takes: NVDA notices the new foreground window, sees that the application is one of yours, and goes to sleep for it.

Sleep mode is never switched off again by the add-on. It behaves as it always has: it lasts until you switch it off with NVDA+shift+s, or until the application is closed.

## Settings

The add-on adds an **Autosleep Mode** category to NVDA's Settings dialog (NVDA menu, Preferences, Settings). It contains:

* **Apps to sleep** — the applications that put NVDA to sleep. Empty to begin with. An application that is running appears under the title of its window, just as it does in **Running apps** below; one that is not running has no window to take a title from, and appears under the name of its executable.
* **Remove** — takes the application you are on out of the list. If you have selected several, the button becomes **Remove selected** and takes all of them out at once.
* **Running apps** — the applications running right now that are not on the list yet, each under the title of its window. Only applications with a window of their own are here, the same ones the task switcher offers you, so the background processes that never put anything on the screen stay out of the way. An application whose window carries no title, as a full screen self-voicing game may well not, is listed under the name of its executable instead.
* **Add** — puts the application you are on into the list. If you have selected several, the button becomes **Add selected** and puts all of them in at once. An application you add disappears from **Running apps**, and comes back to it if you remove it from **Apps to sleep** again.
* **Add apps that are put to sleep manually to the autosleep list** — off by default. With it on, every application you put to sleep by hand with NVDA+shift+s joins the list, so it will sleep by itself from then on.
* **Remove manually woken apps from the autosleep list** — off by default, and the mirror image of the option above. With it on, waking an application by hand with NVDA+shift+s also takes it off the list, so it stops sleeping by itself. An application that was never on the list is left alone.

The two options are independent. Either can be on without the other, and having both on is perfectly sensible: the list then follows your use of NVDA+shift+s in both directions, growing as you silence applications and shrinking as you let them speak again.

Both lists take more than one selection at a time, in the usual way: shift with the arrow keys extends the selection, control with the arrow keys and space picks items out one by one. The application you are on is always the selected one, so arrowing to it and pressing the button is all it takes; selecting is only for when you want to act on several at once. Once a button has done its work, focus goes back to the list rather than staying on the button, so you are told where you have ended up instead of being left in silence.

Nothing is changed until you press OK or Apply; Cancel leaves your settings exactly as they were.

## Notes

* What is stored and matched is the name NVDA knows the application by, which is the name of the executable without its extension — `firefox`, `notepad`, `explorer`. The lists show you the title of the application's window over the top of it wherever there is one, since that is the name you see on the application itself, but the title is only a label: it is the whole application that sleeps, not the one window whose title happens to be showing. Titles change as you work, so the same application may well be listed under a different one tomorrow.
* NVDA itself is deliberately left out of **Running apps**. Putting NVDA to sleep inside its own windows would only silence its own interface.
* The list belongs to your configuration profile, so a profile can have a set of applications of its own. Like every other NVDA setting, it is written to disk when NVDA saves its configuration, either on request or when it exits.
* The application in the foreground when NVDA starts is checked once as well, so an application you were already in does not have to be left and returned to.

## License

This add-on is covered by the GNU General Public License, version 2. See the file COPYING.txt for details.
