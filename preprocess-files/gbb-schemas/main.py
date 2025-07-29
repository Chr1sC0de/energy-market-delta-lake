import pathlib as pt

from PyPDF2 import PdfReader


def main():
    document_path = (
        pt.Path(__file__).parent / "guide-to-gas-bulletin-board-reports-v23.pdf"
    )
    reader = PdfReader(document_path.as_posix())

    output_file = pt.Path("output.txt")
    if not output_file.exists():
        output_file.unlink(missing_ok=True)
        for page in reader.pages:
            text = page.extract_text()
            with output_file.open("a") as f:
                _ = f.write(text)

    return


if __name__ == "__main__":
    main()
