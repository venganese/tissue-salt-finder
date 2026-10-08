"""Builds the A ∪ B feature set for the 12 Schüssler tissue salts.

A = Schüssler, "An Abridged Therapy" (25th ed., tr. Tafel, 1898)   -> 63810970R.pdf
B = Boericke & Dewey, "The Twelve Tissue Remedies of Schüssler"   -> twelvetissuerem00boer.pdf

Each feature row maps salt -> source ("A", "B" or "AB").
Run:  python3 build_features.py
Out:  features_long.csv, features_matrix.csv, features_matrix.html, features.js
"""
import csv, html, json

SALTS = [  # (key, Schüssler number, short name, full name)
    ("CF", 1, "Calc Fluor", "Calcarea fluorica"),
    ("CP", 2, "Calc Phos", "Calcarea phosphorica"),
    ("FP", 3, "Ferrum Phos", "Ferrum phosphoricum"),
    ("KM", 4, "Kali Mur", "Kali muriaticum (Kalium chloratum)"),
    ("KP", 5, "Kali Phos", "Kali phosphoricum"),
    ("KS", 6, "Kali Sulph", "Kali sulphuricum"),
    ("MP", 7, "Mag Phos", "Magnesia phosphorica"),
    ("NM", 8, "Nat Mur", "Natrum muriaticum"),
    ("NP", 9, "Nat Phos", "Natrum phosphoricum"),
    ("NS", 10, "Nat Sulph", "Natrum sulphuricum"),
    ("SI", 11, "Silicea", "Silicea"),
    ("CS", 12, "Calc Sulph", "Calcarea sulphurica"),
]
KEYS = [s[0] for s in SALTS]


def f(spec):
    """'FP:AB KM:B' -> {'FP': 'AB', 'KM': 'B'}"""
    return dict(p.split(":") for p in spec.split())


# (group, feature, salt->source)
FEATURES = [
    # 1. Where the salt acts (tissue affinity)
    ("Tissue affinity", "Bone surface, tooth enamel, elastic fibres", f("CF:AB")),
    ("Tissue affinity", "Bones, teeth, growth, new cell formation", f("CP:AB")),
    ("Tissue affinity", "Blood (oxygen carrier), muscle walls of vessels", f("FP:AB")),
    ("Tissue affinity", "Fibrin; mucous membranes; glands", f("KM:AB")),
    ("Tissue affinity", "Brain and nerves (nutrition of nerve tissue)", f("KP:AB")),
    ("Tissue affinity", "Skin surface (epidermis) and linings (epithelium)", f("KS:AB")),
    ("Tissue affinity", "Nerves and muscles (contraction / spasm)", f("MP:AB")),
    ("Tissue affinity", "Water distribution in tissues; mucus", f("NM:AB")),
    ("Tissue affinity", "Acid balance (lactic & uric acid); fat digestion", f("NP:AB")),
    ("Tissue affinity", "Removal of excess water; liver, bile, kidneys", f("NS:AB")),
    ("Tissue affinity", "Connective tissue, skin, hair, nails", f("SI:AB")),
    ("Tissue affinity", "Suppuration / healing of discharging wounds", f("CS:B SI:AB")),

    # 2. Stage of inflammation
    ("Inflammation stage", "1st stage: redness, heat, throbbing, fever onset, no discharge yet", f("FP:AB")),
    ("Inflammation stage", "2nd stage: swelling, white/grey fibrinous exudation", f("KM:AB")),
    ("Inflammation stage", "3rd stage: yellow discharge, peeling / desquamation", f("KS:AB")),
    ("Inflammation stage", "Inflamed skin/tissue before pus forms (phlegmonous)", f("NP:AB")),
    ("Inflammation stage", "Pus forming; abscess needs to ripen / come to a head", f("SI:AB")),
    ("Inflammation stage", "Pus with an outlet; discharge goes on too long, slow to heal", f("CS:B")),
    ("Inflammation stage", "Discharge turns foul / septic / gangrenous", f("KP:AB")),
    ("Inflammation stage", "Hard lump (induration) left behind", f("CF:AB")),

    # 3. Discharge / mucus (colour & consistency)
    ("Discharge", "Clear, watery, transparent, frothy (like raw egg-white / boiled starch)", f("NM:AB")),
    ("Discharge", "Albuminous, like white of egg (not watery)", f("CP:AB")),
    ("Discharge", "Thick, white, fibrinous, milky", f("KM:AB")),
    ("Discharge", "Yellow, slimy (sometimes watery)", f("KS:AB")),
    ("Discharge", "Golden-yellow, creamy, honey-coloured", f("NP:AB")),
    ("Discharge", "Green / yellowish-green", f("NS:AB KS:B SI:B")),
    ("Discharge", "Thick yellow pus", f("SI:AB NP:A CS:B")),
    ("Discharge", "Thick, yellow, lumpy (Calc Sulph: may be blood-tinged)", f("CS:B CF:B")),
    ("Discharge", "Foul, fetid, carrion-like smell", f("KP:AB")),
    ("Discharge", "Acrid / excoriating (burns the skin)", f("NM:AB KP:AB")),
    ("Discharge", "Watery exudation that is yellowish", f("NS:AB")),
    ("Discharge", "No discharge at all (dry, red, hot)", f("FP:AB")),

    # 4. Tongue
    ("Tongue", "Clean and red / dark-red swollen", f("FP:AB")),
    ("Tongue", "White or greyish-white coating (not slimy)", f("KM:AB")),
    ("Tongue", "Clean & moist, or frothy bubbles of saliva along the edges", f("NM:AB")),
    ("Tongue", "Yellow, slimy coating", f("KS:AB")),
    ("Tongue", "Moist, creamy, golden-yellow coating at the back", f("NP:AB")),
    ("Tongue", "Dirty brownish-green / greyish-green, bitter taste", f("NS:AB")),
    ("Tongue", "Brownish, like liquid mustard; dry; offensive breath", f("KP:AB")),
    ("Tongue", "Clean tongue with stomach cramps", f("MP:AB")),
    ("Tongue", "Clay-coloured, yellow at base, flabby", f("CS:B")),
    ("Tongue", "Cracked, hardened", f("CF:AB")),
    ("Tongue", "White-furred, swollen, numb or stiff", f("CP:B")),
    ("Tongue", "Hardened / ulcer / feels like a hair on it", f("SI:B")),
    ("Tongue", "Mapped tongue", f("NM:B KM:B")),

    # 5. Character of pain
    ("Pain type", "Throbbing / stitching with heat & redness", f("FP:AB")),
    ("Pain type", "Shooting, lightning-like, boring, cramping, constricting; changes place", f("MP:AB")),
    ("Pain type", "Pain with a paralysed / lame feeling; followed by exhaustion", f("KP:AB")),
    ("Pain type", "Pain with numbness, coldness or crawling (ants) sensation", f("CP:AB")),
    ("Pain type", "Shifting, wandering pains", f("KS:B MP:AB")),
    ("Pain type", "Pain with tears, salivation or vomiting of water", f("NM:AB")),
    ("Pain type", "Pain with vomiting of bile", f("NS:AB")),
    ("Pain type", "Deep pain as if ulcerating; small nodules on scalp", f("SI:AB")),
    ("Pain type", "Dragging, bearing-down pain (relaxed tissues)", f("CF:B")),

    # 6. What makes it worse
    ("Worse from", "Motion", f("FP:AB KM:AB CP:B")),
    ("Worse from", "Light touch", f("MP:AB")),
    ("Worse from", "Cold, cold air, draughts, cold washing", f("MP:B SI:B CP:B")),
    ("Worse from", "Warm / heated room", f("KS:AB")),
    ("Worse from", "Rest, rising from sitting, beginning to move, exertion", f("KP:AB")),
    ("Worse from", "Noise", f("KP:B SI:B")),
    ("Worse from", "Being alone", f("KP:B")),
    ("Worse from", "Damp, wet weather; living near water / damp houses", f("NS:AB CF:B")),
    ("Worse from", "Getting wet; change of weather", f("CP:B")),
    ("Worse from", "Working / washing in water", f("CS:B NS:B")),
    ("Worse from", "Sea-side; cold weather", f("NM:B")),
    ("Worse from", "Thunderstorm", f("NP:B")),
    ("Worse from", "Fatty or rich food, pastry", f("KM:B NP:AB")),
    ("Worse from", "Chilled feet / suppressed foot-sweat", f("SI:AB")),
    ("Worse from", "Lying on left side", f("NS:B")),
    ("Worse from", "Consolation", f("NM:B")),

    # 7. What makes it better
    ("Better from", "Cold applications / cold drinks", f("FP:AB")),
    ("Better from", "Warmth, heat, hot drinks", f("MP:AB SI:B")),
    ("Better from", "Pressure, bending double, rubbing", f("MP:AB")),
    ("Better from", "Cool, open air", f("KS:AB")),
    ("Better from", "Gentle motion; eating; company; pleasant excitement", f("KP:AB")),
    ("Better from", "Lying down", f("CP:B")),
    ("Better from", "Lying on something hard (backache)", f("NM:B")),
    ("Better from", "Warm, dry weather", f("NS:B")),
    ("Better from", "Wrapping up warmly (esp. the head)", f("SI:B")),
    ("Better from", "Sleep", f("FP:B")),

    # 8. Time / side
    ("Time & side", "Worse in the evening", f("KS:AB NP:B")),
    ("Time & side", "Worse in the morning", f("NM:B")),
    ("Time & side", "Worse at night", f("SI:B CP:AB")),
    ("Time & side", "Comes at set times / periodical", f("NM:AB")),
    ("Time & side", "Right-sided complaints", f("MP:B")),
    ("Time & side", "Worse at full moon", f("SI:B")),

    # 9. Mind & mood
    ("Mind & mood", "Nervous exhaustion, brain-fag, poor memory", f("KP:AB SI:B NM:B")),
    ("Mind & mood", "Anxious, fearful, weepy, homesick, suspicious, shy", f("KP:AB")),
    ("Mind & mood", "Depressed; groundless fear of money troubles; indecisive", f("CF:B")),
    ("Mind & mood", "Peevish, fretful (children); after grief or disappointment", f("CP:B")),
    ("Mind & mood", "Trifles seem like mountains; indifferent", f("FP:B")),
    ("Mind & mood", "Imagines he must starve", f("KM:B")),
    ("Mind & mood", "Fear of falling; sad, anxious", f("KS:AB")),
    ("Mind & mood", "Forgetful, dull; complains constantly about the pain", f("MP:B")),
    ("Mind & mood", "Hopeless, sad, weepy; worse from consolation", f("NM:AB")),
    ("Mind & mood", "Apprehensive; irritable over trifles", f("NP:B")),
    ("Mind & mood", "Low, irritable from 'biliousness'; worse from sad music", f("NS:B")),
    ("Mind & mood", "Can't concentrate, tires easily, oversensitive", f("SI:B")),
    ("Mind & mood", "Changeable mood", f("CS:B KP:B")),

    # 10. Constitution / general picture
    ("General picture", "Watery, puffy face; tired, sleepy, chilly; craves salt", f("NM:AB")),
    ("General picture", "Pale, sensitive, irritable, easily exhausted", f("KP:AB")),
    ("General picture", "Thin, anaemic, slow growth; craves salty/smoked meats", f("CP:AB")),
    ("General picture", "Flushed, florid face", f("FP:B")),
    ("General picture", "Lean, nervous, tired, can't sit up; craves sugar", f("MP:B")),
    ("General picture", "Feels the damp; sallow / jaundiced; bilious", f("NS:AB")),
    ("General picture", "Chilly, poorly nourished, sweaty head, offensive foot-sweat", f("SI:AB")),
    ("General picture", "Relaxed, sagging tissues", f("CF:AB")),
    ("General picture", "Sour smell / sour symptoms everywhere", f("NP:AB")),
    ("General picture", "Thirst for cold water", f("FP:B")),
    ("General picture", "Craves fruit, sour green vegetables", f("CS:B")),

    # 11. Digestion
    ("Digestion", "Vomits undigested food", f("FP:AB")),
    ("Digestion", "Vomits bile; bitter taste", f("NS:AB")),
    ("Digestion", "Vomits clear water or stringy mucus; water-brash", f("NM:AB")),
    ("Digestion", "Retches up white mucus", f("KM:AB")),
    ("Digestion", "Sour burps, heartburn, sour or curdled vomit", f("NP:AB")),
    ("Digestion", "Cramping colic, better with heat & bending double; burping no relief", f("MP:AB")),
    ("Digestion", "Pressure / fullness in stomach with yellow tongue", f("KS:AB")),
    ("Digestion", "Flatulent colic with constipation", f("NS:AB")),
    ("Digestion", "Nervous 'gone' feeling; stomach ache from fright", f("KP:B")),
    ("Digestion", "Stomach pain eased by eating / colic each time child feeds", f("CP:B")),
    ("Digestion", "Indigestion after fatty food", f("KM:B NP:AB")),

    # 12. Stool
    ("Stool", "Watery, mucous diarrhoea", f("NM:AB")),
    ("Stool", "Carrion-smelling, putrid", f("KP:AB SI:B")),
    ("Stool", "Watery-bilious, green", f("NS:AB")),
    ("Stool", "Bloody-mucous; or pale, clay-coloured", f("KM:AB")),
    ("Stool", "Sour-smelling, green", f("NP:AB")),
    ("Stool", "Undigested", f("FP:AB")),
    ("Stool", "Watery, with cramping colic before each stool", f("MP:AB")),
    ("Stool", "Purulent", f("NP:A SI:A CS:B")),
    ("Stool", "Dry, hard, crumbling constipation", f("NM:B")),
    ("Stool", "Stool slips back after partly expelled", f("SI:B")),
    ("Stool", "Green, slimy, hot, sputtering; worse fruit", f("CP:B")),

    # 13. Skin: blisters by contents
    ("Skin: blisters", "Clear, watery contents", f("NM:AB")),
    ("Skin: blisters", "Thick white (fibrinous) contents", f("KM:AB")),
    ("Skin: blisters", "Albuminous contents", f("CP:A")),
    ("Skin: blisters", "Honey-yellow contents", f("NP:AB")),
    ("Skin: blisters", "Yellowish-watery contents", f("NS:AB")),
    ("Skin: blisters", "Pus-like contents", f("NP:A SI:A")),
    ("Skin: blisters", "Bloody, foul contents", f("KP:AB")),

    # 14. Skin: crusts & scales
    ("Skin: crusts", "Mealy, flour-like scurf", f("KM:AB")),
    ("Skin: crusts", "Yellowish-white crusts", f("CP:AB")),
    ("Skin: crusts", "White scales", f("NM:AB")),
    ("Skin: crusts", "Honey-yellow crusts", f("NP:AB")),
    ("Skin: crusts", "Yellowish scales", f("NS:AB")),
    ("Skin: crusts", "Yellow, purulent crusts", f("SI:A CS:B")),
    ("Skin: crusts", "Greasy, foul-smelling crusts", f("KP:AB")),
    ("Skin: crusts", "Profuse peeling on a sticky base", f("KS:AB")),
    ("Skin: crusts", "Hard skin on palms with cracks", f("CF:AB")),

    # 15. Skin: other
    ("Skin: other", "Cracks, chaps, fissures", f("CF:AB")),
    ("Skin: other", "Itching", f("MP:A CP:B KP:B")),
    ("Skin: other", "Hives / nettle-rash", f("KP:A NM:B")),
    ("Skin: other", "Boils, abscesses", f("SI:AB CS:B")),
    ("Skin: other", "Brittle nails, white spots, ingrowing nails", f("SI:AB")),
    ("Skin: other", "Warts", f("KM:AB NS:AB NM:B")),
    ("Skin: other", "Burns that blister", f("NM:A KM:AB")),
    ("Skin: other", "Insect stings", f("NM:AB")),
    ("Skin: other", "Chilblains", f("NS:A KM:B KP:B SI:B CS:B")),
    ("Skin: other", "Hair loss / bald patches", f("KP:AB NM:AB KS:B SI:B")),
    ("Skin: other", "Dandruff", f("KM:B KS:B NM:B MP:B")),

    # 16. Bleeding
    ("Bleeding", "Bright red, clots easily", f("FP:AB")),
    ("Bleeding", "Dark, thick, sticky, clotted", f("KM:AB")),
    ("Bleeding", "Thin, watery, does not clot", f("KP:AB NM:AB")),
    ("Bleeding", "Nosebleeds in children", f("FP:AB")),

    # 17. Fever
    ("Fever", "Start of any fever; chilly stage; quick pulse", f("FP:AB")),
    ("Fever", "Exhausted, stuporous fever; dry brown tongue", f("KP:AB")),
    ("Fever", "Drowsy fever with watery vomiting", f("NM:AB")),
    ("Fever", "Recurring (intermittent) fever", f("NS:AB NM:AB")),
    ("Fever", "Temperature rises in the evening; helps sweating", f("KS:B")),
    ("Fever", "Fever while pus is forming (hectic)", f("CS:B SI:B")),
    ("Fever", "Influenza", f("NS:AB")),

    # 18. Nerves, spasms, sleep
    ("Nerves & sleep", "Cramps, spasms, hiccough, writer's cramp", f("MP:AB")),
    ("Nerves & sleep", "Convulsions with fever (teething)", f("FP:AB")),
    ("Nerves & sleep", "Spasms in anaemic, weak children", f("CP:AB")),
    ("Nerves & sleep", "Weakness, paralysis, nervous collapse", f("KP:AB")),
    ("Nerves & sleep", "Numbness, pins & needles", f("CP:AB NM:B")),
    ("Nerves & sleep", "Sleepless from worry or excitement", f("KP:B")),
    ("Nerves & sleep", "Sleepy, unrefreshed on waking", f("NM:AB")),
    ("Nerves & sleep", "Attacks at night", f("SI:AB")),

    # 19. Structure: bones, teeth, veins, glands
    ("Structure", "Slow bone growth, fractures slow to knit, late teeth, open fontanelles", f("CP:AB")),
    ("Structure", "Hard knobby bone growths; stony-hard lumps", f("CF:AB")),
    ("Structure", "Loose teeth, rough enamel", f("CF:AB")),
    ("Structure", "Varicose veins, piles, sagging / prolapse", f("CF:AB")),
    ("Structure", "Bone inflammation tending to pus", f("SI:AB")),
    ("Structure", "Glands swollen, soft", f("KM:B NP:AB")),
    ("Structure", "Glands swollen, stony hard", f("CF:AB")),
    ("Structure", "Glands suppurating", f("SI:AB CS:B")),
    ("Structure", "Joint / gout pains from uric acid", f("NP:AB SI:AB NS:B")),
    ("Structure", "Fluid in joints / sacs (e.g. knee)", f("CP:AB SI:AB NM:A")),
]


# Browse areas for the finder's starting pick. A feature can sit in several
# areas so the doctor finds it wherever they look first. Areas only affect
# browsing: each feature is still one row and is scored once.
AREA_ORDER = [
    "Inflammation & pus", "Discharge & mucus", "Fever", "Pain",
    "Digestion & appetite", "Stool & bowels", "Mouth, tongue & teeth", "Skin",
    "Bones, joints & muscles", "Veins & glands", "Bleeding", "Nerves & sleep",
    "Mind & mood", "General picture", "Children", "Worse from", "Better from",
    "Time & side",
]

GROUP_AREA = {  # home area of each feature group
    "Inflammation stage": "Inflammation & pus",
    "Discharge": "Discharge & mucus",
    "Tongue": "Mouth, tongue & teeth",
    "Pain type": "Pain",
    "Worse from": "Worse from",
    "Better from": "Better from",
    "Time & side": "Time & side",
    "Mind & mood": "Mind & mood",
    "General picture": "General picture",
    "Digestion": "Digestion & appetite",
    "Stool": "Stool & bowels",
    "Skin: blisters": "Skin",
    "Skin: crusts": "Skin",
    "Skin: other": "Skin",
    "Bleeding": "Bleeding",
    "Fever": "Fever",
    "Nerves & sleep": "Nerves & sleep",
    "Structure": "Bones, joints & muscles",
}

EXTRA_AREAS = {  # feature -> additional areas it is also listed under
    # bowels belong to digestion too, and the other way round
    "Watery, mucous diarrhoea": ["Digestion & appetite"],
    "Carrion-smelling, putrid": ["Digestion & appetite"],
    "Watery-bilious, green": ["Digestion & appetite"],
    "Bloody-mucous; or pale, clay-coloured": ["Digestion & appetite"],
    "Sour-smelling, green": ["Digestion & appetite", "Children"],
    "Undigested": ["Digestion & appetite"],
    "Watery, with cramping colic before each stool": ["Digestion & appetite", "Pain"],
    "Purulent": ["Digestion & appetite", "Inflammation & pus"],
    "Dry, hard, crumbling constipation": ["Digestion & appetite"],
    "Stool slips back after partly expelled": ["Digestion & appetite"],
    "Green, slimy, hot, sputtering; worse fruit": ["Digestion & appetite", "Children"],
    "Flatulent colic with constipation": ["Stool & bowels", "Pain"],
    "Cramping colic, better with heat & bending double; burping no relief": ["Stool & bowels", "Pain"],
    "Stomach pain eased by eating / colic each time child feeds": ["Pain", "Children"],
    "Nervous 'gone' feeling; stomach ache from fright": ["Mind & mood"],
    "Pain with vomiting of bile": ["Digestion & appetite"],
    "Fatty or rich food, pastry": ["Digestion & appetite"],
    "Indigestion after fatty food": ["Worse from"],
    # appetite, thirst and cravings
    "Watery, puffy face; tired, sleepy, chilly; craves salt": ["Digestion & appetite"],
    "Thin, anaemic, slow growth; craves salty/smoked meats": ["Digestion & appetite", "Children"],
    "Lean, nervous, tired, can't sit up; craves sugar": ["Digestion & appetite"],
    "Thirst for cold water": ["Digestion & appetite"],
    "Craves fruit, sour green vegetables": ["Digestion & appetite"],
    "Sour smell / sour symptoms everywhere": ["Digestion & appetite"],
    # tongue findings a doctor reads alongside the stomach
    "Clean tongue with stomach cramps": ["Digestion & appetite"],
    "Dirty brownish-green / greyish-green, bitter taste": ["Digestion & appetite"],
    "Yellow, slimy coating": ["Digestion & appetite"],
    "Moist, creamy, golden-yellow coating at the back": ["Digestion & appetite"],
    "Loose teeth, rough enamel": ["Mouth, tongue & teeth"],
    # pus and boils
    "Boils, abscesses": ["Inflammation & pus"],
    "Glands suppurating": ["Inflammation & pus", "Veins & glands"],
    "Pus forming; abscess needs to ripen / come to a head": ["Skin"],
    "Pus with an outlet; discharge goes on too long, slow to heal": ["Skin"],
    "Thick yellow pus": ["Inflammation & pus"],
    "Thick, yellow, lumpy (Calc Sulph: may be blood-tinged)": ["Inflammation & pus"],
    "Foul, fetid, carrion-like smell": ["Inflammation & pus"],
    "Discharge turns foul / septic / gangrenous": ["Discharge & mucus"],
    "Pus-like contents": ["Inflammation & pus"],
    "Yellow, purulent crusts": ["Inflammation & pus"],
    "Bone inflammation tending to pus": ["Inflammation & pus"],
    # fever and colds
    "1st stage: redness, heat, throbbing, fever onset, no discharge yet": ["Fever"],
    "Start of any fever; chilly stage; quick pulse": ["Inflammation & pus"],
    "Influenza": ["Discharge & mucus"],
    "Fever while pus is forming (hectic)": ["Inflammation & pus"],
    # pain, muscles, joints
    "Cramps, spasms, hiccough, writer's cramp": ["Pain", "Bones, joints & muscles"],
    "Shooting, lightning-like, boring, cramping, constricting; changes place": ["Nerves & sleep"],
    "Joint / gout pains from uric acid": ["Pain"],
    "Pain with numbness, coldness or crawling (ants) sensation": ["Nerves & sleep"],
    "Numbness, pins & needles": ["Pain"],
    "Dragging, bearing-down pain (relaxed tissues)": ["Veins & glands"],
    "Motion": ["Pain"],
    "Rest, rising from sitting, beginning to move, exertion": ["Pain"],
    "Pressure, bending double, rubbing": ["Pain"],
    # veins and glands
    "Varicose veins, piles, sagging / prolapse": ["Veins & glands", "Stool & bowels"],
    "Glands swollen, soft": ["Veins & glands"],
    "Glands swollen, stony hard": ["Veins & glands"],
    "Relaxed, sagging tissues": ["Veins & glands"],
    # mind and nerves
    "Nervous exhaustion, brain-fag, poor memory": ["Nerves & sleep"],
    "Sleepless from worry or excitement": ["Mind & mood"],
    "Pale, sensitive, irritable, easily exhausted": ["Mind & mood"],
    # children
    "Convulsions with fever (teething)": ["Children", "Fever"],
    "Spasms in anaemic, weak children": ["Children"],
    "Nosebleeds in children": ["Children"],
    "Slow bone growth, fractures slow to knit, late teeth, open fontanelles": ["Children", "Mouth, tongue & teeth"],
    "Peevish, fretful (children); after grief or disappointment": ["Children"],
}


def areas_of(group, feature):
    if group not in GROUP_AREA:  # Tissue affinity: not something to pick or ask
        return []
    return [GROUP_AREA[group]] + [a for a in EXTRA_AREAS.get(feature, []) if a != GROUP_AREA[group]]


def check_areas():
    names = {feat for _, feat, _ in FEATURES}
    unknown = [k for k in EXTRA_AREAS if k not in names]
    assert not unknown, f"EXTRA_AREAS lists unknown features: {unknown}"
    used = {a for g, feat, _ in FEATURES for a in areas_of(g, feat)}
    assert used == set(AREA_ORDER), f"area mismatch: {used ^ set(AREA_ORDER)}"


def label(src):
    return {"A": "A only", "B": "B only", "AB": "A+B"}[src]


def main():
    # Long format: one row per feature x salt
    with open("features_long.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["group", "feature", "salt_no", "salt", "source"])
        for g, feat, m in FEATURES:
            for k, no, short, _ in SALTS:
                if k in m:
                    w.writerow([g, feat, no, short, label(m[k])])

    # Wide matrix: one row per feature, one column per salt
    head = [f"{no}. {short}" for _, no, short, _ in SALTS]
    with open("features_matrix.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["group", "feature"] + head)
        for g, feat, m in FEATURES:
            w.writerow([g, feat] + [m.get(k, "") for k in KEYS])

    write_html(head)
    write_js()
    per_salt = {k: sum(k in m for _, _, m in FEATURES) for k in KEYS}
    print(len(FEATURES), "features;", sum(per_salt.values()), "salt links")
    print(per_salt)


def write_js():
    """features.js: the same data for the browser finder (loads over file:// too)."""
    check_areas()
    data = {
        "salts": [{"key": k, "no": no, "name": short, "latin": full} for k, no, short, full in SALTS],
        "areas": AREA_ORDER,
        "features": [{"group": g, "feature": feat, "salts": m, "areas": areas_of(g, feat)}
                     for g, feat, m in FEATURES],
    }
    with open("features.js", "w") as fh:
        fh.write("// Generated by build_features.py, do not edit by hand.\n")
        fh.write("var SALT_DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")
        fh.write("if (typeof module !== 'undefined') module.exports = SALT_DATA;\n")


def write_html(head):
    rows, last = [], None
    for g, feat, m in FEATURES:
        if g != last:
            rows.append(f'<tr class="grp"><th colspan="{len(KEYS)+1}">{html.escape(g)}</th></tr>')
            last = g
        cells = "".join(
            f'<td class="s{m[k]}">{m[k]}</td>' if k in m else "<td></td>" for k in KEYS
        )
        rows.append(f"<tr><td class='feat'>{html.escape(feat)}</td>{cells}</tr>")
    ths = "".join(f"<th class='salt'><span>{html.escape(h)}</span></th>" for h in head)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tissue Salt Features</title>
<style>
:root{{--bg:#f6f1e7;--ink:#1f2a24;--muted:#6b7068;--line:#e3dccd;--a:#c9822b;--b:#4a7fa8;--ab:#2f6b4f}}
@media (prefers-color-scheme:dark){{:root{{--bg:#16191a;--ink:#e8e6e1;--muted:#9a9d97;--line:#2c3130}}}}
body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.4 system-ui,sans-serif;padding:16px}}
h1{{font-size:20px;margin:0 0 4px}} p{{color:var(--muted);margin:0 0 12px;max-width:70ch}}
.key span{{display:inline-block;padding:1px 8px;border-radius:6px;color:#fff;margin-right:6px;font-weight:600}}
.wrap{{overflow:auto;max-height:80vh;border:1px solid var(--line);border-radius:10px}}
table{{border-collapse:collapse;min-width:900px}}
th,td{{border-bottom:1px solid var(--line);padding:4px 6px;text-align:center}}
thead th{{position:sticky;top:0;background:var(--bg);z-index:2;vertical-align:bottom}}
th.salt span{{writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap}}
td.feat{{text-align:left;min-width:320px;position:sticky;left:0;background:var(--bg)}}
tr.grp th{{text-align:left;background:var(--line);position:sticky;left:0}}
td.sA,td.sB,td.sAB{{color:#fff;font-weight:600;font-size:12px}}
.sA{{background:var(--a)}} .sB{{background:var(--b)}} .sAB{{background:var(--ab)}}
</style></head><body>
<h1>Tissue Salt Feature Set (A ∪ B)</h1>
<p>A = Schüssler, <i>An Abridged Therapy</i> (25th ed.). B = Boericke &amp; Dewey, <i>The Twelve Tissue Remedies</i>.
{len(FEATURES)} features across 12 salts. Traditional reference only, not medical advice.</p>
<p class="key"><span class="sAB">AB</span>in both books <span class="sA">A</span>Schüssler only <span class="sB">B</span>Boericke only</p>
<div class="wrap"><table><thead><tr><th>Feature</th>{ths}</tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
</body></html>"""
    with open("features_matrix.html", "w") as fh:
        fh.write(page)


if __name__ == "__main__":
    main()
