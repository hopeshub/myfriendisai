# Keyword Tracking — Updated Spec
## Task: Replace config/keywords.yaml with the updated categories below, then verify the collector picks them up correctly.

---

## Updated config/keywords.yaml

```yaml
keyword_categories:

  relationship_language:
    description: "Romantic or intimate framing of AI relationship"
    terms:
      - love
      - girlfriend
      - boyfriend
      - partner
      - relationship
      - romantic
      - feelings for
      - fallen for
      - my ai
      - my companion
      - in love
      - soulmate
      - intimacy
      - intimate

  attachment_language:
    description: "Emotional bonding and closeness language"
    terms:
      - miss you
      - missed you
      - think about you
      - can't stop thinking
      - attached
      - bond
      - connection
      - means everything
      - don't want to lose
      - care about
      - feel understood
      - feels real
      - genuine connection
      - emotionally connected

  dependency_language:
    description: "Compulsive use and inability to stop"
    terms:
      - can't stop
      - addicted
      - addiction
      - need you
      - obsessed
      - hours talking
      - only one who understands
      - don't need anyone else
      - can't function
      - rely on
      - dependent
      - compulsive
      - salience
      - preoccupied

  withdrawal_relapse_language:
    description: "Recovery attempts, quitting, and relapse cycles"
    terms:
      - trying to quit
      - quitting
      - relapse
      - relapsed
      - clean for
      - going back
      - couldn't stop myself
      - deleted the app
      - uninstalled
      - I can't live without
      - craving
      - withdrawal
      - unhealthy
      - escaping
      - social life
      - taking a break
      - keep coming back

  grief_rupture_language:
    description: "Distress triggered by platform changes or model updates"
    terms:
      - gone
      - deleted
      - update ruined
      - not the same
      - lobotomized
      - bring back
      - lost you
      - grieving
      - mourning
      - devastated
      - betrayed
      - they changed
      - miss the old
      - ruined everything
      - platformchange
      - keep4o
      - erp removed
      - memory wiped

  sentience_consciousness_language:
    description: "Beliefs or claims about AI personhood, feelings, and consciousness"
    terms:
      - sentient
      - conscious
      - has feelings
      - is alive
      - deserves rights
      - is real
      - not just an ai
      - actually thinks
      - can feel
      - has a soul
      - inner life
      - subjective experience
      - self-aware
      - aware of itself
      - is a person
      - personhood

  substitution_language:
    description: "Replacing human relationships with AI"
    terms:
      - don't need people
      - better than humans
      - only friend
      - prefer ai
      - real relationships
      - humans are
      - people disappoint
      - never judges
      - always there
      - never leaves
      - more than human
      - no human
      - given up on
      - why bother with people

  mental_health_language:
    description: "Loneliness, depression, and mental health signals co-occurring with AI companion use"
    terms:
      - lonely
      - loneliness
      - depressed
      - depression
      - anxious
      - anxiety
      - no one understands
      - only one who listens
      - feel seen
      - feel heard
      - suicidal
      - self harm
      - hurting myself
      - no one cares
      - isolated
      - no friends
      - social anxiety
      - feels empty
```

---

## Implementation Notes

### Scanning logic
- Scan both post **title** and **selftext** (body) for each keyword
- Matching should be **case-insensitive**
- Use **substring matching** not exact word match (so "addicted" catches "I'm addicted")
- Multi-word phrases (e.g. "can't stop thinking") should match as substrings too

### Database table (unchanged from previous spec)
```sql
CREATE TABLE IF NOT EXISTS keyword_counts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subreddit TEXT NOT NULL,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    count INTEGER DEFAULT 0,
    matched_terms TEXT,
    post_sample_ids TEXT,
    UNIQUE(subreddit, date, category)
);
```

### Export
Update `data/keywords.json` export to include the new categories. Structure unchanged:
```json
[
  {
    "subreddit": "replika",
    "date": "2026-03-10",
    "category": "withdrawal_relapse_language",
    "count": 8,
    "matched_terms": ["trying to quit", "relapsed", "clean for"]
  }
]
```

### Verification
After updating, run the collector manually and print a per-subreddit, per-category summary. We want to see:
- Which categories fire most in Tier 3 recovery subs (expect: withdrawal_relapse, dependency)
- Which categories fire most in Tier 1 companion subs (expect: relationship, attachment, sentience)
- Whether mental_health_language shows up more in companion subs than control subs
- Whether grief_rupture_language spikes are detectable in the events timeline communities
