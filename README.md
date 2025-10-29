# 🧠 ao1codes' Brainrot Esolang

A playful little esolang where commands like rizz, yeet, and sus control a number. Write loops, print values, and mess with the accumulator to make fun programs.

---

# Features

* 12+ Gen Z slang commands that change an integer accumulator
* Line-by-line parser ignoring blanks and comments (#)
* Nested loops with vibe and unvibe
* Skip next command if accumulator is zero (sus)
* Prints accumulator with skibidi
* Debug mode for command tracing

---

# Installation & Running

1. Clone this repo
   ```bash
   git clone https://github.com/ao1codes/brainrot_esolang.git
   cd brainrot_esolang
   ```

2. Run a Brainrot program with Python 3
   ```bash
    python3 brainrot.py examples/hello_world.brainrot
   ```

3. Add --debug to trace commands
   ```bash
    python3 brainrot.py --debug examples/hello_world.brainrot
   ```
   
---

# Commands Cheat Sheet

- `rizz` — Increment accumulator by 1  
- `gyatt` — Decrement accumulator by 1  
- `drip` — Increment accumulator by 5  
- `npc` — Decrement accumulator by 5  
- `lit` — Increment accumulator by 10  
- `slaps` — Decrement accumulator by 10  
- `yeet` — Multiply accumulator by 2  
- `flex` — Push accumulator squared onto stack (does NOT modify accumulator)  
- `fam` — Push accumulator onto stack  
- `clapback` — Pop from stack into accumulator  
- `cringe` — Integer divide accumulator by 2 if not zero  
- `spill` — Prompt user for integer input and replace accumulator  
- `skibidi` — Print current accumulator value  
- `no cap` — Reset accumulator to 0  
- `sus` — If accumulator is 0, skip next command  
- `suspect` — If accumulator is greater than 0, skip next command  
- `vibe` — Start loop (while accumulator > 0)  
- `unvibe` — End loop (jump back if accumulator > 0)  
- `func <name>` - Define function 
- `endfunc` - End function 
- `call <name>` - Call function 
- `return` - Return from function
- `load <filename>` — Include and run another Brainrot file  
- `set <varname>` — Store accumulator value in a variable  
- `get <varname>` — Load variable value into accumulator  
- `mid` — No-op (comment / ignore)  

---

# Example snippet

```brainrot
no cap
drip
rizz
vibe
skibidi
gyatt
unvibe
```

**Expected output:**

```
6
5
4
3
2
1
```

---
