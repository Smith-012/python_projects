import sys

def count_char_occurrences(sentence: str, ch: str) -> int:
    """Count total occurrences of ch in sentence (case-insensitive)."""
    ch = ch[:1]  # only first character if user pasted more
    return sentence.lower().count(ch.lower())

def prompt_enter_or_esc() -> bool:
    """
    Ask user to press Enter (continue) or Esc (quit).
    Returns True to continue, False to quit.
    Re-prompts on any other key.
    """
    print("\nPress Enter to run again, or Esc to quit... ", end="", flush=True)

    # Windows: use msvcrt to capture single key presses
    try:
        import msvcrt
        while True:
            key = msvcrt.getch()
            # Enter can be '\r' (carriage return); on some terminals msvcrt returns b'\r'
            if key in (b"\r", b"\n"):
                print()  # newline after prompt
                return True
            # Esc is 0x1B
            if key == b"\x1b":
                print()  # newline after prompt
                return False
            # For special keys msvcrt returns a prefix (b'\x00' or b'\xe0'), consume the next byte
            if key in (b"\x00", b"\xe0"):
                msvcrt.getch()  # discard second byte
            else:
                print("\nPlease press Enter to continue or Esc to quit.")
                print("Press Enter to run again, or Esc to quit... ", end="", flush=True)
    except ImportError:
        # Non-Windows fallback: ask user to type and press Enter
        while True:
            typed = input().strip().lower()
            if typed == "":
                return True
            if typed in ("esc", "quit", "q"):
                return False
            print("Please type Enter (blank) to continue or 'esc' to quit:")

def app_once():
    sentence = input("Enter a sentence: ").strip()
    while True:
        char = input("Enter the alphabet/character to count (single character): ").strip()
        if len(char) >= 1:
            char = char[0]  # take only first character
            break
        print("Please enter at least one character.")

    count = count_char_occurrences(sentence, char)

    if count == 0:
        print(f"\n❌ The character '{char}' was NOT found in the sentence.")
    else:
        print(f"\n✅ The character '{char}' appears {count} time(s) in the sentence.")

def main():
    print("=== Character Occurrence Counter (case-insensitive) ===")
    while True:
        app_once()
        if not prompt_enter_or_esc():
            print("Goodbye!")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExited.")
        sys.exit(0)
