# Gauntlet Customizer Standalone UE4SS Mod
**For Dauntless 1.14.7 (offline / Dauntless Forever)**

A fully detached, modular UE4SS mod that expands Gauntlet Mode into a complete sandbox customizer:
* **Dynamic Density**: Scale any round to 1 (Solo), 2 (Dual), 3 (Trio), or 4 (Brawl) Behemoths.
* **Custom Seasons**: Play any encounter specification across Seasons 1, 2, 3, 4, and 5.
* **Level & Round Tuning**: Configure per-level starting match timer, Behemoth Level (1 to 100), arena layouts, and stacked hunt modifiers.
* **1000-Level Expansion**: Expands encounter rows natively up to 1000 unique levels without engine looping.
* **L100 Native Power Scaling**: Includes an expanded `exploration_enemy_level_table` with full CityHash64 Name Map hashes, enabling native combat scaling and Mastery rewards up to Level 100.
* **Hunt Board Unlocking**: Automatically unlocks all 100-level chunks on the Hunt Board.
* **Procedural Custom Season Generator**: Generates full custom campaigns with elemental themes (Frostfall, Inferno, Shock Surge, Keystone Rush), milestone bosses, and custom level curves.

---

## In-Game Controls (UE4SS)

| Hotkey | Action |
| :--- | :--- |
| **`F7`** | **Open Gauntlet Customizer UI**: Launches the web customizer in your browser (`http://127.0.0.1:8799`). |
| **`F6`** | **Active Behemoths Diagnostic**: Prints all active Behemoths, class names, and (X, Y, Z) coordinates in the arena into `UE4SS.log`. |

### In-Game Console Commands (`~` or `Ctrl+O`)
* `gauntlet_open`: Opens the customizer UI.
* `gauntlet_log`: Logs active Behemoths in the arena.
* `gauntlet_status`: Displays mod status and hotkey info.

---

## Outside the Game (Standalone Configurator)
You can customize your Gauntlet settings without launching the game:
1. Double-click `LaunchCustomizer.bat` in this folder.
2. The customizer will open automatically in your browser at `http://127.0.0.1:8799`.
3. Tweak your settings, click **Save & Apply**, and the custom `.pak` will be compiled and mounted into your game's `Archon/Content/Paks` directory immediately!

---

## Installation & Portability
To use this mod:
1. Ensure UE4SS is installed (in the launcher: **Mods > Get UE4SS**).
2. Place the `GauntletCustomizer` folder into:
   ```
   <Game>\Archon\Binaries\Win64\ue4ss\Mods\GauntletCustomizer
   ```
3. Make sure `enabled.txt` is present or enable `GauntletCustomizer` in `mods.txt`.
