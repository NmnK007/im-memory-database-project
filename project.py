import time
 
 
class NmnQL:
    
 
    def __init__(self):
        self.data = {}
        self.expiry = {}  
 
    def _drop_if_expired(self, key):
        
        if key in self.expiry and time.time() >= self.expiry[key]:
            self.data.pop(key, None)
            self.expiry.pop(key, None)
 
    def set_value(self, key, value):
        self.data[key] = value
        self.expiry.pop(key, None)  
 
    def set_with_expiry(self, key, value, seconds):
        self.data[key] = value
        self.expiry[key] = time.time() + float(seconds)
 
    def time_left(self, key):
        
        self._drop_if_expired(key)
        if key not in self.data:
            return None
        if key not in self.expiry:
            return -1
        return round(self.expiry[key] - time.time(), 1)
 
    def get_value(self, key):
        self._drop_if_expired(key)
        if key not in self.data:
            raise KeyError(key)
        return self.data[key]
 
    def remove_key(self, key):
        self._drop_if_expired(key)
        if key not in self.data:
            raise KeyError(key)
        del self.data[key]
        self.expiry.pop(key, None)
 
    def has_key(self, key):
        self._drop_if_expired(key)
        return key in self.data
 
    def to_lines(self):
        """Serial karega every entry ko as one line: key<TAB>value. Used by save()."""
        lines = []
        for key, value in self.data.items():
            lines.append(f"{key}\t{value}")
        return lines
 
    def load_lines(self, lines):
        """Rebuild self.data from lines produced by to_lines(). Replaces current data."""
        rebuilt = {}
        for raw_line in lines:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            if "\t" not in line:
                continue  # skip any corrupted/unreadable line instead of crashing
            key, value = line.split("\t", 1)
            rebuilt[key] = value
        self.data = rebuilt
 
    def save_to_file(self, filename):
        with open(filename, "w") as f:
            for line in self.to_lines():
                f.write(line + "\n")
 
    def load_from_file(self, filename):
        with open(filename, "r") as f:
            self.load_lines(f.readlines())
 
 
def tokenize(raw_line):
    """
    Split a typed line into tokens, with validation baked in.
 
    Returns (tokens, error_message). error_message is None when parsing
    succeeded. This keeps all the "is this input well-formed?" logic in
    one place instead of scattered across every command branch.
    """
    stripped = raw_line.strip()
    if stripped == "":
        return None, "No command entered."
 
    tokens = stripped.split()
 
    if len(tokens) == 0:
        return None, "No command entered."
 
    return tokens, None
 
 
def run_shell():
    store = NmnQL()
    print("NmnQL ready. Commands: SET GET DEL EXISTS SETEX TTL SAVE LOAD QUIT")
 
    while True:
        raw_line = input("> ")
 
        tokens, error = tokenize(raw_line)
        if error:
            print(f"[!] {error}")
            continue
 
        action = tokens[0].upper()
        rest = tokens[1:]
 
        # ---- SET: needs exactly a key and a value ----
        if action == "SET":
            if len(rest) < 2:
                print("[!] SET needs a key and a value, e.g.: SET username alex")
                continue
            key = rest[0]
            value = " ".join(rest[1:])  # allow multi-word values without needing quotes
            store.set_value(key, value)
            print(f"[ok] stored '{key}'")
 
        # ---- GET: needs exactly a key, must exist ----
        elif action == "GET":
            if len(rest) != 1:
                print("[!] GET needs exactly one key, e.g.: GET username")
                continue
            try:
                print(store.get_value(rest[0]))
            except KeyError:
                print(f"[!] no such key: '{rest[0]}'")
 
        # ---- DEL: needs exactly a key, must exist ----
        elif action == "DEL":
            if len(rest) != 1:
                print("[!] DEL needs exactly one key, e.g.: DEL username")
                continue
            try:
                store.remove_key(rest[0])
                print(f"[ok] removed '{rest[0]}'")
            except KeyError:
                print(f"[!] no such key: '{rest[0]}'")
 
        # ---- SETEX: like SET, but the key auto-expires after N seconds ----
        elif action == "SETEX":
            if len(rest) < 3:
                print("[!] SETEX needs a key, seconds, and a value, e.g.: SETEX temp 10 hello")
                continue
            key = rest[0]
            seconds_text = rest[1]
            value = " ".join(rest[2:])
            try:
                seconds = float(seconds_text)
            except ValueError:
                print(f"[!] seconds must be a number, got '{seconds_text}'")
                continue
            store.set_with_expiry(key, value, seconds)
            print(f"[ok] stored '{key}' (expires in {seconds}s)")
 
        # ---- TTL: how many seconds until a key expires ----
        elif action == "TTL":
            if len(rest) != 1:
                print("[!] TTL needs exactly one key, e.g.: TTL temp")
                continue
            result = store.time_left(rest[0])
            if result is None:
                print(f"[!] no such key: '{rest[0]}'")
            elif result == -1:
                print("no expiry set")
            else:
                print(f"{result}s left")
 
        # ---- EXISTS: needs exactly a key ----
        elif action == "EXISTS":
            if len(rest) != 1:
                print("[!] EXISTS needs exactly one key, e.g.: EXISTS username")
                continue
            print("yes" if store.has_key(rest[0]) else "no")
 
        # ---- SAVE: dump everything to a file ----
        elif action == "SAVE":
            if len(rest) != 1:
                print("[!] SAVE needs a filename, e.g.: SAVE backup.txt")
                continue
            try:
                store.save_to_file(rest[0])
                print(f"[ok] saved to '{rest[0]}'")
            except OSError as e:
                print(f"[!] could not write file: {e}")
 
        # ---- LOAD: replace current data with what's in a file ----
        elif action == "LOAD":
            if len(rest) != 1:
                print("[!] LOAD needs a filename, e.g.: LOAD backup.txt")
                continue
            try:
                store.load_from_file(rest[0])
                print(f"[ok] loaded from '{rest[0]}'")
            except FileNotFoundError:
                print(f"[!] file not found: '{rest[0]}'")
 
        elif action == "QUIT":
            break
 
        else:
            print(f"[!] unknown command: '{action}'")
 
 
if __name__ == "__main__":
    run_shell()