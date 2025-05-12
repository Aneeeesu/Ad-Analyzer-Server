This program is a YAML-driven automation runner that simulates user behavior across different applications (e.g., TikTok, Novinky.cz) and systems.
---
```
python3 main.py [test-description file path]
```
if no path is provided it will use ./test-description.yaml
## Structure of Input YAML

Example yaml file:


```yaml
#Used for doomscroll and search action in tiktok
Labels:
  - girlfriend
  - counter-strike
  - Anime
  - else
  - Cats
  - Dogs


#Ad labels to identify
AdLabels:
  - reklama na vzdělávání
  - reklama na aplikace
  - reklama na oblečení a doplňky

#Actions to execute with arguments
Tasks:
- Action: Doomscroll
  Application: TikTok
  Device: 8ad45a96
  Action_args:
    - Anime
  #End conditions are optional If not provided the action will be executed once
  Conditions:
    - Type: Timeout
      Timeout: 500

#Events to execute with arguments
#They were not ever used in actual testing as they would be annyoing to set up and provide barely any benefit
Events:
- Action: SendMessage
  Application: TikTok
  Action_args:
    - "User"
    - "Still TikTok doesn't allow us to text?"
  TriggerConditions:
    - Type: Timeout
      Timeout: 120
```

---

## Supported Applications & Actions

Each application provides a mapping of actions via `getActionMap()`:

### Tiktok
  - OpenDM(username)
  - SendDM(message)
  - GoToHome
  - SwipeDown
  - SwipeUp
  - GoToMessages
  - GoToProfile
  - Like
  - Search(searchedLabel)
  - Doomscroll(likedLabel)
  - SendMessage(Username,MessageContent)

### Novinky.cz
  - Open
  - GoThroughAds

### System
  - WakeUp

### Misc
  - MarkEvent
  - Sleep
  - PlaySound

---

## Supported Conditions

Conditions determine whether an action/event should execute:
  - MarkEvent(Id: int)
  - Timeout(Timeout: int)
  - Percentage(Percentage: float, Label: str, Timeout: float)


Each condition is a function with defined expected argument types.


## Preparing the Environment

```bash
# Prepare the environment
# I recommend using a virtual environment however if you already have compatible pytorch it could save disk space
pip install -r requirements.txt
```
## Execution

Run the program with or without a YAML file:
```bash
python main.py
# or
python main.py ./my_tasks.yaml
```

## Tested Platforms
This project was tested on:

Archlinux with kernel Linux 6.14.6-arch1-1 and a AMD Radeon RX 9070 XT (replacing the cuda pytorch with ROCm alternative)

However project and most experiments ran on Ubuntu 22.04 LTS in WSL with a nVidia 3060 mobile GPU