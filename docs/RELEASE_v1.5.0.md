# Quasar v1.5.0 Release Notes

**Release Date:** 2026-01-15  
**Codename:** Structs  
**Test Count:** 854

---

## 🎉 Highlights

This release introduces **User Defined Types (Structs)**, enabling developers to create custom data structures with named fields.

---

## ✨ New Features

### Struct Declaration
Define custom types with the `struct` keyword:

```quasar
struct Player {
    name: str,
    hp: int,
    xp: int
}
```

**Compiles to Python:**
```python
@dataclass
class Player:
    name: str
    hp: int
    xp: int
```

### Struct Instantiation
Create instances using named field syntax:

```quasar
let hero: Player = Player { name: "Alice", hp: 100, xp: 0 }
```

### Member Access & Modification
Read and write fields using dot notation:

```quasar
let name: str = hero.name  # Read
hero.hp = 80               # Write
```

### Nested Structs
Structs can contain other structs with deep access:

```quasar
struct Point { x: int, y: int }
struct Rect { top_left: Point, width: int, height: int }

let r: Rect = Rect { top_left: Point { x: 0, y: 0 }, width: 10, height: 5 }
let x: int = r.top_left.x  # Deep access
```

### Arrays of Structs
Combine structs with lists:

```quasar
let users: [User] = [User { id: 1 }, User { id: 2 }]
let first_id: int = users[0].id
```

---

## 📚 New Examples

| Example | Description |
|---------|-------------|
| `rpg.qsr` | Mini RPG system with Player/Enemy structs |
| `geometry.qsr` | Nested structs with Point/Rect |

---

## ⚠️ Known Constraints

> **Reserved Keyword Field Names**  
> Field names cannot be reserved keywords (e.g., `end`, `for`, `if`).  
> Use synonyms like `finish` instead of `end`.

---

## 📊 Test Summary

| Component | Tests |
|-----------|-------|
| Phase 8.0 (Declaration) | 8 |
| Phase 8.1 (Instantiation) | 13 |
| Phase 8.2 (Member Access) | 12 |
| Phase 8.3 (Nested/Integration) | 13 |
| **Total Suite** | **854** |

---

## 🔄 Migration Notes

No breaking changes from v1.4.0. Existing code will work unchanged.

---

## 🔮 What's Next

- Phase 9: Methods on Structs (`fn Player.heal()`)
- Phase 10: Enums
