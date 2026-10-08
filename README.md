# Tissue Salt Finder

An interactive finder for the 12 Schüssler tissue salts. You pick one feature that is present, then answer
**Have this / Don't have this / I don't know** questions until the closest matching salts emerge.

**Live page:** `https://<your-username>.github.io/<repo-name>/`

> **Not medical advice.** This is a traditional biochemic reference made for education and entertainment.
> It says nothing about potency, dosage or repetition. Ask a qualified practitioner, and see a doctor for
> anything serious.

## How it works

1. **Starting pick.** Choose an area (e.g. *Digestion & appetite*), then one feature you are sure of
   (e.g. *Flatulent colic with constipation*). This counts as the first "yes".
2. **Follow-up questions.** Each question is one feature. The next question is always the one with the
   highest expected information gain over the current salt scores.
3. **Scoring.** Every salt keeps a score (a Bayesian update):
   - **Have this:** salts with the feature go up.
   - **Don't have this:** salts with the feature go down, but are never ruled out.
   - **I don't know:** nothing changes.
   - Features found in **both** source books count more than features from one book.
4. **Stopping.** The finder stops when one salt reaches 90%, or after 20 answered questions (the starting
   pick included). Every "I don't know" adds one more allowed question.
5. **Result.** It shows the top salts whose scores together cover at least 67%.

All of these settings are at the top of [`engine.js`](engine.js).

## Sources

The feature set is the union (A ∪ B) of two public-domain books:

- **A:** W. H. Schüssler, *An Abridged Therapy: Manual for the Biochemical Treatment of Disease*,
  25th ed., tr. L. H. Tafel (Boericke & Tafel, 1898).
- **B:** W. Boericke & W. A. Dewey, *The Twelve Tissue Remedies of Schüssler* (Boericke & Tafel).

Every link between a feature and a salt is tagged **A**, **B** or **A+B**. Some notes on the data:

- Schüssler's final edition drops **Calcarea sulphurica**, so it appears only through Book B.
- Where Book B contradicts itself and Book A is silent, the feature is left out. This applies to Calc Fluor
  and temperature, Kali Phos and cold, and Kali Phos's "2–5" time.
- The set covers each salt's characteristic features, not every symptom in the books.

## Files

| File | What it is |
|---|---|
| `index.html` | The finder page (9:16 layout for screen recording) |
| `engine.js` | Scoring and question selection; runs in the browser and in Node |
| `features.js` | The feature data for the page (generated) |
| `build_features.py` | The source of truth: all 188 features, their sources and browse areas |
| `features_matrix.html` | Colour-coded table of features × salts |
| `features_matrix.csv`, `features_long.csv` | The same data for spreadsheets |

## Editing the data

Edit `build_features.py`, then regenerate everything:

```bash
python3 build_features.py
```

No dependencies: Python 3 standard library only, and plain HTML, CSS and JavaScript with no build step.
`index.html` also works when opened straight from disk.

## Keyboard shortcuts

`1` / `Y` have this · `2` / `N` don't have this · `3` / `I` don't know · `H` hide controls for recording

## License

[MIT](LICENSE)
