# Sample Book Data CSV

This directory contains CSV files for importing book data.

## Expected CSV Format

Your CSV file should have the following columns:

- `category_name`: The name of the book category (e.g., "Fiction", "Science")
- `category_label`: A short label for the category (e.g., "FIC", "SCI")
- `book_name`: The title of the book
- `location`: The storage location (e.g., "Shelf A1")

## Example

```csv
category_name,category_label,book_name,location
Fiction,FIC,The Great Gatsby,Shelf A1
Science,SCI,A Brief History of Time,Shelf C1
History,HIST,Sapiens,Shelf D1
```

## Usage

Place your CSV file in this directory and run:

```bash
docker-compose exec etl python csv_loader/load_books.py --file /data/your_file.csv
```
