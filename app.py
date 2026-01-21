from shiny import App, render, ui, reactive
from shiny.ui import tags
import pandas as pd
import pikepdf
import re
from typing import List, Dict, Tuple
from shiny.types import FileInfo

# --- FUNGSI EKSTRAKSI DATA ---
def extract_form_data(pdf_path: str) -> Dict:
    try:
        with pikepdf.open(pdf_path) as pdf:
            form_data = {}
            # Cek ketersediaan AcroForm
            if pdf.Root.AcroForm is not None and pdf.Root.AcroForm.Fields is not None:
                for field in pdf.Root.AcroForm.Fields:
                    field_name = str(field.T)
                    field_value = ""
                    
                    if hasattr(field, 'V'):
                        value_obj = field.V
                        # KRUSIAL: Paksa semua tipe data pikepdf menjadi string
                        # Ini mencegah ValueError di Shiny lokal
                        if isinstance(value_obj, pikepdf.objects.Name):
                            field_value = str(value_obj)[1:]
                        else:
                            field_value = str(value_obj)
                            
                    form_data[field_name] = field_value
            return form_data
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
    return {}

def sort_key(field_name: str) -> tuple:
    match = re.match(r"([a-zA-Z\s]+)_(\d+)", field_name)
    if match:
        section = match.group(1)
        number = int(match.group(2))
        return (section, number)
    return (field_name, float('inf'))

# --- FUNGSI PEMROSESAN (DENGAN LIST FILE GAGAL) ---
def process_uploaded_pdfs(uploaded_files: List[FileInfo]) -> Tuple[List[Dict], List[str]]:
    all_results = []
    failed_files = []
    
    if uploaded_files:
        for file_info in uploaded_files:
            filename = file_info['name']
            filepath = file_info['datapath']
            
            form_data = extract_form_data(filepath)
            
            if form_data:
                form_data['filename'] = filename
                all_results.append(form_data)
            else:
                # Masuk ke daftar file yang kemungkinan flattened
                failed_files.append(filename)
                
    return all_results, failed_files

# --- Shiny App UI ---
app_ui = ui.page_fluid(
    ui.h2("PDF Answer Sheet Reader"),
    ui.input_file("pdf_files", "Upload Answer Sheet PDFs", multiple=True, accept=".pdf"),
    
    # Area untuk menampilkan daftar file yang gagal (Flattened)
    ui.output_ui("failed_files_alert"),
    
    ui.output_ui("results_table"),
    ui.download_button("download_csv", "Download CSV Hasil"),

    # Footer
    tags.hr(),
    tags.footer(
        "Creator: Muhammad Yoga Prabowo",
        style=(
            "text-align: center; padding: 10px; margin-top: 30px; "
            "font-size: 14px; color: #6c757d; background-color: #f8f9fa;"
        )
    )
)

# --- Shiny App Server ---
def server(input, output, session):
    
    @reactive.calc
    def processed_data():
        uploaded_files = input.pdf_files()
        if not uploaded_files:
            return [], []
        return process_uploaded_pdfs(uploaded_files)

    @output
    @render.ui
    def failed_files_alert():
        _, failed = processed_data()
        if failed:
            items = [ui.tags.li(f) for f in failed]
            return ui.div(
                ui.tags.strong("⚠️ File Tidak Terbaca (Kemungkinan Flattened):"),
                ui.tags.ul(*items),
                style="color: #856404; background-color: #fff3cd; border: 1px solid #ffeeba; padding: 10px; border-radius: 5px; margin-bottom: 15px;"
            )
        return None

    @reactive.calc
    def extracted_df():
        data, _ = processed_data()
        if data:
            df = pd.DataFrame(data)
            # Pastikan filename di depan
            if 'filename' in df.columns:
                cols = ['filename'] + [col for col in df.columns if col != 'filename']
                df = df[cols]
            # Sorting kolom
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

    @render.download(filename="extracted_data.csv")
    def download_csv():
        df = extracted_df()
        yield df.to_csv(index=False)

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
