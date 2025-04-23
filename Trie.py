import pandas as pd


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

    
class Trie:
    def __init__(self):
        self.root = TrieNode()  # Root node of the tree


    def create_dict(self, file_path="word_list_common.csv"):
        """Construct a trie from a file containing a list of words.

        Args:
            file_path (string): 
        """
        with open(file_path, 'r') as f:
            for word in f:
                self.insert(word.strip())
    
    def insert(self, word: str):
        """Insert a word into the trie.
        
        Args:
            word: The word to insert into the trie.
        """
        node = self.root
        for letter in word:
            if letter not in node.children:
                node.children[letter] = TrieNode()
            node = node.children[letter]
        node.is_end_of_word = True  # <-- Mark word ending



    def prune(
        self,
        green: list[tuple[str, int]],
        yellow: list[tuple[str, int]],
        grey: set[str]
    ) -> None:
        """
        Prunes the Trie to remove words that do not match the Wordle constraints.

        Args:
            green (list[tuple[str, int]]): 
                A list of (letter, position) pairs representing letters that must appear 
                at the exact position in the word (correct letter, correct spot).
            
            yellow (list[tuple[str, int]]): 
                A list of (letter, position) pairs representing letters that must be included 
                in the word but not at the specified position (correct letter, wrong spot).
            
            grey (set[str]): 
                Letters that are not in the word at all *unless* they also appear in green/yellow.
                In that case, the letter must appear **exactly** as many times as specified.

        Returns:
            None. Modifies the Trie in-place by removing branches that violate the constraints.
        """

        green_map = {pos: char for char, pos in green}  # Map positions to green letters
        yellow_map = {}
        yellow_count = {}  # Count appearances of yellow letters

        for char, pos in yellow:
            yellow_map.setdefault(char, set()).add(pos)
            yellow_count[char] = yellow_count.get(char, 0) + 1

        green_count = {}
        for char, pos in green:
            green_count[char] = green_count.get(char, 0) + 1

        # Total required occurrences per letter (from green + yellow)
        required_count = {}
        for char in set(green_count) | set(yellow_count):
            required_count[char] = green_count.get(char, 0) + yellow_count.get(char, 0)

        def dfs(node, prefix, depth):
            # Only validate complete words (length 5)
            if depth == 5:
                # Count how many times each letter appears in this word
                from collections import Counter
                word_count = Counter(prefix)

                # Check each green letter is in the correct position
                for pos, char in green_map.items():
                    if prefix[pos] != char:
                        return None

                # Check each yellow letter is present but not in forbidden positions
                for char, positions in yellow_map.items():
                    if char not in prefix:
                        return None
                    for pos in positions:
                        if prefix[pos] == char:
                            return None

                # If the letter also appears in green/yellow, enforce exact count
                # Otherwise, it must not appear at all
                for char in grey:
                    if char in required_count:
                        if word_count[char] != required_count[char]:
                            return None
                    else:
                        if char in prefix:
                            return None

                # If all checks pass, this word is valid
                node.is_end_of_word = True
                return node

            # Recursively prune children
            new_children = {}
            for char, child in node.children.items():
                # Green constraint: must match the required letter at that depth
                if depth in green_map and char != green_map[depth]:
                    continue

                # Yellow constraint: cannot appear in known bad positions
                if char in yellow_map and depth in yellow_map[char]:
                    continue

                pruned_child = dfs(child, prefix + char, depth + 1)
                if pruned_child:
                    new_children[char] = pruned_child

            node.children = new_children

            # Keep node if it has valid children or is a valid word
            if node.children or node.is_end_of_word:
                return node
            return None

        # Start DFS from root and prune invalid branches
        self.root = dfs(self.root, "", 0) or TrieNode()



    def display(self, node=None, prefix="", depth=0):
        """Recursively print the tree structure."""

        # Use root on first call
        if node is None:
            node = self.root

        if depth == 5:
            print(prefix)

        for letter, child in node.children.items():
            self.display(child, prefix + letter, depth + 1)

    def probability_matrix(self) -> pd.DataFrame:
        """
        Generates a 26x5 DataFrame representing the probability of each letter (a-z)
        appearing in each position (0-4) across all valid 5-letter words in the Trie.

        Returns:
            pd.DataFrame: A DataFrame where each row corresponds to a letter (a-z),
            and each column corresponds to a position in the word (0-4). The values
            represent the percentage of times that letter appears in that position
            over the total number of valid words.
        """
        # create array of letters a-z
        letters = [chr(i) for i in range(ord('a'), ord('z') + 1)]

        df = pd.DataFrame(0, index=letters, columns=range(5))  # Initialize with zeros
        total_words = 0

        # Recursive function to traverse the Trie and count letter occurrences
        def dfs(node, word):
            nonlocal total_words

            # Add letters to the DataFrame if it's a complete word
            if node.is_end_of_word and len(word) == 5:
                total_words += 1
                for i, char in enumerate(word):
                    if char in df.index:
                        df.at[char, i] += 1
            
            # Traverse children
            for char, child in node.children.items():
                dfs(child, word + char)

        dfs(self.root, "")

        if total_words > 0:
            df = df.div(total_words)

        return df

    def find_nextBest_word(self) -> str:
        """
        Find the next best word to try based on the current Trie state.

        Args:
            word (str): The word to check against the Trie.

        Returns:
            str: The next best word to try.
        """
        best = ""
        best_score = 0
        prob_matrix = self.probability_matrix()

        # Recursive function to traverse the Trie and count letter occurrences
        def dfs(node, word):
            nonlocal best, best_score

            # Add letters to the DataFrame if it's a complete word
            if node.is_end_of_word and len(word) == 5:
                score = 0

                # add probability of each letter in the word to score
                for i, char in enumerate(word):
                    score += prob_matrix.at[char, i]
                
                # Update best word if score is higher
                if score > best_score:
                    # print(f"New best word: {word} with score {score}")
                    best = word
                    best_score = score
            
            # Traverse children
            for char, child in node.children.items():
                dfs(child, word + char)

        dfs(self.root, "")

        return best
