# 🎮 How to Submit Your Own Pokemon Data

This guide explains all the ways you can add custom Pokemon to the database!

---

## 📝 Method 1: Web Form (Easiest!)

Perfect for adding individual Pokemon quickly.

### Steps:

1. **Start the app:**
   ```bash
   python simple_app.py
   ```

2. **Open in browser:**
   ```
   http://localhost:8000
   ```

3. **Go to "Submit Pokemon" tab**

4. **Fill in the form:**
   - **Pokemon Name:** Enter any name (e.g., "MyAwesomePokemon")
   - **Primary Type:** Select from dropdown (required)
   - **Secondary Type:** Optional second type
   - **HP:** Health Points (1-255)
   - **Attack:** Attack stat (1-255)
   - **Defense:** Defense stat (1-255)
   - **Special Attack:** Sp.Atk stat (1-255)
   - **Special Defense:** Sp.Def stat (1-255)
   - **Speed:** Speed stat (1-255)

5. **Click "Submit Pokemon"**

6. **Success!** Your Pokemon is now in the database

### Example:

```
Name: Thunderflare
Primary Type: Electric
Secondary Type: Dragon
HP: 85
Attack: 120
Defense: 75
Special Attack: 145
Special Defense: 90
Speed: 110
```

---

## 📤 Method 2: CSV Upload (Best for Multiple Pokemon)

Perfect for adding many Pokemon at once.

### Steps:

1. **Create a CSV file** using Excel, Google Sheets, or any text editor

2. **Use this format:**
   ```csv
   Name,Type1,Type2,HP,Attack,Defense,Sp_Atk,Sp_Def,Speed
   ```

3. **Add your Pokemon as rows:**
   ```csv
   Name,Type1,Type2,HP,Attack,Defense,Sp_Atk,Sp_Def,Speed
   Thunderflare,Electric,Dragon,85,120,75,145,90,110
   Aquafrost,Water,Ice,90,75,110,95,115,65
   Blazewing,Fire,Flying,78,115,70,125,80,112
   ```

4. **Save the file** (e.g., `my_pokemon.csv`)

5. **Open the app** and go to **Submit Pokemon** tab

6. **Click the upload area** and select your CSV file

7. **Done!** All Pokemon are added

### CSV Template:

Download or copy this template:

```csv
Name,Type1,Type2,HP,Attack,Defense,Sp_Atk,Sp_Def,Speed
YourPokemon1,Fire,,100,120,80,90,85,95
YourPokemon2,Water,Ice,95,85,100,110,105,70
YourPokemon3,Grass,Poison,80,75,90,100,95,85
```

### Important Notes:

- **Don't skip columns** - use empty value for optional Type2
- **Column names must match exactly** (case-sensitive)
- **Stats must be numbers** between 1-255
- **Save as CSV format**, not Excel (.xlsx)

---

## ✏️ Method 3: Direct File Edit (Advanced)

Perfect for developers or when you want direct control.

### Steps:

1. **Open VS Code** and navigate to project folder

2. **Create or edit** a CSV file in `data/pokemon/`

3. **Two options:**

   **Option A: Edit existing sample file**
   ```
   data/pokemon/sample_pokemon.csv
   ```

   **Option B: Create new file**
   ```
   data/pokemon/user_submitted.csv
   ```

4. **Add your Pokemon:**
   ```csv
   Name,Type1,Type2,HP,Attack,Defense,Sp_Atk,Sp_Def,Speed
   Thunderflare,Electric,Dragon,85,120,75,145,90,110
   ```

5. **Save the file**

6. **Restart the app** or reload in browser

### VS Code Tips:

- Use **Rainbow CSV extension** for color-coded columns
- Use **Edit CSV extension** for table view
- Press `Ctrl+S` to save

---

## 🎯 Field Reference

### Required Fields:

| Field | Description | Valid Values | Example |
|-------|-------------|--------------|---------|
| Name | Pokemon name | Any text | "Pikachu" |
| Type1 | Primary type | See types below | "Electric" |
| HP | Hit points | 1-255 | 35 |
| Attack | Physical attack | 1-255 | 55 |
| Defense | Physical defense | 1-255 | 40 |
| Sp_Atk | Special attack | 1-255 | 50 |
| Sp_Def | Special defense | 1-255 | 50 |
| Speed | Speed stat | 1-255 | 90 |

### Optional Fields:

| Field | Description | Valid Values | Example |
|-------|-------------|--------------|---------|
| Type2 | Secondary type | See types below or empty | "Flying" |

### Valid Pokemon Types:

- Normal
- Fire
- Water
- Electric
- Grass
- Ice
- Fighting
- Poison
- Ground
- Flying
- Psychic
- Bug
- Rock
- Ghost
- Dragon
- Dark
- Steel
- Fairy

---

## 💡 Examples

### Single Type Pokemon:

```csv
Name,Type1,Type2,HP,Attack,Defense,Sp_Atk,Sp_Def,Speed
Firefang,Fire,,78,115,70,95,80,102
Hydropump,Water,,85,70,100,110,95,80
Leafstorm,Grass,,75,80,85,105,90,100
```

### Dual Type Pokemon:

```csv
Name,Type1,Type2,HP,Attack,Defense,Sp_Atk,Sp_Def,Speed
Thunderflare,Electric,Dragon,85,120,75,145,90,110
Frostbite,Ice,Water,90,75,110,95,115,65
Rockslide,Rock,Ground,100,125,130,60,70,45
```

### Legendary Pokemon (High Stats):

```csv
Name,Type1,Type2,HP,Attack,Defense,Sp_Atk,Sp_Def,Speed
SkyKing,Flying,Dragon,106,130,90,130,90,95
OceanLord,Water,Psychic,100,100,100,150,140,80
InfernoGod,Fire,Ghost,95,140,90,140,90,115
```

### Starter Pokemon (Balanced Stats):

```csv
Name,Type1,Type2,HP,Attack,Defense,Sp_Atk,Sp_Def,Speed
Grassling,Grass,,45,49,49,65,65,45
Emberpup,Fire,,39,52,43,60,50,65
Aquakid,Water,,44,48,65,50,64,43
```

---

## 🔍 Validating Your Data

### Check in the Web Interface:

1. Go to **Pokemon Data** tab
2. Click **Load All Pokemon**
3. Look for your Pokemon in the grid
4. Verify all stats are correct

### Search for Your Pokemon:

1. Go to **Pokemon Data** tab
2. Enter your Pokemon's name in search
3. Click **Search**
4. Check the results

### Manual Check:

Open the CSV file and verify:
- ✅ All required fields are present
- ✅ Stats are between 1-255
- ✅ Types are spelled correctly
- ✅ No missing commas
- ✅ No extra spaces

---

## 📊 Stat Guidelines

### Balanced Pokemon:
- Total stats: 300-400
- All stats: 40-80

### Strong Pokemon:
- Total stats: 450-550
- All stats: 70-110

### Legendary Pokemon:
- Total stats: 580-720
- All stats: 90-150

### Formula:
```
Total = HP + Attack + Defense + Sp_Atk + Sp_Def + Speed
```

---

## ⚠️ Common Mistakes

### ❌ Wrong Column Names:

```csv
Name,PrimaryType,SecondaryType,Health,Atk,Def,SpAtk,SpDef,Spd
```

### ✅ Correct Column Names:

```csv
Name,Type1,Type2,HP,Attack,Defense,Sp_Atk,Sp_Def,Speed
```

### ❌ Missing Commas:

```csv
Pikachu,Electric,35,55,40,50,50,90
```

### ✅ Correct Format:

```csv
Pikachu,Electric,,35,55,40,50,50,90
```
(Note the empty Type2 field)

### ❌ Stats Out of Range:

```csv
MegaPower,Dragon,,500,300,200,400,350,280
```

### ✅ Valid Stats:

```csv
PowerDragon,Dragon,,150,140,120,150,130,110
```

---

## 🎨 Advanced: Programmatic Submission

If you're a developer, you can submit Pokemon via API:

### Using Python:

```python
import requests
import json

pokemon = {
    "Name": "Thunderflare",
    "Type1": "Electric",
    "Type2": "Dragon",
    "HP": "85",
    "Attack": "120",
    "Defense": "75",
    "Sp_Atk": "145",
    "Sp_Def": "90",
    "Speed": "110"
}

response = requests.post(
    'http://localhost:8000/api/pokemon/submit',
    headers={'Content-Type': 'application/json'},
    data=json.dumps(pokemon)
)

print(response.json())
```

### Using curl:

```bash
curl -X POST http://localhost:8000/api/pokemon/submit \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "Thunderflare",
    "Type1": "Electric",
    "Type2": "Dragon",
    "HP": "85",
    "Attack": "120",
    "Defense": "75",
    "Sp_Atk": "145",
    "Sp_Def": "90",
    "Speed": "110"
  }'
```

### Using JavaScript:

```javascript
const pokemon = {
    Name: "Thunderflare",
    Type1: "Electric",
    Type2: "Dragon",
    HP: "85",
    Attack: "120",
    Defense: "75",
    Sp_Atk: "145",
    Sp_Def: "90",
    Speed: "110"
};

fetch('http://localhost:8000/api/pokemon/submit', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(pokemon)
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## 📁 Where Data is Stored

Your submitted Pokemon are saved to:

```
CodexEterna/
  └── data/
      └── pokemon/
          ├── sample_pokemon.csv      (default data)
          └── user_submitted.csv      (your submissions)
```

Both files are automatically loaded when you start the app!

---

## 🎉 You're a Pokemon Creator!

Now you know how to:
- ✅ Submit Pokemon via web form
- ✅ Upload CSV files
- ✅ Edit CSV files directly
- ✅ Use the API programmatically
- ✅ Validate your data
- ✅ Follow stat guidelines

**Happy Pokemon creating!** 🎮✨
