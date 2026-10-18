# Technical Specification & Parametric Blueprint: Heavy-Duty Modular Playroom Couch / Bench / Table

## 1. Project Context & Functional Requirements
- **Primary Use Case:** Multi-functional basement rec/playroom furniture acting as a deep lounging couch, bench, and flat play/coffee table.
- **Load Requirements:** Dynamic impact loads (kids jumping) + static multi-adult seating (>1,000 lbs capacity across an 80-inch span with zero front-center leg).
- **Under-Bench Storage:** Minimum 15.5" vertical clearance and unobstructed 71.5" front horizontal span for soft storage baskets.
- **Cushion Retention:** Sunken 3/4" birch plywood deck creating a 1.0" recessed lip/tray around the perimeter to hold a 4" high-density foam cushion without Velcro.
- **Mobility ("Wheelbarrow" Mechanism):** 
  - Rear 3 legs have recessed mortise rollers protruding `0.375"` (3/8") from the bottom of the posts.
  - Front 2 legs have high-friction `0.375"` (3/8") rubber pads.
  - Lifting the front apron by 1" transfers weight to the rear rollers for effortless repositioning while remaining 100% locked under dynamic jumping loads.
- **Modularity:** Two independent 40" wide slanted backrests (`10°` recline) that drop vertically into four captive wooden mortise sleeves behind the main back rail and lift out cleanly for table mode.
- **Aesthetics:** Exterior wrapped in stain-grade 1x4 hardwood/select pine with mitered corners. All structural fasteners are hidden on the interior.

---

## 2. Global Coordinate System & Lumber Standards
For programmatic CAD/drawing generation, use a right-handed Cartesian coordinate system (units in **inches**):
- **X-Axis (Length / Left-to-Right):** `0.00"` to `80.00"`
- **Y-Axis (Depth / Front-to-Back):** `0.00"` (Front exterior face) to `29.00"` (Rear exterior face of base). *Note: Slanted backrest extends to `Y ≈ 32.13"` at top.*
- **Z-Axis (Height / Floor-to-Top):** `0.00"` (Floor plane) to `19.00"` (Top of outer apron trim).

### Nominal vs. Actual Lumber Dimensions Used in Math
- `4x4 Post`: `3.50" × 3.50"`
- `2x4 Stud`: `1.50" × 3.50"`
- `2x6 Board`: `1.50" × 5.50"`
- `1x4 Trim`: `0.75" × 3.50"`
- `1x2 Trim/Cleat`: `0.75" × 1.50"`
- `3/4" Birch Plywood`: `0.75"` thickness

---

## 3. Y-Axis & Z-Axis Stackup Reconciliation (Exact Math)

### 3.1 Y-Axis (Front-to-Back Depth = `29.00"` Total Base)
| Layer | Y-Start (`in`) | Y-End (`in`) | Thickness (`in`) | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Front Trim Apron** | `0.00` | `0.75` | `0.75` | 1x4 Stain-grade front face (mitered at corners) |
| **Front Laminated Beam** | `0.75` | `3.75` | `3.00` | Dual laminated 2x4s (`1.5" + 1.5"`), seated in front 4x4 notches |
| **Interior Joist Span** | `3.75` | `23.75` | `20.00` | 5x 2x4 cross-joists (`20.00"` long). *Note: Plywood deck spans `Y=0.75` to `Y=24.75` (`24.00"` deep)* |
| **Main Structural Back Rail**| `23.75` | `25.25` | `1.50` | Single 2x4 (`78.50"` long) seated in notches of the 3 rear 4x4 legs |
| **Mortise Pocket Channel** | `25.25` | `26.75` | `1.50` | Houses the 4 vertical drop-in slots (`3.5"` wide) + 6 spacer blocks |
| **Rear Pocket Backer Rail** | `26.75` | `28.25` | `1.50` | Single 2x4 (`78.50"` long) closing the rear of the mortise sleeves |
| **Rear Trim Apron** | `28.25` | `29.00` | `0.75` | 1x4 Stain-grade rear face (mitered at corners) |

### 3.2 Z-Axis (Vertical Height = `19.00"` Base Frame)
| Feature | Z-Start (`in`) | Z-End (`in`) | Height (`in`) | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Pads & Rollers** | `0.000` | `0.375` | `0.375` | Front 3/8" rubber grip pads; Rear 3/8" roller wheel protrusion |
| **4x4 Wood Legs** | `0.375` | `18.250`| `17.875`| Cut length `17.875"` (17-7/8"). Top ends flush with top of 2x4 frame |
| **Clear Under-Bench Span** | `0.000` | `14.750`| `14.750` (structural) / `15.500` (visual) | Wait—see Adjustment Note below for exact `15.50"` clearance! |

#### **Z-Axis Adjustment for Strict `15.50"` Under-Bench Clearance:**
To guarantee **exact `15.50"` floor-to-beam clearance** underneath while maintaining a `1.00"` recessed cushion pocket:
- **Floor to Bottom of 2x4 Frame / Trim:** `Z = 0.00"` to `Z = 15.50"` (**15.50" Clear Basket Height**)
- **2x4 Structural Rails & Joists:** `Z = 15.50"` to `Z = 19.00"` (`3.50"` height)
- **4x4 Leg Total Height (Pad + Wood):** `19.00"` (`0.375"` pad/roller + `18.625"` wood post, top flush with 2x4 frame at `Z = 19.00"`)
- **3/4" Birch Plywood Deck (Recessed Inside Frame):**
  - Instead of sitting *on top* of the 2x4s, the plywood deck sits **flush with the top of the 2x4s** (`Z = 18.25"` to `Z = 19.00"`) by dropping the 5 interior joists `0.75"` below the top of the front/back rails (`Z = 14.75"` to `Z = 18.25"`), OR by stepping the outer `1x4` trim up by `1.00"`.
  - **Cleanest Method (Stepped Outer Trim):**
    - 2x4 Frame sits at `Z = 15.50"` to `Z = 19.00"`.
    - 3/4" Birch Plywood Deck sits directly on top of the 2x4 ladder frame (`Z = 19.00"` to `Z = 19.75"`).
    - Outer Stain-Grade Trim uses **1x6 ripped to `4.75"`** (or standard **1x6 = `5.50"`**), spanning `Z = 15.25"` to `Z = 20.75"`.
    - **Alternative (Zero-Rip Standard `1x4` Trim Method):**
      - 2x4 Frame sits at `Z = 15.50"` to `Z = 19.00"`.
      - Interior joists & plywood deck are hung `0.25"` below rail tops so Plywood top is at `Z = 19.00"`.
      - Standard `1x4` (`3.50"`) trim is mounted from `Z = 16.50"` to `Z = 20.00"` (leaving `1.00"` lip above the plywood at `Z = 19.00"` to `20.00"`, and exposing `1.00"` of the bottom of the 2x4, OR using `1x6` trim from `Z = 14.50"` to `Z = 20.00"`).
  - **Locked-In Canonical Z-Spec (Using Standard Un-ripped Lumber + Ledger):**
    - `Z = 0.00"` to `15.50"`: Open under-bench clearance (`15.50"`).
    - `Z = 15.50"` to `19.00"`: 2x4 Perimeter Frame (`3.50"` tall).
    - `Z = 15.50"` to `17.75"`: Joists (`2x3` or notched `2x4` hung on internal `1x2` ledger strip so joist tops are at `Z = 17.75"`).
    - `Z = 17.75"` to `18.50"`: 3/4" Birch Plywood Deck (`76.50" × 23.00"`), resting on top of the inner Front Beam (`Y=2.25..3.75`) and joists.
    - `Z = 16.00"` to `19.50"`: Outer `1x4` (`3.50"`) Trim Apron, creating a **`1.00"` Cushion Pocket** (`Z = 18.50"` to `Z = 19.50"`).

---

## 4. Component Inventory & Parametric Bounding Boxes

### 4.1 Legs (`4x4` Posts — `3.50" × 3.50" × 18.625"` Wood + `0.375"` Foot = `19.00"` Total)
1. **Leg_FL (Front-Left):**
   - `X`: `[0.75, 4.25]`, `Y`: `[0.75, 4.25]`, `Z`: `[0.375, 19.00]`
   - **Joinery Notch:** Top front face notched `3.00"` deep (`Y = 0.75..3.75`) × `3.50"` tall (`Z = 15.50..19.00`) to receive the dual laminated Front Beam, OR notched `1.50"` deep (`Y = 0.75..2.25`) for the outer front 2x4 while the inner front 2x4 (`Y = 2.25..3.75`) butts between the front legs (`70.00"` long) on a ledger.
   - *Structural Choice:* Notch `Y = [0.75, 2.25]`, `Z = [15.50, 19.00]` (`1.50"` deep × `3.50"` tall). This leaves a solid `2.00" × 3.50"` vertical post tenon behind the notch!
2. **Leg_FR (Front-Right):**
   - `X`: `[75.75, 79.25]`, `Y`: `[0.75, 4.25]`, `Z`: `[0.375, 19.00]`
   - **Joinery Notch:** `Y = [0.75, 2.25]`, `Z = [15.50, 19.00]`.
3. **Leg_BL (Back-Left):**
   - `X`: `[0.75, 4.25]`, `Y`: `[23.75, 27.25]`, `Z`: `[0.375, 19.00]`
   - **Joinery Notch:** Front face notched at `Y = [23.75, 25.25]`, `Z = [15.50, 19.00]` to carry the Main Back Rail. Rear face notched `Y = [26.75, 28.25]`, `Z = [15.50, 19.00]` (or shifted so leg sits at `Y = [23.25, 26.75]`).
   - *Optimal Rear Leg Y-Position:* Place all 3 Rear Legs at `Y = [21.75, 25.25]`. Notch the rear face `Y = [23.75, 25.25]`, `Z = [15.50, 19.00]` to cradle the Main Back Rail (`Y = 23.75..25.25`). This leaves `Y = [25.25, 28.25]` completely clear for the drop-in backrest pockets!
4. **Leg_BC (Back-Center — 5th Leg):**
   - `X`: `[38.25, 41.75]`, `Y`: `[21.75, 25.25]`, `Z`: `[0.375, 19.00]`
   - **Joinery Notch:** `Y = [23.75, 25.25]`, `Z = [15.50, 19.00]`.
5. **Leg_BR (Back-Right):**
   - `X`: `[75.75, 79.25]`, `Y`: `[21.75, 25.25]`, `Z`: `[0.375, 19.00]`
   - **Joinery Notch:** `Y = [23.75, 25.25]`, `Z = [15.50, 19.00]`.

### 4.2 Structural Frame (`2x4` Lumber — `Z = [15.50, 19.00]`)
- **Front_Rail_Outer:** `78.50" × 1.50" × 3.50"`
  - `X`: `[0.75, 79.25]`, `Y`: `[0.75, 2.25]`, `Z`: `[15.50, 19.00]` (Rests inside the front leg notches).
- **Front_Rail_Inner:** `71.50" × 1.50" × 2.75"` (Ripped to `2.75"` tall so the `0.75"` plywood deck rests directly on top of it from `Z = 18.25"` to `19.00"`!)
  - `X`: `[4.25, 75.75]`, `Y`: `[2.25, 3.75]`, `Z`: `[15.50, 18.25]`. Glued and lag-screwed continuously to `Front_Rail_Outer`.
- **Main_Back_Rail:** `78.50" × 1.50" × 3.50"`
  - `X`: `[0.75, 79.25]`, `Y`: `[23.75, 25.25]`, `Z`: `[15.50, 19.00]` (Rests inside the 3 rear leg notches).
- **Side_Rail_Left:** `19.50" × 1.50" × 3.50"`
  - `X`: `[0.75, 2.25]`, `Y`: `[4.25, 23.75]`, `Z`: `[15.50, 19.00]`.
- **Side_Rail_Right:** `19.50" × 1.50" × 3.50"`
  - `X`: `[77.75, 79.25]`, `Y`: `[4.25, 23.75]`, `Z`: `[15.50, 19.00]`.
- **Interior_Cross_Joists (Qty 5):** `20.00" × 1.50" × 2.75"` (or standard `3.50"` joists mounted `0.75"` lower at `Z = [14.75, 18.25]`)
  - `Y`: `[3.75, 23.75]`, `Z`: `[14.75, 18.25]`
  - `X` Centers: `16.00"`, `28.00"`, `40.00"`, `52.00"`, `64.00"`.

### 4.3 Drop-In Backrest Pocket Assembly (`Y = [25.25, 28.25]`, `Z = [15.50, 19.00]`)
- **Rear_Pocket_Backer_Rail:** `78.50" × 1.50" × 3.50"`
  - `X`: `[0.75, 79.25]`, `Y`: `[26.75, 28.25]`, `Z`: `[15.50, 19.00]`.
- **4 Vertical Receiver Slots (`3.50"` wide along X × `1.50"` deep along Y × `3.50"` tall along Z):**
  - **Slot 1 (Left-Outer):** `X = [6.00, 9.50]`
  - **Slot 2 (Left-Inner):** `X = [30.50, 34.00]`
  - **Slot 3 (Right-Inner):** `X = [46.00, 49.50]`
  - **Slot 4 (Right-Outer):** `X = [70.50, 74.00]`
- **Pocket Spacer Blocks (`2x4` blocks, `1.50"` thick along Y = `[25.25, 26.75]`, `Z = [15.50, 19.00]`):**
  - `Spacer_1`: `X = [0.75, 6.00]` (`5.25"` long)
  - `Spacer_2`: `X = [9.50, 30.50]` (`21.00"` long)
  - `Spacer_3 (Center)`: `X = [34.00, 46.00]` (`12.00"` long)
  - `Spacer_4`: `X = [49.50, 70.50]` (`21.00"` long)
  - `Spacer_5`: `X = [74.00, 79.25]` (`5.25"` long)

### 4.4 Recessed Plywood Seat Deck & Cushion Pocket
- **Plywood_Seat_Deck (`3/4" Birch Plywood`):**
  - Dimensions: `75.50"` (X: `2.25..77.75`) × `21.50"` (Y: `2.25..23.75`) × `0.75"` (Z: `18.25..19.00`).
  - *Note:* If using `1x4` outer trim shifted up to `Z = [16.50, 20.00]`, the plywood deck sits directly on top of the un-notched 2x4 frame at `Z = [19.00, 19.75]` (`76.50" × 23.00"`), leaving a `1.00"` cushion lip if `1x6` (`5.50"`) trim is used (`Z = [15.25, 20.75]`).
  - **Recommended CAD Spec:** Use **`1x6` Select Pine/Poplar ripped to `4.50"` height** (or standard `1x6` at `5.50"`) for the Outer Trim Apron (`Z = [15.50, 20.00]`), and put the `0.75"` Birch Plywood Deck directly on top of the flush `2x4` frame (`Z = [19.00, 19.75]`, `X = [0.75, 79.25]`, `Y = [0.75, 24.50]`). That way:
    1. Zero ripping or dropping of `2x4` joists is required—all `2x4` tops are coplanar at `Z = 19.00"`.
    2. The `3/4"` plywood sheet bridges the full `2x4` perimeter (`78.50" × 23.75"`), turning the entire top into a true structural torsion box.
    3. The outer trim rises to `Z = 20.75"`, creating an exact **`1.00"` deep Cushion Pocket** (`Z = 19.75"` to `20.75"`).

### 4.5 Two 40" Modular Drop-In Slanted Backrests
- **Angled Uprights (Qty 4 — Cut from a single `2x6 × 8ft` board):**
  - Total Length: `23.50"`
  - **Bottom Tenon (`Z = 15.50"` to `19.75"`, length `4.25"`):** Straight profile, `3.4375"` (3-7/16") wide along X × `1.4375"` along Y so it drops smoothly into the `3.50" × 1.50"` pocket.
  - **Upper Spine (`Z = 19.75"` to `38.50"`, length `19.25"`):** Starting at `Z = 19.75"`, the front edge cants backward (`+Y`) at **`10.0°`** from vertical.
    - Horizontal setback at top (`19.25" × sin(10°)`): `+3.34"` along Y.
    - Vertical rise (`19.25" × cos(10°)`): `+18.96"` along Z (Top of backrest reaches `Z = 38.71"`).
- **Backrest Panels (Qty 2 — `3/4" Birch Plywood`):**
  - Dimensions: `39.25" Wide × 15.00" Tall × 0.75" Thick`.
  - Mounted to the `10°` angled front faces of the upright pairs, starting `3.50"` above the plywood deck (`Z = 23.25"`) so the `4.00"` seat cushion slides underneath the bottom edge of the backrest panel.

---

## 5. Fastener & Joinery Schedule (Engineering Rules)
1. **4x4 Half-Lap Notches:** Cut `1.50"` deep × `3.50"` tall using circular saw kerf-cutting + chisel cleanup. Glue with Titebond III and secure with 2x `3.0"` GRK R4 `#10` structural screws per joint from the inside.
2. **Front Laminated Beam:** Glue face-to-face and clamp; drive `2.75"` structural screws in a staggered W-pattern every `8.0"` from the interior side.
3. **Joist Connections:** Use 2x `2.5"` heavy-duty pocket screws (`Kreg HD` or `#10` angled screws) + glue at each joist end, plus a `1x2` bottom ledger strip under the front and back rails if joists are inset.
4. **Torsion-Box Deck:** Glue and screw `3/4"` Birch Plywood to all perimeter rails and joists using `#8 × 1.75"` wood screws every `8.0"`.
5. **Blind-Fastened Outer Trim:** Miter ends at `45°`. Glue and screw from the *inside* of the `2x4` rails outward into the back face of the `0.75"` trim using `#8 × 1.875"` screws (penetrates `1.50"` rail + `0.375"` into trim without piercing the exterior face).

---

## 6. Agent / CLI Execution Prompt
> **Instructions for `agy` CLI:**
> 1. **Design Review & Clash Detection:** Parse the coordinate system and bounding boxes in Sections 3 and 4. Verify that:
>    - All 5 legs (`Leg_FL`, `Leg_FR`, `Leg_BL`, `Leg_BC`, `Leg_BR`) have zero volumetric overlap with the 4 vertical backrest receiver slots (`Slot 1..4`).
>    - Under-bench vertical clearance is `>= 15.50"` across the entire front span (`X = 4.25"` to `75.75"`).
>    - Deflection across the `71.50"` clear front span under a `600 lb` center point load (`L/360` standard) is within structural limits given the laminated `2x4` + `3/4"` plywood torsion deck + `1x6` trim composite beam.
> 2. **Programmatic Drawing Generation:** Generate a parametric CAD script (e.g., Python `svgwrite` / `matplotlib` multi-view orthographic blueprint OR `OpenSCAD` / `CadQuery` 3D model) containing:
>    - **View 1: Front Elevation (`X-Z` plane)** showing the 71.5" clear basket opening, recessed cushion pocket, and split 40" backrests.
>    - **View 2: Right Side Cross-Section (`Y-Z` plane)** detailing the half-lap 4x4 notches, laminated front beam, torsion-box plywood deck, 1" cushion lip, rear mortise pocket sleeve, 10° angled 2x6 backrest post, and 3/8" wheelbarrow roller/pad geometry.
>    - **View 3: Top Plan View (`X-Y` plane, exploded deck)** showing the 5-leg layout, 5 cross-joists, and 4 receiver slot coordinates along the back rail.
>    - **View 4: 2x6 Nested Cut Diagram** showing how to nest the four `23.50"` angled backrest posts out of a single `96.00" × 5.50"` (`2x6`) board.