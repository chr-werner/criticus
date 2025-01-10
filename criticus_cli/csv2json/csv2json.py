import argparse
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor
from to_json import *

# Helper function to process each tuple
def process_tuple(tuple, verses_df, output_dir):
    ga = tuple[0]
    nkv = tuple[1]

    # Filter verses_df based on the tuple
    verse_df = verses_df[(verses_df['ga'] == ga) & (verses_df['nkv'] == nkv)]

    # Initialize list for witnesses' data
    witnesses_dict_list = []
    for _, row in verse_df.iterrows():
        lection = row["lection"]  # Handle None value appropriately
        witness = row["witness"]
        text = row["text"]
        
        # Create witness dictionary
        witness_dict = {"id": f"{ga}-{lection}-{witness}", "tokens": words_to_tokens(text.split(), f"{ga}-{witness}")}
        witnesses_dict_list.append(witness_dict)

    # Create the transcription dictionary
    transcription = dictify_transcription(siglum=ga, ref=nkv, plain_tx="", witnesses=witnesses_dict_list)

    # Define the file path for output
    file_path = f"{output_dir}/{ga}-{nkv}.json"

    # Write JSON to file
    with open(file_path, "w") as file:
        json.dump(transcription, file, indent=4)

# Create a ThreadPoolExecutor to process tuples in parallel
def process_in_parallel(tuple_list, verses_df, output_dir, threads):
    with ThreadPoolExecutor(max_workers=threads) as executor:
        # Submit tasks to the executor for each tuple in the tuple_list
        futures = [executor.submit(process_tuple, tup, verses_df, output_dir) for tup in tuple_list]
        
        # Optionally, wait for all futures to complete
        for future in futures:
            future.result()  # This ensures that any exceptions are raised

def main():
    # Argument parser to handle input parameters
    parser = argparse.ArgumentParser(description="Process verses and export JSON files.")
    parser.add_argument('input_file', type=str, help="Path to the input CSV file containing verses")
    parser.add_argument('output_dir', type=str, help="Directory where the JSON files will be saved")
    parser.add_argument('--threads', type=int, default=0, help="Number of threads to use for parallel processing")

    # Parse the arguments
    args = parser.parse_args()

    # Read the input CSV file
    verses_df = pd.read_csv(args.input_file, low_memory=True)

    # TODO: remove when verses.csv is up to date
    verses_df["witness"] = "testing"

    # Get necessary columns only
    verses_df = verses_df[["ga", "lection", "nkv", "witness", "text", "source"]]

    # Get all unique "ga and nkv" variants
    ga_nkv_df = verses_df[["ga", "nkv"]]
    ga_nkv_df.drop_duplicates(inplace=True, ignore_index=True)

    # Write to tuple list for parallel processing
    tuple_list = ga_nkv_df.to_records(index=False).tolist()

    # Run the parallel processing function
    process_in_parallel(tuple_list, verses_df, args.output_dir, args.threads)

if __name__ == '__main__':
    main()
