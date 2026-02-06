import hashlib
import itertools

def generate_case_variations(text):
    """Generate all case variations of a string (e.g. 'ab' -> 'ab', 'aB', 'Ab', 'AB')"""
    if not text:
        return [text]
    variations = []
    for i in range(2 ** len(text)):
        variant = ""
        for j, char in enumerate(text):
            if (i >> j) & 1:
                variant += char.upper()
            else:
                variant += char.lower()
        variations.append(variant)
    return variations

target_hash = "8a8c48b5907be12e019177693b3b0300"
base_terms = "2241112"
dict="abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-_"

def find_matching_hash():
    """Generate all combinations of strings around base_terms and find MD5 hash match"""
    
    for left_len in range(9):
        for right_len in range(5):
            # Generate all combinations for left part
            for left in itertools.product(dict, repeat=left_len):
                left_str = ''.join(left)
                # Generate all combinations for right part
                for right in itertools.product(dict, repeat=right_len):
                    right_str = ''.join(right)
                    candidate = left_str + base_terms + right_str
                    
                    md5_hash = hashlib.md5(candidate.encode()).hexdigest()
                    
                    if md5_hash == target_hash:
                        print(f"Found match: {candidate} -> {md5_hash}")
                        return candidate
            
            print(f"Checked left={left_len}, right={right_len}")
    
    print("No match found")

find_matching_hash()

