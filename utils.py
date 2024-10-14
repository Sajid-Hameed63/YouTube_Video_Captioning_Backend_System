import pandas as pd

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def save_to_excel(results, output_file):
    df = pd.DataFrame(results)
    df.to_excel(output_file, index=False)
    print(f"Results saved to '{output_file}'.")
