import os
import tkinter as tk
from tkinter import filedialog, messagebox
import chess.pgn


def select_files():
    # Open file dialog to select multiple PGN files
    file_paths = filedialog.askopenfilenames(filetypes=[("PGN files", "*.pgn")])
    if file_paths:
        # Call the process function with selected files
        process_files(file_paths)


def process_files(file_paths):
    try:
        for file_path in file_paths:
            # Get the output file name by appending "(sorted)" to the original file name
            folder, original_name = os.path.split(file_path)
            output_file = os.path.join(folder, f"{os.path.splitext(original_name)[0]} (sorted).pgn")

            # Process the single file with the merge logic
            merge_pgn_file(file_path, output_file)

        messagebox.showinfo("Success", "Files have been merged and saved with '(sorted)' added to the names.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def merge_pgn_file(input_file, output_file):
    standard_games = {}
    non_standard_games = []

    # Process the PGN file
    with open(input_file, "r", encoding="utf-8") as file:
        while True:
            try:
                game = chess.pgn.read_game(file)
                if game is None:
                    break

                # Check if FEN is standard or not
                fen = game.headers.get("FEN", "startpos")
                if fen == "startpos":
                    tag = f"{game.headers['White']} vs {game.headers['Black']} ({game.headers.get('Event', 'Unknown')})"
                    if tag not in standard_games:
                        standard_games[tag] = []
                    standard_games[tag].append(game)
                else:
                    non_standard_games.append(game)
            except Exception as e:
                print(f"Error reading game in {input_file}: {str(e)}")

    # Write the merged PGN to the output file
    with open(output_file, "w", encoding="utf-8") as outfile:
        for tag, games in standard_games.items():
            merged_game = merge_games_into_tree(games)
            outfile.write(str(merged_game) + "\n\n")

        for game in non_standard_games:
            outfile.write(str(game) + "\n\n")


def merge_games_into_tree(games):
    root_game = games[0]
    current_node = root_game

    for game in games[1:]:
        moves = game.mainline_moves()
        for move in moves:
            current_node = current_node.add_variation(move)

    return root_game


# GUI Setup
root = tk.Tk()
root.title("PGN File Merger")

tk.Label(root, text="Select PGN Files to Merge").pack(pady=10)
tk.Button(root, text="Upload Files", command=select_files).pack(pady=20)

root.mainloop()
