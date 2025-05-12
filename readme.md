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
  ...

#Actions to execute with arguments
Tasks:
- Action: Doomscroll
  Application: TikTok
  Device: 8ad45a96
  Action_args:
    - Anime
  Conditions:
    - Type: Timeout
      Timeout: 500


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

---

## Execution

Run the program with or without a YAML file:

```bash
python main.py
# or
python main.py ./my_tasks.yaml
```

The system will:

1. Parse the YAML.
2. Resolve actions and arguments based on app-specific maps.
3. Evaluate conditions before executing each task.
4. Log and perform the defined behavior over time.
