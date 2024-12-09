import os
import chess.pgn

def group_games(folder_path):
    """Groups games into standard and non-standard starting positions."""
    standard_games = {}  # For standard FEN games (mergeable)
    non_standard_games = []  # For games with custom FENs (intact)

    # Read all PGN files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".pgn"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                while True:
                    try:
                        game = chess.pgn.read_game(file)
                        if game is None:
                            break
                        # Check the starting FEN (default is standard position)
                        starting_fen = game.headers.get("FEN", "startpos")
                        if starting_fen == "startpos" or starting_fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1":
                            # Group by a chapter identifier (e.g., 'White' or 'Event')
                            chapter_name = game.headers.get("White", "Unknown").split()[0]  # Customize as needed
                            if chapter_name not in standard_games:
                                standard_games[chapter_name] = []
                            standard_games[chapter_name].append(game)
                        else:
                            # Add to non-standard games if FEN is different
                            non_standard_games.append(game)
                    except Exception as e:
                        print(f"Error reading game in {filename}: {e}")
                        continue
    return standard_games, non_standard_games

def merge_games_into_tree(games):
    """Merges multiple games into a single PGN tree with variations."""
    if not games:
        return None

    # Use the first game as the root
    root_game = games[0]
    root_node = root_game

    # Add moves from subsequent games as variations
    for game in games[1:]:
        current_node = root_node
        for move in game.mainline_moves():
            # Add the move as a variation if it doesn't already exist
            existing_variation = next((child for child in current_node.variations if child.move == move), None)
            if existing_variation:
                current_node = existing_variation
            else:
                current_node = current_node.add_variation(move)

    return root_game

def create_chaptered_pgn(output_file, standard_games, non_standard_games):
    """Creates a single PGN file with merged chapters and unaltered non-standard games."""
    with open(output_file, "w", encoding="utf-8") as outfile:
        # Write merged chapters for standard games
        for chapter_name, games in standard_games.items():
            merged_game = merge_games_into_tree(games)
            if merged_game:
                # Set the chapter name in the header
                merged_game.headers["Event"] = chapter_name
                outfile.write(str(merged_game) + "\n\n")
        
        # Write non-standard games intact
        for game in non_standard_games:
            outfile.write(str(game) + "\n\n")
    print(f"Final merged PGN saved as {output_file}")

if __name__ == "__main__":
    folder_path = input("Enter the folder path containing PGN files: ")
    output_file = input("Enter the output file name (e.g., final_merged.pgn): ")
    standard_games, non_standard_games = group_games(folder_path)
    create_chaptered_pgn(output_file, standard_games, non_standard_games)
    print("PGN chapters and unmerged games have been successfully compiled!")
