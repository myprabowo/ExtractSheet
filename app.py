# app2.py

from shiny import App, render, ui, reactive
from shiny.ui import tags
import pandas as pd
import pikepdf
import os
import re
import tempfile
from typing import List, Dict
from shiny.types import FileInfo

# --- DEFINE extract_form_data and sort_key HERE ---
def extract_form_data(pdf_path: str) -> Dict:
    try:
        with pikepdf.open(pdf_path) as pdf:
            form_data = {}
            if pdf.Root.AcroForm is not None and pdf.Root.AcroForm.Fields is not None:
                for field in pdf.Root.AcroForm.Fields:
                    field_name = str(field.T)
                    field_value = None
                    if hasattr(field, 'V'):
                        value_obj = field.V
                        if isinstance(value_obj, pikepdf.objects.Name):
                            field_value = str(value_obj)[1:]
                        else:
                            field_value = value_obj
                    form_data[field_name] = field_value
            return form_data
    except pikepdf.PdfError as e:
        print(f"Error processing {pdf_path}: {e}")
    except FileNotFoundError:
        print(f"Error: File not found at {pdf_path}")
    return {}

def sort_key(field_name: str) -> tuple:
    match = re.match(r"([a-zA-Z\s]+)_(\d+)", field_name)
    if match:
        section = match.group(1)
        number = int(match.group(2))
        return (section, number)
    return (field_name, float('inf'))

def process_uploaded_pdfs(uploaded_files: List[FileInfo]) -> List[Dict]:
    all_results = []
    if uploaded_files:
        for file_info in uploaded_files:
            filename = file_info['name']
            filepath = file_info['datapath']  # Temporary path on the server
            print(f"Processing uploaded file: {filename}")
            form_data = extract_form_data(filepath)
            if form_data:
                form_data['filename'] = filename
                all_results.append(form_data)
            else:
                print(f"No form data extracted from {filename}")
    return all_results

# --- Shiny App UI ---
app_ui = ui.page_fluid(
    ui.h2("PDF Answer Sheet Reader"),
    ui.input_file("pdf_files", "Upload Answer Sheet PDFs", multiple=True, accept=".pdf"),
    ui.output_ui("results_table"),
    ui.download_button("download_csv", "Download CSV"),

    # Footer
    tags.hr(),
    tags.footer(
        "Creator: Muhammad Yoga Prabowo",
        style=(
            "text-align: center; "
            "padding: 10px; "
            "margin-top: 30px; "
            "font-size: 14px; "
            "color: #6c757d; "
            "background-color: #f8f9fa;"
        )
    )
)

# --- Shiny App Server ---
def server(input, output, session):
    # Reactive value to cache the processed DataFrame
    @reactive.calc
    def extracted_df():
        uploaded_files = input.pdf_files()
        if uploaded_files:
            extracted_data_list = process_uploaded_pdfs(uploaded_files)
            if extracted_data_list:
                df = pd.DataFrame(extracted_data_list)
                # Put filename first if present
                if 'filename' in df.columns:
                    cols = ['filename'] + [col for col in df.columns if col != 'filename']
                    df = df[cols]
                # Sort columns by your sort_key
                sorted_cols = sorted(df.columns, key=sort_key)
                return df[sorted_cols]
        return pd.DataFrame()

    @output
    @render.ui
    def results_table():
        df = extracted_df()
        if not df.empty:
            return ui.output_data_frame("extracted_table")
        else:
            return ui.tags.p("Please upload PDF answer sheet files.")

    @output
    @render.data_frame
    def extracted_table():
        return extracted_df()

    # ---- FIXED DOWNLOAD: yield the CSV content ----
    @render.download(filename="extracted_data.csv")
    def download_csv():
        df = extracted_df()
        # Yield the CSV text; Shiny will treat this as file content
        yield df.to_csv(index=False)

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
