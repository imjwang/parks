import base64
import os

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_chroma import Chroma
from tqdm import tqdm
from langchain.globals import set_verbose
set_verbose(True)
# from PIL import Image


# def verify_and_delete_non_jpeg(directory):
#     for root, dirs, files in os.walk(directory):
#         for file in files:
#             file_path = os.path.join(root, file)
#             try:
#                 with Image.open(file_path) as img:
#                     if img.format != 'JPEG':
#                         print(f"{file_path} is not a valid JPEG, deleting...")
#                         os.remove(file_path)
#             except (IOError, SyntaxError) as e:
#                 print(f"{file_path} is not a valid image, deleting...")
#                 os.remove(file_path)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_file_names_in_directory(directory_path):
    try:
        # List all entries in the directory
        entries = os.listdir(directory_path)
        # Filter out only files (not directories)
        file_names = [entry for entry in entries if os.path.isfile(
            os.path.join(directory_path, entry))]
        return file_names
    except FileNotFoundError:
        print(f"Error: The directory '{directory_path}' does not exist.")
        return []
    except PermissionError:
        print(f"Error: Permission denied to access '{directory_path}'.")
        return []


def create_image_message(image_data):
    messages = [
        SystemMessage(content="Your task is to generate text to describe the image. The text is used to create image embeddings. ONLY generate text that is semantically useful. The user WILL NOT see the message so keep the message 'CUT AND DRY'."),
        HumanMessage(content=[
            {
                "type": "text", "text": f"""\
Please describe the following image with AS MUCH DETAIL AS POSSIBLE.
Things to include are:
 - SKY, including cloud formations.
 - LANDSCAPE, including any mountains, hills, or valleys.
 - BODIES OF WATER, such as rivers, lakes, or oceans.
 - PLANTLIFE noting any particularity in the flora.
 - WILDLIFE, including animals or insects.
 - Detailed SENTIMENT ANALYSIS of any users IF PRESENT.
Generate an analysis of the image.
"""
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
            }
        ])
    ]
    return messages


def main():
    # Specify the directory to check
    # directory = 'imges/data'
    # verify_and_delete_non_jpeg(directory)
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small", dimensions=1024)
    llm = ChatOpenAI(
        model="gpt-4o"
    )
    db = Chroma("images_with_meta", embeddings, persist_directory="chroma")
    data_folder = 'imgs/data'
    data_files = get_file_names_in_directory(data_folder)
    image_data = [encode_image(f"imgs/data/{fn}") for fn in data_files]
    inputs = [create_image_message(img_data) for img_data in image_data]
    results = llm.batch(inputs, return_exceptions=True)
    valid_results = [r if not isinstance(
        r, Exception) else "" for r in results]
    print(valid_results)
    contents = []
    metadatas = []
    for res, location in zip(valid_results, data_files):
        if res == "":
            continue
        contents.append(res.content)
        metadatas.append({"location": location[:-7]})

    db.add_texts(contents, metadatas=metadatas)
    return


if __name__ == "__main__":
    main()
