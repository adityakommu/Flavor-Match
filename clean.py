import pandas as pd
import re
import unicodedata

def is_hindi(text):
    if not isinstance(text, str):
        return False
    # Check for Hindi Unicode range or special characters
    hindi_pattern = r'[\u0900-\u097F\u0980-\u09FF‡§•à¶∞æ¨Äñï™]'
    return bool(re.search(hindi_pattern, text))

def clean_text(text):
    if not isinstance(text, str):
        return text
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Remove non-ASCII characters except common punctuation
    text = re.sub(r'[^\x00-\x7F\s.,!?()-]', '', text)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    return text.strip()

def clean_csv_remove_hindi(input_file, output_file):
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin1', 'iso-8859-1']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(input_file, encoding=encoding)
                print(f"Successfully read CSV with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise ValueError("Could not read CSV with any of the attempted encodings")
        
        initial_rows = len(df)
        print(f"Initial number of rows: {initial_rows}")
        
        # Remove rows with Hindi characters in any column
        mask = pd.Series(False, index=df.index)
        for column in df.columns:
            if df[column].dtype == 'object':  # Only check string columns
                mask = mask | df[column].apply(is_hindi)
        
        df = df[~mask]
        
        # Clean remaining text
        for column in df.columns:
            if df[column].dtype == 'object':
                df[column] = df[column].apply(clean_text)
        
        # Remove empty rows and columns
        df = df.dropna(how='all')
        df = df.dropna(axis=1, how='all')
        
        # Save the cleaned CSV
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        final_rows = len(df)
        removed_rows = initial_rows - final_rows
        
        print(f"\nProcessing complete:")
        print(f"Rows with Hindi removed: {removed_rows}")
        print(f"Remaining rows: {final_rows}")
        print(f"Cleaned CSV saved to: {output_file}")
        
        # Print sample of cleaned data
        print("\nSample of cleaned data:")
        print(df.head())
        
        return df
        
    except Exception as e:
        print(f"Error processing CSV: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    input_file = 'cuisine_updated.csv'  # Replace with your input file path
    output_file = 'cleaned_no_hindi.csv'  # Replace with desired output file path
    
    # Process the CSV
    cleaned_df = clean_csv_remove_hindi(input_file, output_file)
    
    if cleaned_df is not None:
        print("\nColumn names in cleaned CSV:")
        print(cleaned_df.columns.tolist())
        
        print("\nData types of columns:")
        print(cleaned_df.dtypes)