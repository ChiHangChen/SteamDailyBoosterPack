# SteamDailyBoosterPack


# Installation
```
python3 -m pip install ./requirements.txt
```

# Prepapre

## Update config.ini
### username
your steam login username
### password
your steam login password
### inventory_id

Go to your inventory page, right click cursor and select "copy page url"

Paste clipboard content on any broweser, you will see the url like this:
```
https://steamcommunity.com/id/Chihang0711/inventory/
```

`Chihang0711` should be your inventory_id


### APP List 
Paste the game id that you want to generate booster pack, in the example `config.ini`

```
game_id = [292030, 1091500]
```

`292030` is The Witcher 3, and `1091500` is Cyberpunk 2077, you can get the game id one steam game store url.

# Run

Use the following command to run the program

```
python3 SteamMakeBoosterPack.py Q58BG
```

**Q58BG** should be replaced by your steam guard code generated in your steam mobile app.

I suggest you to find an idle computer and run this command in backgroud, and never shut this computer down, so that you only have to enter the steam guard code once, and the program will generate booster pack every day.
