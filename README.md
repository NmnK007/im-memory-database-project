# im-memory-database-project

A dict with some validation around it basically is an in-memory database — this felt very interesting.
The whole read-input → do something → print result → loop pattern (REPL) is reusable for basically any CLI tool, not just this one.
Keeping the data (the class) separate from the interface made the whole thing less confusing to reason about, since I could think about "what does SET actually do" without also thinking about "how does this get printed."
Raising exceptions and catching them is a different way of handling errors than just checking if key in dict everywhere — took me a bit to get comfortable with try/except actually catching something.
time.time() just gives you one number that keeps going up — seconds since a fixed point in the past. TTL is really just comparing that number to a stored future version of itself. Nothing more magical than that.
Checking argument counts before using them (len(rest) < 2 type checks) is what stops typing SET with nothing after it from just crashing the whole program.

Parsing input (tokenize){yeh wala part mujhe kafi interesting and intutive feel hua tha, similar hamne sih ke model me bhi dekha tha}

Before doing anything with what you typed, it gets split into words and checked that it isn't empty. This is its own function instead of being mixed into each command, so all the "did the user type something reasonable" logic lives in one spot.

Commands{used in project}
SET <key> <value> — stores something. e.g. SET username alex morgan. Overwrites if the key's already there. You don't need quotes for multi-word values, it just takes everything after the key as the value.
GET <key> — gives you back the value, or tells you the key doesn't exist instead of crashing.
DEL <key> — deletes a key.
EXISTS <key> — just says yes or no.
SETEX <key> <seconds> <value> — same as SET but the key disappears on its own after however many seconds you give it.
TTL <key> — tells you how many seconds are left before a key expires (or -1 if it has no expiry at all).
SAVE <filename> — dumps everything currently stored into a file.
LOAD <filename> — reads that file back in.
QUIT — exits.

The class (NmnQL) --> It holds two dictionaries:

self.data — the actual key → value pairs
self.expiry — key → the exact timestamp it should expire at (only keys set with SETEX show up here at all)

Instead of returning None when a key's missing, get_value/remove_key raise a KeyError. The command loop catches that with try/except and turns it into a normal-looking error message. I like this better than checking if key in database everywhere because the "is something wrong" logic lives in one place instead of being copy-pasted into every command.

TTL / expiration

When you SETEX something, it records time.time() + seconds — basically "the exact clock reading when this key should die." Nothing is running in the background counting down — instead, every time a key gets touched (GET, DEL, EXISTS, TTL), it first checks "has the clock already passed that stored timestamp?" and deletes the key right then if so. I learned this is called lazy expiration — the key doesn't vanish the instant it expires, it vanishes the next time someone actually looks for it.

saving and loading - one line per key, written as key and value separated by a tab character. I used a tab specifically because values can have spaces in them, so splitting on spaces would've broken things. to_lines() turns the dict into text lines, load_lines() turns text lines back into a dict, and save_to_file() / load_from_file() are the only two spots that actually open a file.


now i want to write about what i did other than this project in these last 3-4 days
firstly i cleared my misconception about git and github
then did few basic linux cmds (still not great at it but i have learned the most imp ones)
created 2-3 projects using numpy(nothing major, just for a deeper understanding)
watched the full ml specializtion course by ng andrew
learned more on forensics and web exploitations

this project taught me a lot more about python in general that how i could make something so unique with it, though i used ai for help (i wont eny that) but i tried writting the whole code by myself and understanding it... hoepfully will learn a lot more in future through such projects!!!