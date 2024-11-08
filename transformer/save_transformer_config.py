#!/cws/anaconda/envs/mlenv/bin/python -W ignore

import argparse
import csv
import logging

def main(csv_data, file_name, delimiter, header_comments):
    """
    Write to CSV file with optional header comments.
    csv_data is a list of lists.
    header_comments is a string with each comment separated by newline.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        with open(file_name, 'w', newline='') as file:
            if header_comments:
                # Write header comments as they are
                for comment in header_comments.split('\n'):
                    file.write(f"{comment}\n")
            
            writer = csv.writer(file, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
            for row in csv_data:
                # Strip any surrounding whitespace or newlines from each cell
                cleaned_row = [cell.strip() for cell in row if cell]
                writer.writerow(cleaned_row)
    except Exception as e:
        logging.error(f"Failed to write to file: {e}")
        print(f"Failure &#10060;")        
        return

    logging.info(f"Success saving to: {file_name}")
    print(f"Success &#9989;")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Write CSV data to a file with optional header comments.')
    parser.add_argument('--csv_data', required=True, help='CSV data as a string with rows separated by "\\n" and columns separated by the specified delimiter')
    parser.add_argument('--file_name', required=True, help='Name of the file to write the CSV data to')
    parser.add_argument('--delimiter', default=',', help='Delimiter to separate columns in the CSV file')
    parser.add_argument('--header_comments', default='', help='Header comments to add to the file, each separated by "\\n"')

    args = parser.parse_args()
    csv_data = [row.split(args.delimiter) for row in args.csv_data.strip().split("\n") if row]
    main(csv_data, args.file_name, args.delimiter, args.header_comments)
