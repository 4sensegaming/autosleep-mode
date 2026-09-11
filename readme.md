# Autosleep Mode

**English** | [Čeština](addon/doc/cs/readme.md) | [Deutsch](addon/doc/de/readme.md) | [Italiano](addon/doc/it/readme.md) | [Slovenčina](addon/doc/sk/readme.md)

* Author: Lukáš Hosnedl
* Minimum NVDA version: 2026.1
* Last tested NVDA version: 2026.2

**Created by AI, designed and thoroughly tested by humans.**

## Description

If you ever found yourself needing to turn on NVDA's sleep mode for a particular app or several apps often, this add-on is for you.
It lets NVDA remember the apps that you want to use with sleep mode, so you won't have to turn it on manually ever again.

Many blind-centric apps either provide their own self-voicing features, or talk (send their messages) to screen readers directly. In these apps, the screen reader doesn't need to continuously monitor their windows for changes as it doesn't actively read anything. Therefore, turning on sleep mode in these apps can be helpful as it ensures that no utterance is ever missed because NVDA just read e.g. an incoming notification over it, and that no extra screen reader speech at all ever interrupts the app's operation.

Note, though, that when sleep mode is on, NVDA doesn't process and react to its own commands. For that, you will need to turn it off again or temporarily switch away from the app.

Another potential problem with self-voicing apps or apps that communicate with screen readers directly are the options to interrupt speech when either the enter key or any key at all is pressed, which can be found in NVDA's keyboard settings. When either option is enabled, you press a key that triggers the enabled behavior, and you didn't put NVDA to sleep for that app, your key presses are essentially cutting off screen reader speech. This may result in you overhearing a message you may have wanted to hear. A potential solution to this problem is to either disable the typing interrupts for the given app manually or create a configuration profile for it.

However, NVDA's own built-in sleep mode combined with this add-on removes all of that hassle entirely and for good, as key presses do not interrupt speech at all when NVDA is sleeping, including any speech that was triggered directly by the app.

## Usage

This add-on needs no keystrokes of its own. Once an app is on the [apps to sleep list](#settings), switching to it is all it takes: NVDA notices the new foreground window, recognizes the app, and goes to sleep for it.

Sleep mode is never switched off by the add-on. It behaves as it always has: it lasts until you switch it off with NVDA+shift+S (NVDA+shift+Z in the laptop keyboard layout) by default, or until the app is closed, removed from the apps to sleep list, or you switch away from it.

## Settings

The add-on adds an **Autosleep Mode** category to NVDA's Settings dialog (NVDA menu, Preferences, Settings). It contains:

* **Apps to sleep** — the list of apps for which you want NVDA to fall asleep, empty by default.
* **Remove** — removes the focused app from the list so NVDA will no longer go to sleep for this app. If you have selected several apps at once, the button becomes **Remove selected** and takes all of them out at once.
* **Available apps** — all windowed apps that are running right now and are not on the autosleep list yet.
* **Add** — puts the focused app from the available apps list into the apps to sleep list. If you have selected several, the button becomes **Add selected** and puts all of them in at once. An application you add disappears from **Available apps**, and comes back to it if you remove it from **Apps to sleep** again.
* **Add apps with manually activated sleep mode to the autosleep list** — off by default. With it on, every application you put to sleep by hand with NVDA+shift+S (NVDA+shift+Z in the laptop keyboard layout) by default is added to the autosleep list, so it will sleep by itself from then on.
* **Remove manually woken apps from the autosleep list** — off by default, and the mirror image of the option above. With it on, waking an application by hand with NVDA+shift+S (NVDA+shift+Z in the laptop keyboard layout) by default immediately takes it off the apps to sleep list, so NVDA won't autosleep for it again.

The two checkboxes are independent. Either can be on without the other, and having both on is perfectly sensible: the list then follows your use of NVDA+shift+s (NVDA+shift+Z in the laptop keyboard layout) by default in both directions, growing as you silence applications and shrinking as you let them speak again.

Nothing is changed until you press OK or Apply; Cancel leaves your settings exactly as they were.

What's stored and matched is the name NVDA knows the app by, which is the name of the executable without its extension — `firefox`, `notepad`, `explorer`, and so on. Adding an app to the autosleep list works for the whole app, not just the one window whose title currently happens to be displayed.

The add-on respects configuration profiles, so your settings are saved for each one independently.

## Contributing

If you would like to contribute to the add-on's development by providing translations, reporting issues or opening a pull request, and you know how to, you can [do so in its GitHub repository](https://github.com/4sensegaming/autosleep-mode). All contributions are welcome and appreciated.

## Changelog

### Version 1.0, 2026/09/05
* Initial release
