import glob
import os

from dotenv import load_dotenv
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

root_directory = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

markdown_files_path = os.path.join(
    root_directory, "scripts/load_pdf_to_vector_db/papers_markdown"
)
markdown_files = glob.glob(os.path.join(markdown_files_path, "**/*.md"))
headers_to_split_on = [
    ("#", "header1"),
    ("##", "header2"),
    ("###", "header3"),
    ("####", "header4"),
]

text_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on, strip_headers=False
)
doc_splits = []

for markdown_file in markdown_files:
    print(f"[INFO] Processing markdown file: {markdown_file}")
    file_name = markdown_file.split("/")[-1]
    parts = file_name.split(" - ", 2)

    author = parts[0]
    year = parts[1]
    title = parts[2].replace(".md", "") if len(parts) == 3 else ""
    extra_metadata = {
        "file_name": file_name,
        "title": title,
        "author": author,
        "year": int(year),
    }
    with open(markdown_file, "r", encoding="utf-8") as file:
        file_content = file.read()
        for doc in text_splitter.split_text(file_content):
            doc.page_content = (
                f"Title: {title}\nAuthor: {author}\nYear: {year}\n\n{doc.page_content}"
            )
            doc.metadata.update(extra_metadata)
            doc_splits.append(doc)
    #         print(doc)
    #         print("*" * 100)

    # break


persist_directory = os.path.join(root_directory, ".chroma")

vectorstore = Chroma.from_documents(
    documents=doc_splits,
    collection_name="papers",
    embedding=OpenAIEmbeddings(model="text-embedding-3-large"),
    persist_directory=persist_directory,
)
